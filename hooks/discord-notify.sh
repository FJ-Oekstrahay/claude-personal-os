#!/bin/bash
# PreToolUse + PostToolUse + Notification hook: post Claude Code activity to Discord webhooks
# PreToolUse: flush narrative text before the tool runs → LOGS_WEBHOOK_URL (early, no delay)
# PostToolUse: play-by-play mutations → LOGS_WEBHOOK_URL
# Notification: approval alerts → ALERTS_WEBHOOK_URL
#
# curl is backgrounded so this hook exits immediately (<1ms latency to Claude).
# Exit 0 always — never block Claude.

CONF="$HOME/.claude/hooks/discord-webhook.conf"
[ -f "$CONF" ] || exit 0

# shellcheck disable=SC1090
source "$CONF" 2>/dev/null || exit 0

INPUT=$(cat)

TOOL_NAME=$(echo "$INPUT" | /usr/bin/jq -r '.tool_name // empty' 2>/dev/null)
HAS_RESPONSE=$(echo "$INPUT" | /usr/bin/jq -r 'if has("tool_response") then "yes" else "no" end' 2>/dev/null)

if [ -n "$TOOL_NAME" ] && [ "$HAS_RESPONSE" = "no" ]; then
  # PreToolUse path — flush narrative text before the tool runs so it arrives in Discord
  # immediately rather than after the (potentially slow) tool completes.
  # Must exit 0 always — never block the tool call.
  [ -z "$LOGS_WEBHOOK_URL" ] && exit 0

  SESSION_ID=$(echo "$INPUT" | /usr/bin/jq -r '.session_id // empty' 2>/dev/null)
  TRANSCRIPT_PATH=$(echo "$INPUT" | /usr/bin/jq -r '.transcript_path // empty' 2>/dev/null)

  if [ -n "$SESSION_ID" ] && [ -n "$TRANSCRIPT_PATH" ]; then
    python3 "$HOME/.claude/hooks/discord-text-extract.py" \
      "$SESSION_ID" "$TRANSCRIPT_PATH" "$LOGS_WEBHOOK_URL" 2>/dev/null &
  fi

  exit 0

