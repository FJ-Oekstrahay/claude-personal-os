#!/bin/bash
# PreToolUse + PostToolUse + Notification hook: post Claude Code activity to Discord webhooks
# PreToolUse: flush narrative text before the tool runs → LOGS_WEBHOOK_URL (early, no delay)
# PostToolUse: play-by-play mutations → LOGS_WEBHOOK_URL
# Notification: approval alerts → ALERTS_WEBHOOK_URL
#
# curl is backgrounded so this hook exits immediately (<1ms latency to Claude).
# Exit 0 always — never block Claude.

CONF="$HOME/.claude/hooks/discord-webhook.conf"
ERROR_LOG="$HOME/.claude/hooks/state/hook-errors.log"

_log_error() {
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] discord-notify: $1" >> "$ERROR_LOG" 2>/dev/null
}

# Retry/backoff wrapper for webhook (and bot-API) POSTs.
# Always call backgrounded — `post_webhook "$url" "$payload" "Label" &` — so the
# whole retry loop runs in a background subshell and never adds latency to Claude.
#   $1=url  $2=json-payload  $3=label-for-errorlog  $4=optional extra header (e.g. Authorization)
post_webhook() {
  local url="$1" payload="$2" label="$3" auth_header="$4" attempt=0 code retry
  while [ $attempt -lt 3 ]; do
    if [ -n "$auth_header" ]; then
      code=$(/usr/bin/curl -s -o /dev/null -w "%{http_code}" --max-time 8 \
        -X POST "$url" -H "Content-Type: application/json" -H "$auth_header" -d "$payload")
    else
      code=$(/usr/bin/curl -s -o /dev/null -w "%{http_code}" --max-time 8 \
        -X POST "$url" -H "Content-Type: application/json" -d "$payload")
    fi
    [ "$code" -ge 200 ] && [ "$code" -lt 300 ] 2>/dev/null && return 0
    # 429: fixed wait + jitter so concurrent backgrounded retries don't re-fire in lockstep.
    # 5xx/other: linear backoff. 4xx (non-429) won't succeed on retry but the bounded
    # loop is cheap; we still log the final failure below.
    if [ "$code" = "429" ]; then retry=$((2 + RANDOM % 2)); else retry=$((1 + attempt)); fi
    sleep "$retry"
    attempt=$((attempt + 1))
  done
  _log_error "$label: POST failed after retries HTTP $code (url=${url:0:60}...)"
  return 1
}

if [ ! -f "$CONF" ] || [ ! -r "$CONF" ]; then
  _log_error "webhook conf missing or unreadable at $CONF"
  exit 0
fi

# shellcheck disable=SC1090
if ! source "$CONF" 2>/dev/null; then
  _log_error "failed to source webhook conf at $CONF"
  exit 0
fi

# Resolve the Discord chat id for a session, in priority order:
# 1. routechatid — parent-resolved ID (set for thread sessions so they route to parent channel)
# 2. chatid — raw Discord channel from the session
# 3. DISCORD_CHAT_ID env var — per-project fallback
# Echoed (not a global) so it works inside command substitution; callers use it both
# to resolve the webhook and to label empty-resolution errors with the chat id.
_resolve_chat_id() {
  local session_id="$1"
  local state_base="$HOME/.claude/hooks/state/${session_id}"
  local chat_id=""
  for candidate_file in "${state_base}.routechatid" "${state_base}.chatid"; do
    if [ -f "$candidate_file" ]; then
      chat_id=$(tr -d '[:space:]' < "$candidate_file" 2>/dev/null)
      [ -n "$chat_id" ] && break
    fi
  done
  [ -z "$chat_id" ] && chat_id="${DISCORD_CHAT_ID:-}"
  echo "$chat_id"
}

