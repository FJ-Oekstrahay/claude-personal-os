#!/usr/bin/env python3
"""
Shared outbound helper for the Discord notify hooks.

Centralizes four cross-cutting concerns so discord-notify.sh,
discord-text-extract.py, and discord-stop-check.py all behave identically:

  1. post_with_retry()   — bounded retry/backoff curl POST (webhook OR bot-API).
  2. dedup guard         — time-windowed (session, channel, content-hash) ring;
                           suppresses identical text re-posted within WINDOW secs.
                           This is the safety net that makes the 4x duplication
                           impossible even if a root-cause path is missed.
  3. coalescing buffer   — per (session, log-channel) append buffer flushed as a
                           single POST once it is >COALESCE_MAX_AGE old, exceeds
                           COALESCE_MAX_CHARS, or is force-flushed at Stop.
  4. outbound audit log  — one JSON line per POST attempt to outbound-audit.log
                           (O_APPEND single write, size-capped) for later forensics.

Design invariants:
  * Never block Claude. This module is only ever called from processes the shell
    hook already backgrounded, so retry sleeps add no latency to the tool call.
  * Fail OPEN. Any internal error here must never raise into the caller; a lost
    Discord mirror is annoying, a crashed hook is worse.
  * Side-effect-safe under concurrency. financial + health sessions run these
    hooks simultaneously and share state/. All shared-file writes are append-only
    single writes (O_APPEND) or atomic replace; no read-modify-write on a shared
    file without a per-file lock.

State dir + dry-run are env-overridable so the offline test harness never touches
the live state dir or POSTs to a real webhook:
  DISCORD_HOOK_STATE_DIR  — override ~/.claude/hooks/state
  DISCORD_DRYRUN=1         — write intended POSTs to $DISCORD_DRYRUN_FILE instead
                             of curling (default /tmp/discord-dryrun.log)
  DISCORD_COALESCE=0       — disable coalescing (post each line immediately)
"""
import hashlib
import json
import os
import subprocess
import sys
import time

# ---------------------------------------------------------------- config knobs
DEDUP_WINDOW_SECS = int(os.environ.get('DISCORD_DEDUP_WINDOW', '20'))
DEDUP_RING = 40                      # hashes retained per (session, channel)
COALESCE_MAX_AGE = float(os.environ.get('DISCORD_COALESCE_AGE', '2.0'))
COALESCE_MAX_CHARS = 1600            # flush before Discord's 2000-char body cap
AUDIT_CAP_BYTES = 5 * 1024 * 1024    # rotate outbound-audit.log past 5 MB
DISCORD_BODY_CAP = 1900


def _state_dir():
    d = os.environ.get('DISCORD_HOOK_STATE_DIR') or os.path.expanduser('~/.claude/hooks/state')
    try:
        os.makedirs(d, exist_ok=True)
    except Exception:
        pass
    return d


def _err_log():
    return os.path.join(_state_dir(), 'hook-errors.log')


def _log_error(msg):
    try:
        with open(_err_log(), 'a') as f:
            f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] discord_outbound: {msg}\n")
    except Exception:
        pass


def content_hash(text):
    try:
        return hashlib.sha1(text.encode('utf-8', 'replace')).hexdigest()[:12]
    except Exception:
        return '0' * 12


# ------------------------------------------------------------------- audit log
def audit(session, event, channel, target, status, http_code, text):
    """Append one JSON line describing a POST attempt. Single O_APPEND write so
    concurrent sessions never interleave a partial record."""
    try:
        path = os.path.join(_state_dir(), 'outbound-audit.log')
        # Size-check-then-append: cheap, tolerant of slight overshoot under a
        # concurrent write (a racing truncate would be worse — see module docs).
        try:
            if os.path.exists(path) and os.path.getsize(path) > AUDIT_CAP_BYTES:
                os.replace(path, path + '.1')
        except Exception:
            pass
        rec = {
            'ts': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
            'session': (session or '')[:12],
            'event': event,
            'channel': str(channel or ''),
            'target': target,            # 'log' | 'discussion' | 'alert'
            'status': status,            # 'sent' | 'dedup' | 'dropped' | 'buffered'
            'http': str(http_code or ''),
            'hash': content_hash(text or ''),
            'text': (text or '').replace('\n', ' ')[:60],
        }
        line = json.dumps(rec, ensure_ascii=False) + '\n'
        # O_APPEND guarantees the whole line lands atomically for reasonable sizes.
        fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o644)
        try:
            os.write(fd, line.encode('utf-8', 'replace'))
        finally:
            os.close(fd)
    except Exception:
        pass


