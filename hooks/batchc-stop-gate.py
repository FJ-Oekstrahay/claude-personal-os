#!/usr/bin/env python3
"""
Stop hook gate: enforce batchc §12 — force a handoff when a substantial batch
ends with no HANDOFF-*.md written this session.

Wired as a Stop hook in settings.json alongside discord-notify.sh. This script
runs SYNCHRONOUSLY and may exit 2 to BLOCK the stop. discord-notify.sh keeps its
own job (flush trailing text + Discord closing-statement "done" ping) untouched.

Decision (reviews/prompts/geoff-answers-workflow-review.md, Q1): BLOCK, not warn
("force handoff").

Input: JSON on stdin — {session_id, transcript_path, stop_hook_active, cwd, ...}.
Exit codes (Claude Code Stop-hook contract):
  exit 0  — allow the stop.
  exit 2  — block the stop; STDERR is fed back to the model as the reason.

Fail-OPEN on any error or missing signal. NOTE: this deliberately INVERTS the
global CLAUDE.md "fail-closed on parse errors" lesson, which was written for
PreToolUse *protection* hooks (block-on-doubt protects a resource). For a Stop
hook, "closed" = blocking the stop; failing closed on a parse bug would wedge
EVERY session in an un-stoppable loop. So the safe failure here is to allow the
stop. Loud-but-stoppable beats wedged.

Loop prevention (three layers, any one suffices):
  1. stop_hook_active=True  → we're already in a stop-hook continuation; allow.
  2. per-session marker file → block at most once per session.
  3. handoff-detected scan   → a written handoff clears the §12 obligation.
     NOTE (2026-07-24): this is no longer an unconditional "never block again".
     Geoff ruled that a handoff must NOT satisfy the §11 verifier gate — it
     records that work happened, it is not evidence anyone reviewed it. So a
     handoff allows the stop only when no review is outstanding. Layers 1 and 2
     are what guarantee no session can wedge; layer 3 is a §12 clearance only.

Lessons gate (added 2026-08-25, prompts/tighten-handoff-lessons-capture.md): a
written handoff no longer clears §12 by itself either — it must actually
CONTAIN a "## Lessons Captured" section. Measured across duel-dingo's own
handoffs/: 13 of 47 (28%) omit that section entirely, despite /session-handoff
marking it REQUIRED — and it was skipped in 4 of the 6 most recent sessions at
the time this was found. "A handoff was written" and "a handoff was written
that self-checked whether MEMORY.md/a playbook needed the finding" are
different claims; only the second is the actual §12 obligation. The check is
presence-only (does the header exist), not a quality judgment — the skill's own
escape hatch ("if nothing worth capturing, say so explicitly") still applies,
it just has to say so INSIDE the handoff, not by omitting the section.

Discord notify (2026-07-18, handoffs/HANDOFF-stop-gate-discord-notify-gap-2026-07-18-1124.md,
Option A): the block message below is written to stderr, which is internal to the
model's own context and has NO path to Discord. On Discord-bound sessions the model
never sees this until it re-reads its own context, so `_notify_discord()` best-effort
mirrors the block text to the discussion channel via discord_outbound.py's `send`
CLI (same bot-API POST shape discord-stop-check.py already uses), fired as a
detached background process so it never delays the exit(2) block. Silent no-op on
terminal-only sessions (no chat_id) or missing bot token — matches the existing
"nowhere to post, stay silent" convention in discord-notify.sh.
"""

import json
import os
import re
import subprocess
import sys

STATE_DIR = os.path.expanduser("~/.claude/hooks/state")
PRESSURE_FILE = os.path.join(STATE_DIR, "session-pressure.json")
DISCORD_CONF = os.path.expanduser("~/.claude/hooks/discord-webhook.conf")
DISCORD_OUTBOUND_HELPER = os.path.expanduser("~/.claude/hooks/discord_outbound.py")
DISCORD_MSG_CAP = 1900  # Discord's 2000-char body limit, minus headroom for the prefix

# Substantial-batch thresholds (any one trips it).
# cumulative_tool_calls counts every PostToolUse call; 15 is a real working batch.
SUBSTANTIAL_TOOL_CALLS = 15
# fill_pct is now relative to the model's real context window (1M on opus-5/
# sonnet-5-class), so 0.35 means 350k tokens — far too high to fire in practice.
# Trip on absolute context tokens instead; the pct is kept as a backstop for
# small-window models where 35% is a genuinely substantial batch.
# 150k, not 70k: 70k is reachable by two or three sizeable Reads, so a purely
# read-only exploratory session would trip the §12 handoff checklist having
# produced nothing to hand off. cumulative_tool_calls >= 15 already catches any
# real working batch; this arm is meant to catch a big-context one.
SUBSTANTIAL_FILL_PCT = 0.35
SUBSTANTIAL_CONTEXT_TOKENS = 150_000


