#!/usr/bin/env bash
# TEMPLATE — SessionStart hook: unconditionally inject a file's contents into
# every new session. Copy into a project's .claude/hooks/, fill in FILE_PATH,
# and register it (see bottom). On-demand only — not auto-installed anywhere.
#
# Derived from financial/.claude/hooks/inject-memory.sh (proven pattern:
# injection beats a CLAUDE.md pointer the model can skip/forget to read).
#
# Hook lessons baked in (see distillation/checklist.md section D):
# - This hook is fail-open BY DESIGN: a missing memory/context file should
#   degrade to a warning, not block the session from starting. That is a
#   deliberate choice for SessionStart injection, not a shortcut — do NOT
#   copy this fail-open default into a hook that's supposed to block
#   (blocking hooks must fail CLOSED: exit 2 if input can't be parsed).
# - If you ever change this hook to also read tool_input (e.g. to gate on
#   which tool triggered it), the JSON payload key is `tool_input`, not
#   `input` — a common typo.
# - If you extend the matcher for this hook to also fire on Bash-based
#   writes to the injected file, remember `Write|Edit` alone misses `cp`,
#   `tee`, `>>` — include `Bash` explicitly in the matcher.
set -euo pipefail

# --- fill in for your project ---
FILE_PATH="__ABSOLUTE_PATH_TO_FILE__"   # e.g. /path/to/project/memory/MEMORY.md
LABEL="__LABEL__"                        # e.g. "Curated project memory"
# ---------------------------------

if [[ -f "$FILE_PATH" ]]; then
  echo "# ${LABEL} (auto-injected — read linked files before reasoning from handoffs)"
  echo
  cat "$FILE_PATH"
else
  echo "[inject-file-at-sessionstart] WARNING: $FILE_PATH not found" >&2
fi

# Registration example (project .claude/settings.json):
# {
#   "hooks": {
#     "SessionStart": [
#       { "hooks": [{ "type": "command", "command": ".claude/hooks/inject-file-at-sessionstart.sh" }] }
#     ]
#   }
# }
