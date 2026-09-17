#!/usr/bin/env bash
# TEMPLATE — UserPromptSubmit hook: re-inject a small, non-negotiable core
# snippet on EVERY turn, so mid-session context compaction can't silently
# drop it. Copy into a project's .claude/hooks/, point CORE_SNIPPET_PATH at
# a file containing the snippet (do not heredoc-edit this script directly —
# edit the snippet file instead). On-demand only — not auto-installed.
#
# Derived from health/.claude/hooks/safety_core_reinject.sh.
#
# Hook lessons baked in (see distillation/checklist.md section D):
# - Fires on EVERY prompt — keep the snippet SHORT. This is a re-injection
#   hook, not a place to dump a whole playbook.
# - Fail-open BY DESIGN: this hook must never block the turn. Always
#   exit 0 — a missing snippet file degrades to a stderr warning, not a
#   blocked prompt. (Contrast with a hook whose JOB is to block, which must
#   fail CLOSED — exit 2 — if its input can't be parsed.)
# - stdout here is appended to the model's context; stderr is for the human
#   at the terminal. Don't swap them.
set -euo pipefail

# --- fill in for your project ---
CORE_SNIPPET_PATH="__ABSOLUTE_PATH_TO_CORE_SNIPPET_FILE__"
# ---------------------------------

if [[ -f "$CORE_SNIPPET_PATH" ]]; then
  cat "$CORE_SNIPPET_PATH"
else
  echo "[reinject-core-at-prompt] WARNING: $CORE_SNIPPET_PATH not found" >&2
fi

exit 0

# Registration example (project .claude/settings.json):
# {
#   "hooks": {
#     "UserPromptSubmit": [
#       { "hooks": [{ "type": "command", "command": ".claude/hooks/reinject-core-at-prompt.sh" }] }
#     ]
#   }
# }
