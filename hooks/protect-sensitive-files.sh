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
)

for pattern in "${PROTECTED_PATTERNS[@]}"; do
  if echo "$TARGET" | grep -qE "$pattern"; then
    echo "BLOCKED: '$TARGET' matches protected pattern '$pattern'. Propose the change and apply it manually." >&2
    exit 2
  fi
done

# For Write and Edit, also scan content for bot token patterns
# Exception: discord-webhook.conf is the designated token store — allow credential writes there
if [ "$TOOL_NAME" = "Write" ] || [ "$TOOL_NAME" = "Edit" ]; then
  if echo "$TARGET" | grep -q 'discord-webhook.conf$'; then
    exit 0
  fi
  TOKEN_FOUND=$(echo "$INPUT" | python3 -c "
import sys, json, re
try:
    d = json.load(sys.stdin)
    ti = d.get('tool_input', {})
    content = ti.get('content', '') or ti.get('new_string', '')
    PLACEHOLDER_TERMS = ['YOUR_', 'PLACEHOLDER', 'EXAMPLE', 'TOKEN_HERE', 'xxx', '...', 'YOUR_BOT', 'discord.com/api/webhooks']
    def is_placeholder(s):
        return any(t in s for t in PLACEHOLDER_TERMS)
    patterns = [
        (r'DISCORD_BOT_TOKEN\s*=\s*[A-Za-z0-9._-]{20,}', 'DISCORD_BOT_TOKEN'),
        (r'sk-[A-Za-z0-9]{48,}', 'OpenAI API key'),
        (r'sk-ant-[A-Za-z0-9_-]{40,}', 'Anthropic API key'),
        (r'[A-Za-z0-9_-]{24}\.[A-Za-z0-9_-]{6}\.[A-Za-z0-9_-]{27,}', 'Discord bot token'),
        (r'https://discord\.com/api/webhooks/\d+/[A-Za-z0-9_-]{60,}', 'Discord webhook URL'),
    ]
    for pattern, label in patterns:
        m = re.search(pattern, content)
        if m and not is_placeholder(m.group(0)):
            print(f'blocked:{label}')
            break
except Exception:
    pass
" 2>/dev/null)

  if [ "$TOKEN_FOUND" != "" ]; then
    echo "BLOCKED: Content appears to contain a sensitive credential ($TOKEN_FOUND). Store tokens in discord-webhook.conf, not source files." >&2
    exit 2
  fi
fi

# For Bash, scan the command string for embedded webhook URLs and bot token assignments
if [ "$TOOL_NAME" = "Bash" ]; then
  BASH_TOKEN_FOUND=$(echo "$INPUT" | python3 -c "
import sys, json, re
try:
    d = json.load(sys.stdin)
    ti = d.get('tool_input', {})
    command = ti.get('command', '')
    PLACEHOLDER_TERMS = ['YOUR_', 'PLACEHOLDER', 'EXAMPLE', 'TOKEN_HERE', 'xxx', '...', 'YOUR_BOT', 'discord.com/api/webhooks']
    def is_placeholder(s):
        return any(t in s for t in PLACEHOLDER_TERMS)
    patterns = [
        (r'https://discord\.com/api/webhooks/\d+/[A-Za-z0-9_-]{60,}', 'Discord webhook URL'),
        (r'DISCORD_BOT_TOKEN\s*=\s*[A-Za-z0-9._-]{20,}', 'DISCORD_BOT_TOKEN'),
    ]
    for pattern, label in patterns:
        m = re.search(pattern, command)
        if m and not is_placeholder(m.group(0)):
            print(f'blocked:{label}')
            break
except Exception:
    pass
" 2>/dev/null)

  if [ "$BASH_TOKEN_FOUND" != "" ]; then
    echo "BLOCKED: Bash command appears to contain a sensitive credential ($BASH_TOKEN_FOUND). Store tokens in discord-webhook.conf, not source files." >&2
    exit 2
  fi
fi

exit 0