# ----------------------------------------------------------------- dedup guard
def _dedup_path(session, channel):
    safe = f'{session}__{channel}'.replace('/', '_')
    return os.path.join(_state_dir(), f'{safe}.dedup.json')


def is_duplicate(session, channel, text):
    """Return True if (session, channel, hash(text)) was posted within
    DEDUP_WINDOW_SECS. Records the hash+timestamp either way. Time-windowed so
    legitimately-identical posts in *different* turns (e.g. the done-ping) still
    fire — only rapid re-fires / concurrent duplicates are suppressed."""
    try:
        h = content_hash(text)
        now = time.time()
        path = _dedup_path(session, channel)
        ring = []
        if os.path.exists(path):
            try:
                ring = json.load(open(path))
            except Exception:
                ring = []
        dup = any(e.get('h') == h and (now - e.get('t', 0)) < DEDUP_WINDOW_SECS for e in ring)
        # prune stale + cap ring, then append current
        ring = [e for e in ring if (now - e.get('t', 0)) < DEDUP_WINDOW_SECS][-DEDUP_RING:]
        ring.append({'h': h, 't': now})
        tmp = path + '.tmp'
        with open(tmp, 'w') as f:
            json.dump(ring, f)
        os.replace(tmp, path)   # atomic; last writer wins, acceptable for a hint
        return dup
    except Exception:
        return False            # fail open: never suppress on error


# --------------------------------------------------------------------- posting
def _dryrun_post(url, payload, auth_header):
    try:
        out = os.environ.get('DISCORD_DRYRUN_FILE', '/tmp/discord-dryrun.log')
        with open(out, 'a') as f:
            f.write(json.dumps({'url': url[:70], 'auth': bool(auth_header),
                                'payload': payload[:400]}) + '\n')
    except Exception:
        pass
    return '204'


def _curl(url, payload, auth_header, timeout=8):
    if os.environ.get('DISCORD_DRYRUN') == '1':
        return _dryrun_post(url, payload, auth_header)
    args = ['/usr/bin/curl', '-s', '-o', '/dev/null', '-w', '%{http_code}',
            '--max-time', str(timeout), '-X', 'POST', url,
            '-H', 'Content-Type: application/json']
    if auth_header:
        args += ['-H', auth_header]
    args += ['-d', payload]
    try:
        cp = subprocess.run(args, capture_output=True, text=True,
                            check=False, timeout=timeout + 4)
        return (cp.stdout or '').strip()
    except Exception:
        return None


def post_with_retry(url, payload, auth_header=None, attempts=3):
    """Bounded retry curl POST. Returns the final HTTP code string (or None)."""
    code = None
    for i in range(attempts):
        code = _curl(url, payload, auth_header)
        if code and code.isdigit() and 200 <= int(code) < 300:
            return code
        if code == '429':
            time.sleep(2 + (i % 2))
        else:
            time.sleep(1 + i)
    return code


def send(session, event, channel, target, url, text, auth_header=None,
         payload=None, dedup=True, dedup_key=None):
    """The one entry point callers should use.

    dedup-check → POST-with-retry → audit. `text` is the audit preview and the
    default dedup basis; `payload` is the actual JSON body (defaults to
    {"content": text}). Pass `dedup_key` to dedup on something OTHER than the
    visible text — e.g. content + a turn token — so identical text in different
    turns (the done-ping) still fires while same-turn re-fires are suppressed.
    Returns the HTTP code string, 'dedup', or None.
    """
    try:
        if dedup and is_duplicate(session, channel, dedup_key if dedup_key is not None else text):
            audit(session, event, channel, target, 'dedup', '', text)
            return 'dedup'
        body = payload if payload is not None else json.dumps({'content': text})
        code = post_with_retry(url, body, auth_header=auth_header)
        ok = bool(code and code.isdigit() and 200 <= int(code) < 300)
        audit(session, event, channel, target, 'sent' if ok else 'dropped', code, text)
        if not ok:
            _log_error(f'{event}: POST failed HTTP {code} target={target} chan={channel}')
        return code
    except Exception as e:
        _log_error(f'send crashed: {e}')
        return None


