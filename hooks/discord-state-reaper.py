#!/usr/bin/env python3
"""
Standalone GC for ~/.claude/hooks/state/.

That directory accumulates one or more files per Claude Code session
(<session>.txt, .chatid, .routechatid, .parentchatid, .threadid, .stopcheck.lock,
<session>__<channel>.dedup.json, <session>__<channel>.logbuf, ...) and is never
reaped. As of 2026-07-13 it holds ~6000 files. Nothing wires this script into
any hook — it is meant to be run by hand (or from a separate cron/launchd job
Geoff sets up deliberately), never automatically from discord-notify.sh or any
PreToolUse/PostToolUse/Stop path.

Policy:
  - Dry-run by default. Pass --apply to actually delete anything.
  - Age-based: a file is only a delete candidate if its mtime is older than
    --max-age-days (default 14).
  - Session-liveness aware: before touching ANY file belonging to a session,
    try a non-blocking exclusive flock on that session's <session>.stopcheck.lock
    (if present). This mirrors the exact liveness signal discord-stop-check.py
    already uses for itself (fcntl.flock(..., LOCK_EX | LOCK_NB) on that same
    lock file — see discord-stop-check.py Defense A) rather than inventing a
    new one. If the flock cannot be acquired, another process holds it — the
    session is live — skip every file for that session this run. If the lock
    file does not exist, or the flock can be acquired (and is immediately
    released), the session is not currently active; age is the only gate.

Explicitly OUT OF SCOPE, do not wire this in expecting it to help:
  - The ~129 already-orphaned .logbuf files found on 2026-07-12 (dead sessions,
    oldest Jul 3 at time of writing). Those are being handled separately by a
    manual replay-or-bin decision Geoff has not made yet (see item 5 of
    discord-relay-durability-hardening.md) — they are also almost certainly
    younger than the 14-day default threshold, so this reaper would not touch
    them yet regardless. Do not lower the threshold or special-case .logbuf
    here to "clean those up" — that decision belongs to the separate replay
    effort, not to this GC pass.

Usage:
  discord-state-reaper.py                    # dry run, default state dir, 14d
  discord-state-reaper.py --apply             # actually delete
  discord-state-reaper.py --max-age-days 30   # different threshold
  discord-state-reaper.py --state-dir /tmp/x  # override (also honors
                                               # DISCORD_HOOK_STATE_DIR env var,
                                               # same knob the rest of the
                                               # discord hook code uses)
"""
import argparse
import fcntl
import os
import re
import sys
import time

SESSION_RE = re.compile(
    r'^([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})(?:__.*)?\.'
)

DEFAULT_MAX_AGE_DAYS = 14


def _state_dir(override=None):
    return (override or os.environ.get('DISCORD_HOOK_STATE_DIR')
            or os.path.expanduser('~/.claude/hooks/state'))


def _extract_session(name):
    """Return the session-id prefix for a state file, or None if the file
    doesn't follow the <session>[...] naming convention (e.g. the shared
    outbound-audit.log / hook-errors.log files, which are never per-session
    and must never be reaped by this script)."""
    m = SESSION_RE.match(name)
    return m.group(1) if m else None


def _session_is_live(state_dir, session):
    """Best-effort liveness check, mirroring discord-stop-check.py's own
    Defense-A lock (fcntl.flock LOCK_EX | LOCK_NB on <session>.stopcheck.lock).
    Returns True if that lock is currently held by another process (session is
    active), False if the lock file is absent or uncontended."""
    lock_path = os.path.join(state_dir, f'{session}.stopcheck.lock')
    if not os.path.exists(lock_path):
        return False
    try:
        fh = open(lock_path, 'r+')
    except Exception:
        # Can't even open it to check — be conservative and assume live so we
        # never delete out from under a session we couldn't verify.
        return True
    try:
        fcntl.flock(fh.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
    except (BlockingIOError, OSError):
        return True   # someone else holds it → live session
    else:
        fcntl.flock(fh.fileno(), fcntl.LOCK_UN)
        return False
    finally:
        fh.close()


def find_candidates(state_dir, max_age_days):
    """Yield (path, session, age_days) for every file old enough to be a
    delete candidate, grouped so a live session's files are never yielded."""
    cutoff = max_age_days * 86400
    now = time.time()
    try:
        names = os.listdir(state_dir)
    except Exception as e:
        print(f'error: cannot list {state_dir}: {e}', file=sys.stderr)
        return

    by_session = {}
    for name in names:
        session = _extract_session(name)
        if not session:
            continue  # not a per-session file (audit log, error log, etc.) — never touched
        by_session.setdefault(session, []).append(name)

    live_cache = {}
    for session, files in by_session.items():
        if session not in live_cache:
            live_cache[session] = _session_is_live(state_dir, session)
        if live_cache[session]:
            continue  # skip every file for a live session
        for name in files:
            path = os.path.join(state_dir, name)
            try:
                mtime = os.path.getmtime(path)
            except Exception:
                continue
            age = now - mtime
            if age >= cutoff:
                yield path, session, age / 86400.0


def main():
    ap = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0])
    ap.add_argument('--apply', action='store_true',
                     help='actually delete candidates (default: dry-run, list only)')
    ap.add_argument('--max-age-days', type=float, default=DEFAULT_MAX_AGE_DAYS,
                     help=f'age threshold in days (default {DEFAULT_MAX_AGE_DAYS})')
    ap.add_argument('--state-dir', default=None,
                     help='override state dir (also honors DISCORD_HOOK_STATE_DIR env var)')
    args = ap.parse_args()

    state_dir = _state_dir(args.state_dir)
    if not os.path.isdir(state_dir):
        print(f'error: state dir not found: {state_dir}', file=sys.stderr)
        return 1

    candidates = list(find_candidates(state_dir, args.max_age_days))
    if not candidates:
        print(f'no candidates >= {args.max_age_days}d old in {state_dir}')
        return 0

    total_bytes = 0
    for path, session, age_days in candidates:
        try:
            size = os.path.getsize(path)
        except Exception:
            size = 0
        total_bytes += size
        action = 'DELETE' if args.apply else 'would delete'
        print(f'{action}\t{age_days:.1f}d\t{size}B\t{path}')
        if args.apply:
            try:
                os.remove(path)
            except Exception as e:
                print(f'  ! failed to remove {path}: {e}', file=sys.stderr)

    verb = 'removed' if args.apply else 'would remove'
    print(f'\n{verb} {len(candidates)} file(s), {total_bytes} bytes total'
          + ('' if args.apply else ' (dry-run — pass --apply to delete)'))
    return 0


if __name__ == '__main__':
    sys.exit(main())