def _read_pressure_state(session_id):
    """Prefer this session's own state file; the shared one carries whichever
    session ticked last, which under concurrency silently fails this gate open."""
    candidates = []
    if session_id:
        safe = "".join(c for c in session_id if c.isalnum() or c in "-_")
        candidates.append(os.path.join(STATE_DIR, f"session-pressure-{safe}.json"))
    candidates.append(PRESSURE_FILE)
    for path in candidates:
        try:
            with open(path) as f:
                state = json.load(f)
        except Exception:
            continue
        if state.get("session_id") == session_id:
            return state
    return None

HANDOFF_CHECKLIST = """\
[batchc §12 — handoff gate] This looks like a SUBSTANTIAL batch and no \
HANDOFF-*.md was written this session. Per batchc §12, complete the post-batch \
checklist BEFORE stopping:

0. If you already told the user "done" or "safe to clear" earlier this turn, \
send a correction now (Discord-bound: via the reply tool) before doing anything \
else below — this block means that declaration was premature.
1. Auto-memory: does MEMORY.md / project memory need a new entry from this batch? \
Write it now, not later.
2. Playbook: did this batch reveal a pattern, gotcha, or procedure worth a playbook? \
Name it explicitly; write it if it takes under 5 minutes.
3. Run /session-handoff NOW — pick a descriptive name yourself \
(HANDOFF-<topic>-<YYYY-MM-DD>-<HHMM>.md). Handoff is automatic, not advisory.
4. Close with the required statement: "Handoff written — context can now be cleared." \
On Discord-bound sessions, send it via the reply tool (text= param), not just the terminal.

Before stopping, declare EXACTLY ONE end-state, accurately — and never claim \
safe-to-clear while anything is still running:
- DONE — handoff written (or the work was genuinely trivial) and nothing is \
running. Say: "Done — safe to exit or clear."
- PAUSED — no completed batch needs a handoff and nothing is running, but work \
remains for later. Say: "Paused — nothing running, safe to exit; resume next \
session with /load-handoff."
- IN FLIGHT — background agents/tasks are still running. Say: "Work in flight — \
do NOT exit or clear. N background agents are running; exiting or restarting \
kills them and loses their results. I'll continue when they report." NEVER say \
safe-to-clear in this state.
This gate fires at most once per session, so a second stop will not be blocked.\
"""

LESSONS_MISSING_REMINDER = """\
[batchc §12 — lessons gate] A handoff was written this session, but it has no \
"## Lessons Captured" section. That section is REQUIRED by /session-handoff — \
it is the mechanism that stops a hard-won finding from being silently \
re-derived next session (see feedback_struggle_earns_a_playbook_not_just_a_memory_note).

Before stopping, edit the handoff just written and add a "## Lessons Captured" \
section covering:
1. Does MEMORY.md / project memory need a new entry from this session? Write it now.
2. Did this session reveal a pattern, gotcha, or procedure worth a playbook in \
~/.openclaw/workspace/memory/playbooks/? Name it explicitly; write it if it takes \
under 5 minutes.
If genuinely nothing is worth capturing, add the header anyway and say so \
explicitly — this gate only catches an OMITTED header, not a short answer.

Then stop again.\
"""