# ----------------------------------------------------------- coalescing buffer
def _buf_path(session, channel):
    safe = f'{session}__{channel}'.replace('/', '_')
    return os.path.join(_state_dir(), f'{safe}.logbuf')


def _chunk(text, cap=DISCORD_BODY_CAP):
    while text:
        yield text[:cap]
        text = text[cap:]


def _flush_buffer(session, channel, url, event='coalesce'):
    """Post everything currently buffered for (session, channel) as as-few-as-
    possible POSTs, then clear the buffer. Atomic rename claims the buffer so a
    concurrent flush cannot double-send."""
    path = _buf_path(session, channel)
    if not os.path.exists(path):
        return
    claim = path + f'.flushing.{os.getpid()}'
    try:
        os.replace(path, claim)     # atomically take ownership of the pending lines
    except Exception:
        return                      # someone else claimed it first
    try:
        with open(claim) as f:
            lines = [ln.rstrip('\n') for ln in f if ln.strip()]
    except Exception:
        lines = []
    try:
        os.remove(claim)
    except Exception:
        pass
    if not lines or not url:
        return
    combined = '\n'.join(lines)
    for part in _chunk(combined):
        send(session, event, channel, 'log', url, part, dedup=True)


def buffer_or_send(session, event, channel, url, text):
    """Append `text` to the per-channel log buffer; flush the buffer first if it
    is stale or full. With DISCORD_COALESCE=0 (or no url) posts immediately."""
    if not url:
        audit(session, event, channel, 'log', 'dropped', 'no-url', text)
        return
    if os.environ.get('DISCORD_COALESCE') == '0':
        send(session, event, channel, 'log', url, text)
        return
    try:
        path = _buf_path(session, channel)
        # flush existing buffer first if it's old or already large
        if os.path.exists(path):
            try:
                age = time.time() - os.path.getmtime(path)
                size = os.path.getsize(path)
            except Exception:
                age, size = 0, 0
            if age > COALESCE_MAX_AGE or size > COALESCE_MAX_CHARS:
                _flush_buffer(session, channel, url, event='coalesce-flush')
        with open(path, 'a') as f:
            f.write(text.replace('\n', '  ') + '\n')
        audit(session, event, channel, 'log', 'buffered', '', text)
    except Exception:
        # fall back to immediate send on any buffering error
        send(session, event, channel, 'log', url, text)


# --------------------------------------------------------------- CLI for bash
def _cli():
    """Thin CLI so discord-notify.sh (bash) can reach the same helpers.

    Usage:
      discord_outbound.py buffer  <session> <channel> <url> <text>
      discord_outbound.py flush   <session> <channel> <url>
      discord_outbound.py send    <session> <event> <channel> <target> <url> <text> [auth]
      discord_outbound.py audit   <session> <event> <channel> <target> <status> <http> <text>
    """
    if len(sys.argv) < 2:
        return 0
    cmd = sys.argv[1]
    a = sys.argv[2:]
    try:
        if cmd == 'buffer' and len(a) >= 4:
            buffer_or_send(a[0], 'PostToolUse', a[1], a[2], a[3])
        elif cmd == 'flush' and len(a) >= 3:
            _flush_buffer(a[0], a[1], a[2], event='stop-flush')
        elif cmd == 'send' and len(a) >= 6:
            auth = a[6] if len(a) > 6 and a[6] else None
            send(a[0], a[1], a[2], a[3], a[4], a[5], auth_header=auth)
        elif cmd == 'audit' and len(a) >= 7:
            audit(a[0], a[1], a[2], a[3], a[4], a[5], a[6])
    except Exception:
        pass
    return 0


if __name__ == '__main__':
    sys.exit(_cli())