elif [ -n "$TOOL_NAME" ]; then
  # PostToolUse path
  [ -z "$LOGS_WEBHOOK_URL" ] && exit 0

  # --- Extract any new text blocks from the JSONL since last processed line ---
  # (Usually finds nothing — PreToolUse already flushed them. Catches edge cases
  # where PreToolUse didn't run, e.g. hook was just added mid-session.)
  SESSION_ID=$(echo "$INPUT" | /usr/bin/jq -r '.session_id // empty' 2>/dev/null)
  TRANSCRIPT_PATH=$(echo "$INPUT" | /usr/bin/jq -r '.transcript_path // empty' 2>/dev/null)

  if [ -n "$SESSION_ID" ] && [ -n "$TRANSCRIPT_PATH" ]; then
    python3 "$HOME/.claude/hooks/discord-text-extract.py" \
      "$SESSION_ID" "$TRANSCRIPT_PATH" "$LOGS_WEBHOOK_URL" &
  fi

  # --- Tool call summary line ---
  MSG=$(echo "$INPUT" | python3 -c "
import sys, json, os

def trunc(s, n=120):
    s = str(s)
    if len(s) <= n:
        return s
    return s[:n] + '...'

def safe_backtick(s, n=120):
    s = str(s)
    if len(s) > n:
        s = s[:n] + '...'
    s = s.replace('\`', \"'\")
    return s

try:
    d = json.load(sys.stdin)
    tool = d.get('tool_name', '?')
    ti = d.get('tool_input', {})
    tr = str(d.get('tool_response', d.get('tool_result', '')))

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
    elif tool == 'Read':
        path = ti.get('file_path', '?').split('/')[-1]
        print(f'**Read** \`{safe_backtick(path)}\`')
    elif tool == 'WebFetch':
        url = safe_backtick(ti.get('url', '?'), 80)
        print(f'**WebFetch** \`{url}\`')
    elif tool == 'WebSearch':
        q = safe_backtick(ti.get('query', '?'), 80)
        print(f'**WebSearch** \`{q}\`')
    elif tool == 'Agent':
        desc = safe_backtick(ti.get('description') or ti.get('subagent_type', '?'), 80)
        print(f'**Agent** {desc}')
    elif tool.startswith('mcp__'):
        short = tool.split('__')[-1]
        try:
            import json as _json
            _ch_path = os.path.expanduser('~/.claude/hooks/discord-channels.json')
            _channels = _json.load(open(_ch_path)) if os.path.exists(_ch_path) else {}
        except Exception:
            _channels = {}
        chat_id = ti.get('chat_id')
        if chat_id is not None:
            chat_id = str(chat_id)
            log_ch = os.environ.get('DISCORD_LOG_CHANNEL_ID', '')
            if log_ch and chat_id == log_ch:
                convo_id = os.environ.get('DISCORD_CHAT_ID', '')
                label = _channels.get(convo_id, f'...{convo_id[-6:]}') if convo_id else _channels.get(chat_id, f'...{chat_id[-6:]}')
            else:
                label = _channels.get(chat_id, f'...{chat_id[-6:]}')
            print(f'**mcp:{short}** \`{label}\`')
        else:
            first_val = next((f'{k}={safe_backtick(str(v), 60)}' for k, v in ti.items() if v is not None), '')
            print(f'**mcp:{short}** {first_val}')
    elif tool.startswith('Task'):
        ref = ti.get('title') or ti.get('id') or ''
        print(f'**{tool}** {safe_backtick(str(ref), 60)}' if ref else f'**{tool}**')
    else:
        print(f'**{tool}**')
except Exception as e:
    print(f'**hook-error** {str(e)[:60]}')
" 2>/dev/null)

  WEBHOOK_URL="$LOGS_WEBHOOK_URL"

elif [ -z "$TOOL_NAME" ] && echo "$INPUT" | /usr/bin/jq -e 'has("transcript_path")' >/dev/null 2>&1; then
  # Stop hook path — turn ended. Post to Discord if a Discord message arrived this turn
  # but no reply was sent (safety net for when Claude forgets to use the reply tool).
  SESSION_ID=$(echo "$INPUT" | /usr/bin/jq -r '.session_id // empty' 2>/dev/null)
  TRANSCRIPT_PATH=$(echo "$INPUT" | /usr/bin/jq -r '.transcript_path // empty' 2>/dev/null)

  if [ -n "$SESSION_ID" ] && [ -n "$TRANSCRIPT_PATH" ]; then
    python3 "$HOME/.claude/hooks/discord-stop-check.py" \
      "$SESSION_ID" "$TRANSCRIPT_PATH" 2>/dev/null &
  fi

  exit 0

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

  # Also post a compact approval indicator to the log channel (with @mention so notification fires)
  if [ -n "$LOGS_WEBHOOK_URL" ]; then
    if [ -n "$DISCORD_ALERT_USER_ID" ]; then
      LOGS_MSG=":bell: **Needs input** — terminal session \`${SESSION_SHORT}\` in \`${CWD_SHORT}\` <@${DISCORD_ALERT_USER_ID}>"
      PAYLOAD=$(jq -n --arg content "$LOGS_MSG" --arg uid "$DISCORD_ALERT_USER_ID" \
        '{"content": $content, "allowed_mentions": {"users": [$uid]}}')
    else
      LOGS_MSG=":bell: **Needs input** — terminal session \`${SESSION_SHORT}\` in \`${CWD_SHORT}\`"
      PAYLOAD=$(echo "$LOGS_MSG" | /usr/bin/jq -Rs '{"content": .}')
    fi
    /usr/bin/curl -s -o /dev/null --max-time 5 -X POST "$LOGS_WEBHOOK_URL" \
      -H "Content-Type: application/json" \
      -d "$PAYLOAD" &
  fi
fi

[ -z "$MSG" ] && exit 0

/usr/bin/curl -s -o /dev/null --max-time 5 -X POST "$WEBHOOK_URL" \
  -H "Content-Type: application/json" \
  -d "{\"content\": $(echo "$MSG" | /usr/bin/jq -Rs .)}" &

exit 0