VERIFIER_REMINDER = """\

[batchc §11 — verifier gate] This session edited MORE THAN ONE file, or edited a \
LIVE SHARED SURFACE (a hook, slash command, agent/skill definition, settings.json, \
or a launchd plist — one edit there changes behavior for every session on this \
machine). No independent review of those edits was detected.

Per batchc §11 the requirement is an INTENT, not one specific command: a separate \
agent context must review the change. The agent that wrote the code does not \
verify its own work. Writing a handoff does NOT satisfy this — a handoff records \
that work happened, it is not evidence anyone reviewed it.

Two mechanisms satisfy this. Pick one and do it NOW:

  1. Dispatch a reviewer subagent over the diff — this is the one YOU can always \
do. Use the Agent tool.
     DEFAULT: subagent_type "cto" (or "gadfly"). Both run on Sonnet and are the \
right proportionate cost for an ordinary change.
     ESCALATE to "The Architect" (Opus) only when the change is genuinely hard — \
subtle control flow, concurrency, a security or data-loss surface, or anything \
where being wrong is expensive. Opus draws on the weekly cap; spend it on purpose, \
not by default.
     "Safety Officer" (Opus) for anything touching flight-controller or hardware \
safety, regardless of size.
     Any OTHER subagent_type (general-purpose, cob, seymour, ...) counts only if \
you include the literal marker [verifier-gate] in the Agent prompt — that keeps a \
routine search or lookup agent from satisfying this gate by accident.

  2. Ask the user to run /verify or /code-review. Those ARE real built-in commands \
(compiled into the CC binary, not files under ~/.claude/commands), but both are \
registered userInvocable + disableModelInvocation — so the harness structurally \
refuses to let YOU call them. Asking the user to type one is the correct move here, \
not a failure to report.

Do NOT tell the user you are "blocked", that "/code-review isn't available in this \
session", or that "/verify doesn't exist" — all three are wrong, and option 1 is \
always open to you. Note also that the Agent tool needs no opt-in: the "only when \
the user has explicitly opted into multi-agent orchestration" rule belongs to the \
Workflow tool, which is a DIFFERENT tool. Do not generalize it to Agent.

Run the review, then stop again.\
"""

# --- §11 verifier detection tables -------------------------------------------
# Subagent types whose entire purpose is adversarial/structural review. Dispatching
# one of these over a change IS an independent reviewer context by definition.
REVIEWER_SUBAGENT_TYPES = {
    "the architect", "architect", "code-reviewer", "code reviewer",
    "cto", "gadfly", "critic", "safety officer",
}
# Explicit opt-in marker so a generic subagent (general-purpose, cob, seymour)
# can be dispatched AS the §11 verifier without every routine search agent
# accidentally disarming the gate.
VERIFIER_MARKER = "[verifier-gate]"
# Exact skill names that satisfy §11. Matched exactly (after stripping any
# plugin/dir scope prefix) — the previous substring match is what let unrelated
# names through.
VERIFIER_SKILL_NAMES = {"verify", "code-review"}
# A user-typed slash command lands in the transcript as a `user` entry carrying
# <command-name>/foo</command-name>, NOT as an assistant tool_use — because both
# commands are disableModelInvocation and the model cannot emit them.
USER_VERIFIER_COMMANDS = (
    "<command-name>/verify</command-name>",
    "<command-name>/code-review</command-name>",
)

# Live shared surfaces: one edit here changes behavior for EVERY session on this
# machine, so it earns a reviewer regardless of file count. Kept deliberately
# narrow and path-anchored — a broad match would nag on ordinary source edits
# and the gate would get ignored, which is worse than not having it.
LIVE_SURFACE_SUFFIXES = (
    "/.claude/settings.json",
    "/.claude/settings.local.json",
)
LIVE_SURFACE_DIRS = (
    "/.claude/hooks/",
    "/.claude/commands/",
    "/.claude/agents/",
    "/.claude/skills/",
    "/.claude/output-styles/",
    "/.openclaw/bin/",
    "/Library/LaunchAgents/",
)

# Matches the resolved destination path echoed by the canonical
# /session-handoff rename command's own `ls -la "$f"` (session-handoff.md:
# "The final `ls -la` prints the real path"). Used to read the PRECISE final
# handoff path out of that Bash tool_use's tool_result, rather than guessing
# via mtime — see _newest_handoff_sibling_content's note on why guessing is
# unsafe under concurrent peer sessions.
RENAME_PATH_RE = re.compile(r'(\S*HANDOFF-\S+\.md)')


def _is_scratch_path(path):
    """True if `path` is a throwaway scratch file, not a reviewable change.

    The §11 file-count arm had no path filter, so a session that wrote two
    disposable files — a debug script and its output, a pair of /tmp fixtures —
    tripped the verifier gate with no reviewable change in existence. Observed:
    a reviewer subagent wrote two sandboxed repro harnesses under /tmp and the
    gate demanded an independent review of those. That is how a gate earns being
    ignored on the change that actually matters.

    Only the file-COUNT arm uses this. The live-surface arm stays unfiltered —
    it is path-anchored to ~/.claude and cannot match these prefixes anyway.
    """
    prefixes = ["/tmp/", "/private/tmp/", "/var/folders/"]
    tmpdir = os.environ.get("TMPDIR")
    if tmpdir:
        prefixes.append(os.path.join(tmpdir, ""))
    try:
        expanded = os.path.abspath(os.path.expanduser(str(path)))
    except Exception:
        return False

    # A background job's working directory is real work, whatever path it sits
    # under. CLAUDE_JOB_DIR's convention is not documented and could not be
    # confirmed from an interactive session; if it is ever placed under a temp
    # path, every edit a bg/longrun session makes would be misfiled as scratch
    # and skip the §11 count arm silently. Cheaper to exclude it than to find
    # out the hard way.
    job_dir = os.environ.get("CLAUDE_JOB_DIR")
    if job_dir:
        try:
            jd = os.path.abspath(os.path.expanduser(job_dir))
            if expanded.startswith(os.path.join(jd, "")) or expanded == jd:
                return False
        except Exception:
            pass
    for cand in (expanded, os.path.realpath(expanded)):
        if any(cand.startswith(p) for p in prefixes):
            return True
    return False