resolve_log_webhook() {
  local session_id="$1"
  local routing_file="$HOME/.claude/hooks/discord-routing.json"
  [ -f "$routing_file" ] || { echo ""; return; }

  local chat_id
  chat_id=$(_resolve_chat_id "$session_id")
  [ -z "$chat_id" ] && { echo ""; return; }

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
    if [ -n "$url" ]; then
      echo "$url"
      return
    fi
    # routing.json maps this chat to a var, but the var is absent/empty in the conf.
    # Name it explicitly so the config gap is fixable (vs the generic downstream message).
    _log_error "missing conf var $var_name for chat $chat_id"
  fi
  echo ""
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
    if [ -z "$ACTIVE_LOG_WEBHOOK" ]; then
      # Only an actionable gap if there's a real chat to route (see PostToolUse note);
      # unbound terminal sessions have nowhere to post, so stay silent.
      PRE_CHAT_ID=$(_resolve_chat_id "$SESSION_ID")
      [ -n "$PRE_CHAT_ID" ] && _log_error "PreToolUse: ACTIVE_LOG_WEBHOOK is empty, cannot post PRE_MSG (session=$SESSION_ID chat=$PRE_CHAT_ID)"
    else
      PRE_PAYLOAD="{\"content\": $(echo "$PRE_MSG" | /usr/bin/jq -Rs .)}"
      post_webhook "$ACTIVE_LOG_WEBHOOK" "$PRE_PAYLOAD" "PreToolUse" &
    fi
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
        header = f'**Agent** → \`{safe_backtick(subagent, 40)}\`'
        if desc:
            header += f' — {safe_backtick(desc, 80)}'
        if prompt:
            prompt_str = str(prompt)
            cap = 1500
            if len(prompt_str) > cap:
                prompt_body = prompt_str[:cap] + '...'
            else:
                prompt_body = prompt_str
            print(f'{header}\n\`\`\`\n{prompt_body}\n\`\`\`')
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
    post_webhook "https://discord.com/api/v10/channels/$CHAT_ID/messages" \
      "$DIRECT_PAYLOAD" "Notification bot-API (channel=$CHAT_ID)" "Authorization: Bot $BOT_TOKEN" &
  fi

  # Also post to log webhook and ALERTS webhook as secondary channels
  ACTIVE_LOG_WEBHOOK=$(resolve_log_webhook "$SESSION")
  [ -z "$ACTIVE_LOG_WEBHOOK" ] && ACTIVE_LOG_WEBHOOK="$LOGS_WEBHOOK_URL"
  if [ -n "$ACTIVE_LOG_WEBHOOK" ]; then
    LOG_MSG=":bell: **Needs input** — session \`${SESSION_SHORT}\` in \`${CWD_SHORT}\`"
    LOG_PAYLOAD="{\"content\": $(echo "$LOG_MSG" | /usr/bin/jq -Rs .)}"
    post_webhook "$ACTIVE_LOG_WEBHOOK" "$LOG_PAYLOAD" "Notification log webhook" &
  fi
  if [ -n "$ALERTS_WEBHOOK_URL" ]; then
    ALERTS_MSG=":rotating_light: **Claude Code needs input**
Session: \`${SESSION_SHORT}\`  CWD: \`${CWD_SHORT}\`"
    ALERTS_PAYLOAD="{\"content\": $(echo "$ALERTS_MSG" | /usr/bin/jq -Rs .)}"
    post_webhook "$ALERTS_WEBHOOK_URL" "$ALERTS_PAYLOAD" "Notification alerts webhook" &
  fi

  exit 0
fi

[ -z "$MSG" ] && exit 0

if [ -z "$WEBHOOK_URL" ]; then
  # Distinguish two empty cases:
  #  - chat id empty  → session has no Discord binding (e.g. a plain terminal session).
  #    There is genuinely nowhere to post; this is expected, not a dropped message, so
  #    exit silently rather than logging an error on every tool call (the old behavior
  #    flooded hook-errors.log from unbound sessions).
  #  - chat id present → a real channel/thread not mapped in discord-routing.json (or
  #    mapping to an empty conf var). That IS an actionable gap — log it with the chat id.
  POST_CHAT_ID=$(_resolve_chat_id "$SESSION_ID")
  if [ -n "$POST_CHAT_ID" ]; then
    _log_error "PostToolUse: WEBHOOK_URL is empty, cannot post MSG (session=$SESSION_ID chat=$POST_CHAT_ID)"
  fi
  exit 0
fi

MSG_PAYLOAD="{\"content\": $(echo "$MSG" | /usr/bin/jq -Rs .)}"
post_webhook "$WEBHOOK_URL" "$MSG_PAYLOAD" "PostToolUse" &

# DONE_MSG block removed: the [agent done]/[skill done] line was redundant with the
# PostToolUse MSG line above (which already reports the tool) and added one extra POST
# per Skill/Agent call — a direct contributor to the per-webhook 429 rate.

exit 0
