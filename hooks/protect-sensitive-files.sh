#!/bin/bash
# PreToolUse hook: block writes to sensitive OpenClaw files
# Claude Code passes tool info as JSON on stdin.
# Exit 2 = block (Claude sees stderr). Exit 0 = allow.

if ! command -v python3 >/dev/null 2>&1; then
  echo "BLOCKED: python3 not found — cannot parse hook input. Refusing to allow as a safety measure." >&2
  exit 2
fi

INPUT=$(cat)

# Extract tool_name and relevant field (file_path for Write/Edit, command for Bash)
read -r TOOL_NAME TARGET <<< "$(echo "$INPUT" | python3 -c "
import sys, json
try:
    d = json.load(sys.stdin)
    tool = d.get('tool_name', '')
    ti = d.get('tool_input', {})
    if tool in ('Write', 'Edit'):
        print(tool, ti.get('file_path', ''))
    elif tool == 'Bash':
        print(tool, ti.get('command', ''))
    else:
        print(tool, '')
except Exception:
    print('', '')
" 2>/dev/null)"

if [ -z "$TARGET" ]; then
  exit 0
fi

PROTECTED_PATTERNS=(
  "/credentials/"
  "/secrets/"
  "auth-profiles"
  "\.env"
  "LaunchAgents/com\.bluebubbles"
  "agents/.*/agent/IDENTITY\.md"
)

for pattern in "${PROTECTED_PATTERNS[@]}"; do
  if echo "$TARGET" | grep -qE "$pattern"; then
    echo "BLOCKED: '$TARGET' matches protected pattern '$pattern'. Propose the change and apply it manually." >&2
    exit 2
  fi
done

exit 0