# --- Handoff on-disk content resolution -------------------------------------
# NOTE (2026-08-25, second cto review — FAIL on the first lessons-check
# design): that version inferred `handoff_has_lessons` from the `content` of
# a `Write` tool_use, and only `Write` — never `Edit`. But the reminder text
# this hook itself emits tells the model to "edit the handoff just written,"
# which is the natural, low-diff way to add a missing section to an
# already-existing multi-KB file. A model that follows that instruction via
# `Edit` was invisible to the old check forever, and once the marker-fired
# re-check (same day) made this check re-run on every subsequent Stop, that
# dead detection became a live, un-clearable block — the exact wedge a Stop
# hook must never produce. Reading the file's actual current content
# sidesteps the whole problem: it doesn't matter which tool the model used,
# only what's on disk now.
#
# NOTE (2026-08-25, same-day follow-up — a THIRD bug, caught by testing this
# fix against a simulated concurrent peer, not by review): an early version
# of the disk-read fix tried each tracked path via ONE function that mixed an
# exact read with a same-path glob-fallback guess, called in an unordered
# `for hp in handoff_paths:` loop with a `break` on first match. That let the
# STALE draft path's own glob-fallback (see _newest_handoff_sibling) win the
# race and return a WRONG file's content before the precise, resolved path
# elsewhere in the same set was ever tried — confirmed live: a synthetic
# "peer" handoff with a newer mtime and a real Lessons section caused this
# session's own lessons-less handoff to read as compliant. Splitting into two
# explicit PASSES (below, in main()) fixes it structurally: every tracked
# path gets an EXACT read first, across the WHOLE set, before any glob
# guessing is attempted for ANY of them — so a precise match can never lose a
# race to an imprecise one.


def _read_file_if_exists(path):
    """Exact read only — no guessing. Returns None (not "") if unreadable,
    so callers can distinguish "empty file" from "couldn't read it"."""
    try:
        with open(path) as f:
            return f.read()
    except Exception:
        return None


def _newest_handoff_sibling_content(tracked_path):
    """Last-resort fallback: the newest HANDOFF-*.md in tracked_path's own
    directory. Exists for the DRAFT path specifically (.HANDOFF-draft.md,
    which a `Bash mv` renames away — untracked, since only Write/Edit
    tool_use are scanned — so the draft itself no longer exists on disk by
    the time this hook runs) or any flow whose real destination the rename
    parser in main() didn't catch.

    This is a GUESS, not a precise resolution, and is only ever called (see
    main()'s two-pass structure) after every tracked path in the set has
    already failed an EXACT read — never as a way to second-guess a path
    that WAS readable. Geoff has an active peer session in this exact repo
    as this is being written; if a peer ALSO renames a handoff into the same
    directory around the same time, mtime ordering could still pick THEIR
    file over a legitimate empty result here, and this session can never fix
    a peer's file — a different-shaped version of the same "must never
    wedge" failure the marker-fired fix above exists to prevent. That
    residual risk is accepted here (last resort, exercised only when nothing
    precise was found at all) rather than solved, unlike the common-path
    case, which the two-pass ordering in main() does solve precisely.
    """
    try:
        d = os.path.dirname(tracked_path) or "."
        siblings = [os.path.join(d, n) for n in os.listdir(d)
                    if n.startswith("HANDOFF-") and n.endswith(".md")]
        if not siblings:
            return None
        newest = max(siblings, key=os.path.getmtime)
    except Exception:
        return None
    return _read_file_if_exists(newest)


