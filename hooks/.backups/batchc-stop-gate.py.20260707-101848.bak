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
  3. handoff-detected scan   → once the model writes a handoff, never block again.
"""

import json
import os
import sys

STATE_DIR = os.path.expanduser("~/.claude/hooks/state")
PRESSURE_FILE = os.path.join(STATE_DIR, "session-pressure.json")

# Substantial-batch thresholds (any one trips it).
# cumulative_tool_calls counts every PostToolUse call; 15 is a real working batch.
SUBSTANTIAL_TOOL_CALLS = 15
SUBSTANTIAL_FILL_PCT = 0.35

HANDOFF_CHECKLIST = """\
[batchc §12 — handoff gate] This looks like a SUBSTANTIAL batch and no \
HANDOFF-*.md was written this session. Per batchc §12, complete the post-batch \
checklist BEFORE stopping:

1. Auto-memory: does MEMORY.md / project memory need a new entry from this batch? \
Write it now, not later.
2. Playbook: did this batch reveal a pattern, gotcha, or procedure worth a playbook? \
Name it explicitly; write it if it takes under 5 minutes.
3. Run /session-handoff NOW — pick a descriptive name yourself \
(HANDOFF-<topic>-<YYYY-MM-DD>-<HHMM>.md). Handoff is automatic, not advisory.
4. Close with the required statement: "Handoff written — context can now be cleared." \
On Discord-bound sessions, send it via the reply tool (text= param), not just the terminal.

If the work was genuinely minor, you may stop: say "Context safe to clear — no \
handoff needed." and stop again. This gate fires at most once per session, so a \
second stop will not be blocked.\
"""

VERIFIER_REMINDER = """\

[batchc §11 — verifier gate] This session touched MORE THAN ONE file with no \
subsequent /verify or /code-review call detected. Per batchc §11, multi-file \
changes require an independent verifier context before the task is "done":
  - Feature/behavior changes → run /verify (behavioral, drives the app)
  - Structural/spec changes  → run /code-review (diff-level analysis)
Run the appropriate verifier in a FRESH agent context, then stop again.\
"""


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
    if marker and os.path.exists(marker):
        sys.exit(0)  # loop guard 2: already fired once this session

    # --- Substantial-batch heuristic from session-pressure.json ---
    # Use cumulative_tool_calls (increments on every PostToolUse, both paths).
    # Fall back to tool_calls if cumulative not present (older state files).
    substantial = False
    try:
        ps = json.load(open(PRESSURE_FILE))
        if ps.get("session_id") == session_id:
            cumulative = ps.get("cumulative_tool_calls") or ps.get("tool_calls", 0) or 0
            fill_pct = ps.get("fill_pct", 0) or 0
            pressure = ps.get("pressure", "normal")
            if (cumulative >= SUBSTANTIAL_TOOL_CALLS
                    or fill_pct >= SUBSTANTIAL_FILL_PCT
                    or pressure in ("elevated", "high")):
                substantial = True
    except Exception:
        pass  # no/unreadable pressure state → treat as not substantial (fail-open)

    if not substantial:
        sys.exit(0)

    # --- Scan transcript JSONL for handoff, multi-file edits, and verify calls ---
    handoff_written = False
    multi_file_edited = False   # >1 distinct path written/edited by main session
    verify_called = False       # /verify or /code-review invoked after edits

    try:
        if transcript_path and os.path.exists(transcript_path):
            edited_paths = set()
            with open(transcript_path) as f:
                for line in f:
                    try:
                        e = json.loads(line)
                    except Exception:
                        continue
                    if e.get("type") != "assistant":
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
                        if name in ("Write", "Edit") and "HANDOFF-" in str(inp.get("file_path", "")):
                            handoff_written = True

                        # Multi-file edit detection (Write/Edit by main session)
                        if name in ("Write", "Edit"):
                            fp = inp.get("file_path", "")
                            if fp:
                                edited_paths.add(fp)

                        # Verify call detection — substring match catches flags and
                        # qualified names (e.g. "code-review --fix", "apps/web:verify")
                        if name == "Skill":
                            skill_val = inp.get("skill", "") or ""
                            if "verify" in skill_val or "code-review" in skill_val:
                                verify_called = True
                        elif name == "Bash":
                            cmd = str(inp.get("command", ""))
                            if "/verify" in cmd or "/code-review" in cmd:
                                verify_called = True

            if len(edited_paths) > 1:
                multi_file_edited = True
    except Exception:
        pass  # fail-open: parse errors don't trigger the verifier gate

    if handoff_written:
        sys.exit(0)  # loop guard 3 + the whole point: handoff exists, allow stop

    # --- Build combined block message (never double-block) ---
    needs_verifier = multi_file_edited and not verify_called

    # Compose the full message; verifier reminder appended only when triggered
    block_msg = HANDOFF_CHECKLIST
    if needs_verifier:
        block_msg += VERIFIER_REMINDER

    # --- Block: mark (so we fire only once), write to stderr, exit 2 ---
    if marker:
        try:
            os.makedirs(STATE_DIR, exist_ok=True)
            with open(marker, "w") as f:
                f.write("1")
        except Exception:
            pass

    sys.stderr.write(block_msg + "\n")
    sys.exit(2)


if __name__ == "__main__":
    main()
