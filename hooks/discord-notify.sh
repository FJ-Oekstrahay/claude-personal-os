#!/bin/bash
# PostToolUse + Notification hook: post Claude Code activity to Discord webhooks
# PostToolUse: play-by-play mutations → LOGS_WEBHOOK_URL
# Notification: approval alerts → ALERTS_WEBHOOK_URL
#
# curl is backgrounded so this hook exits immediately (<1ms latency to Claude).
# Exit 0 always — never block Claude.

CONF="$HOME/.claude/hooks/discord-webhook.conf"
[ -f "$CONF" ] || exit 0

# Source conf — no set -e, malformed conf should not inject errors
# shellcheck disable=SC1090
source "$CONF" 2>/dev/null || exit 0

INPUT=$(cat)

TOOL_NAME=$(echo "$INPUT" | /usr/bin/jq -r '.tool_name // empty' 2>/dev/null)

if [ -n "$TOOL_NAME" ]; then
  # PostToolUse path — format mutation summary
  [ -z "$LOGS_WEBHOOK_URL" ] && exit 0

  MSG=$(echo "$INPUT" | python3 -c "
import sys, json

def trunc(s, n=120):
    s = str(s)
    if len(s) <= n:
        return s
    return s[:n] + '...'

def safe_backtick(s, n=120):
    s = str(s)
    if len(s) > n:
        s = s[:n] + '...'
    # Ensure no unmatched backticks
    s = s.replace('\`', \"'\")
    return s

try:
    d = json.load(sys.stdin)
    tool = d.get('tool_name', '?')
    ti = d.get('tool_input', {})
    tr = str(d.get('tool_result', ''))

    if tool == 'Write':
        path = ti.get('file_path', '?').split('/')[-1]
        lines = ti.get('content', '').count('\n') + 1
        print(f'**Write** \`{safe_backtick(path)}\` — {lines} lines')
    elif tool == 'Edit':
        path = ti.get('file_path', '?').split('/')[-1]
        print(f'**Edit** \`{safe_backtick(path)}\`')
    elif tool == 'Bash':
        cmd = safe_backtick(ti.get('command', '?'), 100)
        result_lines = tr.count('\n') + (1 if tr.strip() else 0)
        print(f'**Bash** \`{cmd}\` → {result_lines} lines')
    else:
        print(f'**{tool}**')
except Exception as e:
    print(f'**hook-error** {str(e)[:60]}')
" 2>/dev/null)

  WEBHOOK_URL="$LOGS_WEBHOOK_URL"

else
  # Notification path — approval alert
  [ -z "$ALERTS_WEBHOOK_URL" ] && exit 0

  SESSION=$(echo "$INPUT" | /usr/bin/jq -r '.session_id // "unknown"' 2>/dev/null)
  CWD_VAL=$(echo "$INPUT" | /usr/bin/jq -r '.cwd // "unknown"' 2>/dev/null)
  SESSION_SHORT="${SESSION:0:8}"
  CWD_SHORT=$(echo "$CWD_VAL" | sed 's|/Users/[^/]*/||')

  MSG=":rotating_light: **Claude Code needs input**
Session: \`${SESSION_SHORT}\`  CWD: \`${CWD_SHORT}\`"

  WEBHOOK_URL="$ALERTS_WEBHOOK_URL"
fi

[ -z "$MSG" ] && exit 0

# Background curl — exits immediately, Discord POST runs async
# --max-time 5 bounds orphan lifetime
/usr/bin/curl -s -o /dev/null --max-time 5 -X POST "$WEBHOOK_URL" \
  -H "Content-Type: application/json" \
  -d "{\"content\": $(echo "$MSG" | /usr/bin/jq -Rs .)}" &

exit 0