def _is_live_surface(path):
    """True if `path` is a shared runtime surface every session depends on.

    Checks BOTH the expanded path and its realpath: today ~/.claude is a real
    directory, but if it ever becomes a symlink, realpath alone would resolve the
    ".claude/hooks/" marker out of the string and this gate would fail SILENTLY —
    the worst failure mode available to it. Never raises; a bad path just isn't a
    live surface.
    """
    cands = []
    try:
        expanded = os.path.abspath(os.path.expanduser(str(path)))
        cands.append(expanded)
        cands.append(os.path.realpath(expanded))
    except Exception:
        return False
    for p in cands:
        if p.endswith(LIVE_SURFACE_SUFFIXES) or any(d in p for d in LIVE_SURFACE_DIRS):
            return True
    return False


def _resolve_chat_id(session_id):
    """Mirrors discord-notify.sh's _resolve_chat_id: routechatid (thread→parent)
    takes priority over chatid, then the DISCORD_CHAT_ID env fallback."""
    state_base = os.path.join(STATE_DIR, session_id)
    for suffix in ("routechatid", "chatid"):
        try:
            v = open(f"{state_base}.{suffix}").read().strip()
            if v:
                return v
        except Exception:
            pass
    return os.environ.get("DISCORD_CHAT_ID", "")


def _load_bot_token():
    """Mirrors discord-stop-check.py's load_conf() bot-token lookup."""
    try:
        with open(DISCORD_CONF) as f:
            for line in f:
                line = line.strip()
                if line.startswith("DISCORD_BOT_TOKEN="):
                    return line.partition("=")[2].strip().strip('"').strip("'")
    except Exception:
        pass
    return ""


def _notify_discord(session_id, text):
    """Best-effort mirror of the block message to the discussion channel.
    Fire-and-forget via a detached subprocess — never delays the exit(2) block,
    and any failure here must never affect the gate's own control flow."""
    try:
        chat_id = _resolve_chat_id(session_id)
        bot_token = _load_bot_token()
        if not chat_id or not bot_token:
            return  # no Discord binding for this session — stay silent
        if len(text) > DISCORD_MSG_CAP:
            text = text[:DISCORD_MSG_CAP] + "..."
        url = f"https://discord.com/api/v10/channels/{chat_id}/messages"
        auth = f"Authorization: Bot {bot_token}"
        subprocess.Popen(
            ["python3", DISCORD_OUTBOUND_HELPER, "send", session_id,
             "batchc-stop-gate", chat_id, "discussion", url, text, auth],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            start_new_session=True,
        )
    except Exception:
        pass


