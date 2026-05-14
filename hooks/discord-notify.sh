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

resolve_log_webhook() {
  local session_id="$1"
  local routing_file="$HOME/.claude/hooks/discord-routing.json"
  [ -f "$routing_file" ] || { echo "$LOGS_WEBHOOK_URL"; return; }

  # Try routing IDs in priority order:
  # 1. routechatid — parent-resolved ID (set for thread sessions so they route to parent channel)
  # 2. chatid — raw Discord channel from the session
  # 3. DISCORD_CHAT_ID env var — per-project fallback
  local state_base="$HOME/.claude/hooks/state/${session_id}"
  local chat_id=""
  for candidate_file in "${state_base}.routechatid" "${state_base}.chatid"; do
    if [ -f "$candidate_file" ]; then
      chat_id=$(tr -d '[:space:]' < "$candidate_file" 2>/dev/null)
      [ -n "$chat_id" ] && break
    fi
  done
  [ -z "$chat_id" ] && chat_id="${DISCORD_CHAT_ID:-}"
  [ -z "$chat_id" ] && { echo "$LOGS_WEBHOOK_URL"; return; }

  local var_name
  var_name=$(python3 -c "
import json, sys
try:
    routing = json.load(open(sys.argv[1]))
    print(routing.get(sys.argv[2], ''))
except Exception:
    pass
" "$routing_file" "$chat_id" 2>/dev/null)

  if [ -n "$var_name" ]; then
    local url="${!var_name}"
    [ -n "$url" ] && echo "$url" && return
  fi
  echo "$LOGS_WEBHOOK_URL"
}

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
    ACTIVE_LOG_WEBHOOK=$(resolve_log_webhook "$SESSION_ID")
    python3 "$HOME/.claude/hooks/discord-text-extract.py" \
      "$SESSION_ID" "$TRANSCRIPT_PATH" "$ACTIVE_LOG_WEBHOOK" 2>/dev/null &
  fi

  # Immediate PreToolUse announcements for notable tools
  PRE_MSG=$(echo "$INPUT" | python3 -c "
import sys, json

def safe_backtick(s, n=120):
    s = str(s)
    if len(s) > n:
        s = s[:n] + '...'
    s = s.replace('\`', \"'\")
    return s

try:
    d = json.load(sys.stdin)
    tool = d.get('tool_name', '')
    ti = d.get('tool_input', {})

    if tool == 'Skill':
        skill_name = ti.get('skill', '?')
        args_val = ti.get('args', '')
        if args_val:
            args_short = safe_backtick(str(args_val), 80)
            print(f'⚡ **Skill:** \`{safe_backtick(skill_name)}\` — args={args_short}')
        else:
            print(f'⚡ **Skill:** \`{safe_backtick(skill_name)}\`')
    elif tool == 'Agent':
        desc = ti.get('description', '?')
        subagent_type = ti.get('subagent_type', 'general') or 'general'
        print(f'🤖 **Agent dispatch:** \`{safe_backtick(desc, 80)}\` [{safe_backtick(subagent_type, 30)}]')
    elif tool == 'mcp__plugin_discord_discord__reply':
        print('💬 **Discord reply** queued')
except Exception:
    pass
" 2>/dev/null)

  if [ -n "$PRE_MSG" ]; then
    if [ -z "$ACTIVE_LOG_WEBHOOK" ]; then
      ACTIVE_LOG_WEBHOOK=$(resolve_log_webhook "$SESSION_ID")
    fi
    /usr/bin/curl -s -o /dev/null --max-time 5 -X POST "$ACTIVE_LOG_WEBHOOK" \
      -H "Content-Type: application/json" \
      -d "{\"content\": $(echo "$PRE_MSG" | /usr/bin/jq -Rs .)}" &
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
      "$SESSION_ID" "$TRANSCRIPT_PATH" "$(resolve_log_webhook "$SESSION_ID")" &
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
    elif tool == 'Skill':
        skill_name = ti.get('skill', '?')
        print(f'✅ **Skill done:** \`{safe_backtick(skill_name)}\`')
    elif tool == 'Agent':
        subagent = ti.get('subagent_type', '?')
        desc = ti.get('description', '')
        prompt = ti.get('prompt', '')
        header = f'**Agent** → `{safe_backtick(subagent, 40)}`'
        if desc:
            header += f' — {safe_backtick(desc, 80)}'
        if prompt:
            prompt_str = str(prompt)
            cap = 1500
            if len(prompt_str) > cap:
                prompt_body = prompt_str[:cap] + '…'
            else:
                prompt_body = prompt_str
            print(f'{header}\n```\n{prompt_body}\n```')
        else:
            print(header)
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
                label = _channels.get(convo_id) if convo_id else _channels.get(chat_id)
            else:
                label = _channels.get(chat_id)
            if not label:
                # chat_id may be a thread (dynamic ID not in channels map); fall back to session state
                _session_id = d.get('session_id', '')
                if _session_id:
                    _state_base = os.path.expanduser(f'~/.claude/hooks/state/{_session_id}')
                    for _sfx in ('routechatid', 'chatid'):
                        try:
                            _stored = open(f'{_state_base}.{_sfx}').read().strip()
                            if _stored in _channels:
                                label = _channels[_stored]
                                break
                        except Exception:
                            pass
            if not label:
                label = f'...{chat_id[-6:]}'
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

  WEBHOOK_URL=$(resolve_log_webhook "$SESSION_ID")

elif [ -z "$TOOL_NAME" ] && echo "$INPUT" | /usr/bin/jq -e 'has("transcript_path")' >/dev/null 2>&1; then
  # Stop hook path — turn ended. Post to Discord if a Discord message arrived this turn
  # but no reply was sent (safety net for when Claude forgets to use the reply tool).
  SESSION_ID=$(echo "$INPUT" | /usr/bin/jq -r '.session_id // empty' 2>/dev/null)
  TRANSCRIPT_PATH=$(echo "$INPUT" | /usr/bin/jq -r '.transcript_path // empty' 2>/dev/null)

  if [ -n "$SESSION_ID" ] && [ -n "$TRANSCRIPT_PATH" ]; then
    # Flush any trailing narrative text (after the last tool call) to the log webhook.
    # text-extract advances the state file so stop-check doesn't double-post.
    STOP_LOG_WEBHOOK=$(resolve_log_webhook "$SESSION_ID")
    if [ -n "$STOP_LOG_WEBHOOK" ]; then
      python3 "$HOME/.claude/hooks/discord-text-extract.py" \
        "$SESSION_ID" "$TRANSCRIPT_PATH" "$STOP_LOG_WEBHOOK" 2>/dev/null &
    fi
    python3 "$HOME/.claude/hooks/discord-stop-check.py" \
      "$SESSION_ID" "$TRANSCRIPT_PATH" 2>/dev/null &
  fi

  exit 0

else
  # Notification path — approval alert
  SESSION=$(echo "$INPUT" | /usr/bin/jq -r '.session_id // "unknown"' 2>/dev/null)
  CWD_VAL=$(echo "$INPUT" | /usr/bin/jq -r '.cwd // "unknown"' 2>/dev/null)
  SESSION_SHORT="${SESSION:0:8}"
  CWD_SHORT=$(echo "$CWD_VAL" | sed 's|/Users/[^/]*/||')

  # Post directly to the source discussion channel via bot API (with @mention)
  CHATID_FILE="$HOME/.claude/hooks/state/${SESSION}.chatid"
  BOT_TOKEN=$(python3 -c "
import os
for path in ['~/.claude/hooks/discord-webhook.conf', '~/.claude/channels/discord/.env']:
    try:
        for line in open(os.path.expanduser(path)).read().splitlines():
            if line.startswith('DISCORD_BOT_TOKEN='):
                print(line.split('=',1)[1].strip().strip('\"').strip(\"'\"))
                exit()
    except Exception:
        pass
" 2>/dev/null)

  if [ -f "$CHATID_FILE" ] && [ -n "$BOT_TOKEN" ]; then
    CHAT_ID=$(cat "$CHATID_FILE")
    if [ -n "$DISCORD_ALERT_USER_ID" ]; then
      DIRECT_MSG=":bell: **Claude Code needs your approval** — check terminal <@${DISCORD_ALERT_USER_ID}>"
      DIRECT_PAYLOAD=$(/usr/bin/jq -n --arg content "$DIRECT_MSG" --arg uid "$DISCORD_ALERT_USER_ID" \
        '{"content": $content, "allowed_mentions": {"users": [$uid]}}')
    else
      DIRECT_MSG=":bell: **Claude Code needs approval** — check terminal"
      DIRECT_PAYLOAD=$(echo "$DIRECT_MSG" | /usr/bin/jq -Rs '{"content": .}')
    fi
    /usr/bin/curl -s -o /dev/null --max-time 5 \
      -X POST "https://discord.com/api/v10/channels/$CHAT_ID/messages" \
      -H "Authorization: Bot $BOT_TOKEN" \
      -H "Content-Type: application/json" \
      -d "$DIRECT_PAYLOAD" &
  fi

  # Also post to log webhook and ALERTS webhook as secondary channels
  ACTIVE_LOG_WEBHOOK=$(resolve_log_webhook "$SESSION")
  [ -z "$ACTIVE_LOG_WEBHOOK" ] && ACTIVE_LOG_WEBHOOK="$LOGS_WEBHOOK_URL"
  if [ -n "$ACTIVE_LOG_WEBHOOK" ]; then
    LOG_MSG=":bell: **Needs input** — session \`${SESSION_SHORT}\` in \`${CWD_SHORT}\`"
    /usr/bin/curl -s -o /dev/null --max-time 5 -X POST "$ACTIVE_LOG_WEBHOOK" \
      -H "Content-Type: application/json" \
      -d "{\"content\": $(echo "$LOG_MSG" | /usr/bin/jq -Rs .)}" &
  fi
  if [ -n "$ALERTS_WEBHOOK_URL" ]; then
    ALERTS_MSG=":rotating_light: **Claude Code needs input**
Session: \`${SESSION_SHORT}\`  CWD: \`${CWD_SHORT}\`"
    /usr/bin/curl -s -o /dev/null --max-time 5 -X POST "$ALERTS_WEBHOOK_URL" \
      -H "Content-Type: application/json" \
      -d "{\"content\": $(echo "$ALERTS_MSG" | /usr/bin/jq -Rs .)}" &
  fi

  exit 0
fi

[ -z "$MSG" ] && exit 0

/usr/bin/curl -s -o /dev/null --max-time 5 -X POST "$WEBHOOK_URL" \
  -H "Content-Type: application/json" \
  -d "{\"content\": $(echo "$MSG" | /usr/bin/jq -Rs .)}" &

# PostToolUse completion announcements for Skill and Agent tools
DONE_MSG=$(echo "$INPUT" | python3 -c "
import sys, json

def safe_backtick(s, n=120):
    s = str(s)
    if len(s) > n:
        s = s[:n] + '...'
    s = s.replace('\`', \"'\")
    return s

try:
    d = json.load(sys.stdin)
    tool = d.get('tool_name', '')
    ti = d.get('tool_input', {})

    if tool == 'Skill':
        skill_name = ti.get('skill', '?')
        args_val = ti.get('args', '')
        if args_val:
            args_short = safe_backtick(str(args_val), 80)
            print(f'✅ **Skill done:** \`{safe_backtick(skill_name)}\` — args={args_short}')
        else:
            print(f'✅ **Skill done:** \`{safe_backtick(skill_name)}\`')
    elif tool == 'Agent':
        desc = ti.get('description', '') or ti.get('subagent_type', '?')
        print(f'✅ **Agent done:** \`{safe_backtick(desc, 80)}\`')
except Exception:
    pass
" 2>/dev/null)

if [ -n "$DONE_MSG" ]; then
  /usr/bin/curl -s -o /dev/null --max-time 5 -X POST "$WEBHOOK_URL" \
    -H "Content-Type: application/json" \
    -d "{\"content\": $(echo "$DONE_MSG" | /usr/bin/jq -Rs .)}" &
fi

exit 0