def main():
    raw = sys.stdin.read()
    try:
        data = json.loads(raw)
    except Exception:
        sys.exit(0)  # fail-open: never wedge a session on a parse bug

    session_id = data.get("session_id", "") or ""
    transcript_path = data.get("transcript_path", "") or ""
    if data.get("stop_hook_active"):
        sys.exit(0)  # loop guard 1: already inside a stop-hook continuation

    marker = os.path.join(STATE_DIR, f"{session_id}.batchc-gate-fired") if session_id else None
    marker_fired = bool(marker and os.path.exists(marker))
    # NOTE (2026-08-25, cto review of the lessons-gate addition below): loop
    # guard 2 used to be an unconditional `sys.exit(0)` here, BEFORE any
    # transcript scan. That made the lessons check (added same day) dead for
    # the exact population it targets: a fresh session with no handoff yet
    # gets the FULL checklist on its first Stop (handoff_written is still
    # False, so `lessons_missing` can't even be computed), the marker gets
    # written, and every later Stop this session exits right here with no
    # re-scan — so a handoff written in response, still missing the section,
    # was never re-checked. Fixed by remembering marker_fired instead of
    # exiting immediately, and narrowing what marker_fired suppresses (see
    # the decision block below): the full checklist/verifier reminder still
    # fire at most once, but the lessons check — cheap, deterministic, and
    # self-clearing the instant the model adds the header — is allowed to
    # keep checking. This cannot reproduce the infinite-loop risk the marker
    # exists to prevent, because it can only block while genuinely
    # non-compliant and the fix is a one-line edit the model is told exactly
    # how to make.

    # --- Substantial-batch heuristic from session-pressure.json ---
    # Use cumulative_tool_calls (increments on every PostToolUse, both paths).
    # Fall back to tool_calls if cumulative not present (older state files).
    substantial = False
    try:
        ps = _read_pressure_state(session_id)
        if ps is not None:
            cumulative = ps.get("cumulative_tool_calls") or ps.get("tool_calls", 0) or 0
            fill_pct = ps.get("fill_pct", 0) or 0
            context_tokens = ps.get("context_tokens", 0) or 0
            pressure = ps.get("pressure", "normal")
            if (cumulative >= SUBSTANTIAL_TOOL_CALLS
                    or context_tokens >= SUBSTANTIAL_CONTEXT_TOKENS
                    or fill_pct >= SUBSTANTIAL_FILL_PCT
                    or pressure in ("elevated", "high")):
                substantial = True
    except Exception:
        pass  # no/unreadable pressure state → treat as not substantial (fail-open)

    if not substantial:
        sys.exit(0)

    # --- Scan transcript JSONL for handoff, multi-file edits, and verify calls ---
    handoff_written = False
    handoff_has_lessons = False # resolved AFTER the scan by reading the handoff's
                                 # actual on-disk content — see _read_file_if_exists /
                                 # _newest_handoff_sibling_content and the two-pass note below
    multi_file_edited = False   # >1 distinct path written/edited by main session
    live_surface_edited = False # any edit to a shared runtime surface (see below)
    verify_called = False       # independent review detected after the last edit

    try:
        if transcript_path and os.path.exists(transcript_path):
            edited_paths = set()
            handoff_paths = set()  # file_path of every is_handoff Write/Edit this
                                    # session, PLUS the precise resolved path from
                                    # any rename's ls -la (see pending_rename_ids)
            pending_rename_ids = set()  # tool_use ids of Bash calls matching the
                                         # canonical draft-rename command, awaiting
                                         # their tool_result for the real dest path
            with open(transcript_path) as f:
                for line in f:
                    try:
                        e = json.loads(line)
                    except Exception:
                        continue

                    etype = e.get("type")
                    # A user-typed /verify or /code-review satisfies §11. These are
                    # userInvocable-only builtins, so this is the ONLY shape they
                    # can appear in — there is no assistant tool_use for them.
                    if etype == "user":
                        content = e.get("message", {}).get("content", "")
                        # A genuinely user-typed command arrives as a plain STRING.
                        # Tool RESULTS are also type=="user" but carry a LIST of
                        # blocks, and their output can echo the literal
                        # <command-name> tag (e.g. grepping this very hook, or
                        # reading its test harness) — matching those would be a
                        # false PASS of exactly the kind this rewrite exists to kill.
                        if isinstance(content, str):
                            if any(c in content for c in USER_VERIFIER_COMMANDS):
                                verify_called = True
                        elif isinstance(content, list) and pending_rename_ids:
                            # Tool results for a Bash rename we're tracking — pull
                            # the precise destination path out of its `ls -la`
                            # output rather than guessing by mtime.
                            for blk in content:
                                if (not isinstance(blk, dict)
                                        or blk.get("type") != "tool_result"
                                        or blk.get("tool_use_id") not in pending_rename_ids):
                                    continue
                                blk_content = blk.get("content", "")
                                texts = []
                                if isinstance(blk_content, str):
                                    texts.append(blk_content)
                                elif isinstance(blk_content, list):
                                    texts.extend(
                                        str(item.get("text", ""))
                                        for item in blk_content
                                        if isinstance(item, dict) and item.get("type") == "text")
                                for t in texts:
                                    handoff_paths.update(RENAME_PATH_RE.findall(t))
                        continue
                    if etype != "assistant":
                        continue
                    content = e.get("message", {}).get("content", [])
                    if not isinstance(content, list):
                        continue
                    for b in content:
                        if not isinstance(b, dict) or b.get("type") != "tool_use":
                            continue
                        name = b.get("name", "")
                        inp = b.get("input", {}) or {}

                        # Handoff detection
                        is_handoff = (name in ("Write", "Edit")
                                      and "HANDOFF-" in str(inp.get("file_path", "")))
                        if is_handoff:
                            handoff_written = True
                            fp = str(inp.get("file_path", "") or "")
                            if fp:
                                handoff_paths.add(fp)

                        # Multi-file edit detection (Write/Edit by main session).
                        # The handoff file itself is NOT a code change — exclude it
                        # from both the file count and the reset below.
                        if name in ("Write", "Edit") and not is_handoff:
                            fp = inp.get("file_path", "")
                            if fp:
                                edited_paths.add(fp)
                                # §11 is about the FINAL state of the code. A review
                                # that ran BEFORE this edit did not review this edit,
                                # so an early-session reviewer must not disarm the
                                # gate for everything that follows it. Resetting here
                                # means only a verifier dispatched after the LAST
                                # substantive edit counts.
                                verify_called = False

                        # --- §11 verifier detection ---
                        # NOTE: there is deliberately NO Bash branch here. The old
                        # code matched the substring "/verify" in any Bash command,
                        # which a FILE PATH satisfies — `python3 scripts/verify_claims.py`
                        # (run by financial's reanchor.py on every re-anchor) silently
                        # disarmed this gate for the rest of the session. Since /verify
                        # and /code-review are user-only slash commands, they can never
                        # legitimately appear as a Bash command, so the branch had zero
                        # true positives and only ever produced false PASSes. Removed.
                        if name == "Skill":
                            # exact match after stripping any plugin/dir scope prefix
                            # (e.g. "apps/web:verify" -> "verify")
                            skill_val = str(inp.get("skill", "") or "").strip().lower()
                            if skill_val.rpartition(":")[2] in VERIFIER_SKILL_NAMES:
                                verify_called = True
                        elif name in ("Agent", "Task"):
                            # An Agent dispatch to a reviewer subagent IS the §11
                            # intent ("a separate agent context has reviewed it").
                            # Verified against this CC version: the tool serializes
                            # as name="Agent" with subagent_type/prompt/description.
                            st = str(inp.get("subagent_type", "") or "").strip().lower()
                            blob = (str(inp.get("prompt", "") or "") + " "
                                    + str(inp.get("description", "") or "")).lower()
                            if st in REVIEWER_SUBAGENT_TYPES or VERIFIER_MARKER in blob:
                                verify_called = True

                        # --- Handoff-rename tracking (unrelated to §11 above —
                        # that NOTE is specifically about NOT using Bash command
                        # text to satisfy verify_called, which stays true). This
                        # is a Bash branch, but only ever feeds handoff_paths: the
                        # canonical /session-handoff rename
                        # (`mv "$PWD/handoffs/.HANDOFF-draft.md" "$f"`) is a Bash
                        # tool_use, and its resolved destination only appears in
                        # the tool_result of the trailing `ls -la "$f"` in that
                        # same command — record the id here, extracted on the
                        # matching tool_result above (see pending_rename_ids).
                        if name == "Bash":
                            cmd = str(inp.get("command", "") or "")
                            # NOTE (2026-08-25, third cto review, MAJOR):
                            # requiring "mv" + ".HANDOFF-draft.md" alone is an
                            # unanchored substring match on the WHOLE command
                            # text — a Bash call that merely investigates this
                            # hook (e.g. `grep -n mv .HANDOFF-draft.md ...`)
                            # would satisfy it too, and any HANDOFF-*.md-shaped
                            # path elsewhere in that call's tool_result output
                            # could then enter handoff_paths untrusted. The
                            # reviewer noted this can only ever produce a false
                            # PASS (Pass 1 is OR-across-the-set — a spurious
                            # entry can't suppress the real path also being
                            # checked), never a false BLOCK, so it carries no
                            # wedge risk — but it's a one-line, strictly
                            # NARROWING fix, so applying it anyway rather than
                            # leaving a known gap: also require "ls -la" in
                            # cmd, since only the real rename chain pairs the
                            # mv with a trailing ls -la on the same $f.
                            if ("mv" in cmd and ".HANDOFF-draft.md" in cmd
                                    and "ls -la" in cmd):
                                tu_id = b.get("id")
                                if tu_id:
                                    pending_rename_ids.add(tu_id)

            # Resolve handoff_has_lessons from actual disk content, not the
            # tool-call payload. TWO EXPLICIT PASSES, deliberately not one
            # loop with a fallback per-path (see the NOTE above
            # _read_file_if_exists for the bug that shape had): every tracked
            # path gets an EXACT read first, across the WHOLE set, before any
            # path is allowed to fall back to a glob guess. That ordering is
            # what stops an unreadable stale path (e.g. the pre-rename draft)
            # from guessing its way to a WRONG file while a precise path
            # elsewhere in the same set was never tried.
            if handoff_paths:
                checked_any = False
                # Pass 1 — exact reads only, no guessing.
                for hp in handoff_paths:
                    text = _read_file_if_exists(hp)
                    if text is None:
                        continue
                    checked_any = True
                    if "## Lessons Captured" in text:
                        handoff_has_lessons = True
                        break
                # Pass 2 — nothing in the set was directly readable (e.g.
                # every tracked path was a pre-rename draft that the ls -la
                # parser didn't catch). Now, and only now, fall back to a
                # glob guess — see _newest_handoff_sibling_content for the
                # residual concurrency caveat this still carries.
                if not checked_any:
                    for hp in handoff_paths:
                        text = _newest_handoff_sibling_content(hp)
                        if text is None:
                            continue
                        checked_any = True
                        if "## Lessons Captured" in text:
                            handoff_has_lessons = True
                        break
                if not checked_any:
                    # Every tracked path was unreadable (deleted, permissions,
                    # unusual layout) — inconclusive, not "missing". Fail
                    # toward NOT blocking; see the module docstring's
                    # fail-open rationale for why a Stop hook must never wedge
                    # on an I/O condition it can't attribute to the model's
                    # own non-compliance.
                    handoff_has_lessons = True

            # Scratch files are not a reviewable change — see _is_scratch_path.
            # The live-surface arm below deliberately keeps the unfiltered set.
            substantive_paths = {p for p in edited_paths if not _is_scratch_path(p)}
            if len(substantive_paths) > 1:
                multi_file_edited = True
            # Threshold (Geoff, 2026-07-24): file COUNT is a weak proxy for risk.
            # A single edit to a live shared surface — a hook every session
            # executes, a slash command every session reads, gateway/agent config
            # — deserves a second context regardless of count. Ordinary
            # single-file source edits are still exempt (§7b).
            if any(_is_live_surface(p) for p in edited_paths):
                live_surface_edited = True
    except Exception:
        pass  # fail-open: parse errors don't trigger the verifier gate

    # --- Verifier gate (§11) ---
    # Deliberately evaluated BEFORE the handoff short-circuit (Geoff, 2026-07-24):
    # a handoff is a RECORD that work happened, not evidence anyone reviewed it.
    # Letting it satisfy §11 meant "edit 5 files, write a handoff, skip all
    # review, stop clean" — which contradicts batchc.md's own wording that a
    # multi-file change is NOT done until a separate agent context has reviewed it.
    needs_verifier = (multi_file_edited or live_surface_edited) and not verify_called
    lessons_missing = handoff_written and not handoff_has_lessons

    if marker_fired:
        # The full §12 checklist and the §11 verifier reminder already fired
        # once this session (that's what set the marker) — don't repeat them.
        # The lessons check is the one exception: it's the only reason left
        # that can legitimately still need a nag (see NOTE above marker_fired).
        if lessons_missing:
            block_msg = LESSONS_MISSING_REMINDER.lstrip("\n")
            gate_label = "§12 — lessons gate"
            _notify_discord(session_id, f":no_entry: **batchc {gate_label} blocked stop**\n{block_msg}")
            sys.stderr.write(block_msg + "\n")
            sys.exit(2)
        sys.exit(0)  # loop guard 2: already fired once, and nothing re-blockable remains

    if handoff_written and not needs_verifier and not lessons_missing:
        sys.exit(0)  # loop guard 3: handoff exists, has lessons, AND review happened

    # --- Build the block message ---
    # If the handoff is already written, don't re-run the full §12 checklist at
    # the model — only the outstanding piece(s): the lessons section and/or the
    # review.
    if handoff_written:
        block_msg = ""
        if lessons_missing:
            block_msg += LESSONS_MISSING_REMINDER
        if needs_verifier:
            block_msg += VERIFIER_REMINDER
        block_msg = block_msg.lstrip("\n")
    else:
        block_msg = HANDOFF_CHECKLIST
        if needs_verifier:
            block_msg += VERIFIER_REMINDER

    # --- Block: mark (so the FULL checklist/verifier reminder fire only once —
    # see marker_fired above for why the lessons check is exempt), write to
    # stderr, exit 2 ---
    if marker:
        try:
            os.makedirs(STATE_DIR, exist_ok=True)
            with open(marker, "w") as f:
                f.write("1")
        except Exception:
            pass

    # Name the gate that ACTUALLY blocked. When the handoff is already written,
    # the outstanding obligation is the lessons section and/or the review, and
    # a bare "§12 handoff gate" header over that text reads as a contradiction
    # on Discord (a handoff clearly exists).
    if not handoff_written:
        gate_label = "§12 — handoff gate"
    elif lessons_missing and needs_verifier:
        gate_label = "§12/§11 — lessons + verifier gate"
    elif lessons_missing:
        gate_label = "§12 — lessons gate"
    else:
        gate_label = "§11 — verifier gate"
    _notify_discord(session_id, f":no_entry: **batchc {gate_label} blocked stop**\n{block_msg}")

    sys.stderr.write(block_msg + "\n")
    sys.exit(2)


if __name__ == "__main__":
    main()
