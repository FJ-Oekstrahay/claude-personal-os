#!/bin/bash
# SessionStart hook: infra health check
# Checks memsearch/Milvus and memsearch index age.
# Always exits 0 — never blocks the session.

FAILURES=()

# --- Discord alerting setup ---
CONF="$HOME/.claude/hooks/discord-webhook.conf"
BOT_TOKEN=""
if [ -f "$CONF" ]; then
  # shellcheck disable=SC1090
  source "$CONF" 2>/dev/null
  BOT_TOKEN="${DISCORD_BOT_TOKEN:-}"
fi
# Fallback: try channels dir .env
if [ -z "$BOT_TOKEN" ]; then
  ENV_FILE="$HOME/.claude/channels/discord/.env"
  if [ -f "$ENV_FILE" ]; then
    # shellcheck disable=SC1090
    source "$ENV_FILE" 2>/dev/null
    BOT_TOKEN="${DISCORD_BOT_TOKEN:-}"
  fi
fi

LOG_CHANNEL="${DISCORD_LOG_CHANNEL_ID:-}"

send_discord_alert() {
  local msg="$1"
  if [ -n "$BOT_TOKEN" ] && [ -n "$LOG_CHANNEL" ]; then
    local payload
    payload=$(/usr/bin/jq -n --arg content "$msg" '{"content": $content}')
    /usr/bin/curl -s -o /dev/null --max-time 5 \
      -X POST "https://discord.com/api/v10/channels/${LOG_CHANNEL}/messages" \
      -H "Authorization: Bot ${BOT_TOKEN}" \
      -H "Content-Type: application/json" \
      -d "$payload" &
  fi
}

# --- Check 1: memsearch/Milvus (file-vs-directory bug check) ---
MILVUS_PATH="$HOME/.memsearch/milvus.db"
if [ -d "$MILVUS_PATH" ]; then
  : # Directory exists — normal state for MilvusLite
fi

STATE_DIR="$HOME/.claude/hooks/state"
CACHE_FILE="$STATE_DIR/infra-health-last-ok"
mkdir -p "$STATE_DIR"

SKIP_STATS=0
if [ -f "$CACHE_FILE" ]; then
  NOW_TS=$(date +%s)
  FILE_TS=$(stat -f "%m" "$CACHE_FILE" 2>/dev/null)
  if [ -n "$FILE_TS" ] && [ $(( NOW_TS - FILE_TS )) -lt 3600 ]; then
    SKIP_STATS=1
  fi
fi

if [ $SKIP_STATS -eq 0 ]; then
  STATS_OUTPUT=""
  STATS_EXIT=1
  LOCK_FAILURE=0
  for _attempt in 1 2 3; do
    STATS_OUTPUT=$(uvx --from 'memsearch[onnx]' memsearch stats 2>&1)
    STATS_EXIT=$?
    if [ $STATS_EXIT -eq 0 ] && ! echo "$STATS_OUTPUT" | grep -qi "error\|exception\|traceback\|failed"; then
      break
    fi
    # Check if this is a lock-contention failure
    if echo "$STATS_OUTPUT" | grep -qi "_acquire_lock\|acquire lock\|Failed to start MilvusLite"; then
      LOCK_FAILURE=1
      if [ $_attempt -lt 3 ]; then
        sleep $(( RANDOM % 6 + 3 ))
      fi
    else
      # Non-lock failure — don't retry
      LOCK_FAILURE=0
      break
    fi
  done

  if [ $STATS_EXIT -ne 0 ] || echo "$STATS_OUTPUT" | grep -qi "error\|exception\|traceback\|failed"; then
    if [ $LOCK_FAILURE -eq 1 ]; then
      FAILURES+=("memsearch/Milvus lock contention (3 retries)")
      send_discord_alert "[INFRA ALERT] memsearch/Milvus lock contention persisted across 3 retries — likely another active session or indexing job is holding the MilvusLite lock. This is transient; no action needed."
    else
      FAILURES+=("memsearch/Milvus stats check failed")
      send_discord_alert "[INFRA ALERT] memsearch/Milvus stats check failed. Output: $(echo "$STATS_OUTPUT" | head -3 | tr '\n' ' ')"$'\n'"Run: rm -rf ~/.memsearch/milvus.db && uvx --from 'memsearch[onnx]' memsearch index ~/.openclaw/.memsearch/memory"
    fi
  elif echo "$STATS_OUTPUT" | grep -q "^Total indexed chunks: 0"; then
    FAILURES+=("memsearch index is empty (0 chunks)")
    send_discord_alert "[INFRA ALERT] memsearch index has 0 chunks — index is empty. Run: uvx --from 'memsearch[onnx]' memsearch index ~/.memsearch/memory ~/.openclaw/.memsearch/memory ~/.openclaw/workspace/memory"
  else
    touch "$CACHE_FILE"
  fi
fi

# --- Check 2: memsearch index age ---
MEMSEARCH_DIRS=()
[ -d "$HOME/.memsearch/memory" ] && MEMSEARCH_DIRS+=("$HOME/.memsearch/memory")
[ -d "$HOME/.openclaw/.memsearch/memory" ] && MEMSEARCH_DIRS+=("$HOME/.openclaw/.memsearch/memory")

if [ ${#MEMSEARCH_DIRS[@]} -eq 0 ]; then
  FAILURES+=("memsearch memory directories not found")
  send_discord_alert "[INFRA ALERT] No memsearch memory directories found (~/.memsearch/memory or ~/.openclaw/.memsearch/memory)."
else
  # Find most recent .md file across all dirs
  MOST_RECENT=""
  for dir in "${MEMSEARCH_DIRS[@]}"; do
    CANDIDATE=$(find "$dir" -name "*.md" -type f -print0 2>/dev/null | xargs -0 ls -t 2>/dev/null | head -1)
    if [ -n "$CANDIDATE" ]; then
      if [ -z "$MOST_RECENT" ] || [ "$CANDIDATE" -nt "$MOST_RECENT" ] 2>/dev/null; then
        MOST_RECENT="$CANDIDATE"
      fi
    fi
  done

  if [ -z "$MOST_RECENT" ]; then
    FAILURES+=("memsearch: no .md files found in memory dirs")
    send_discord_alert "[INFRA ALERT] memsearch memory dirs exist but contain no .md files."
  else
    # Check if older than 48h (172800 seconds)
    NOW=$(date +%s)
    FILE_MTIME=$(stat -f "%m" "$MOST_RECENT" 2>/dev/null)
    if [ -n "$FILE_MTIME" ]; then
      AGE=$(( NOW - FILE_MTIME ))
      if [ $AGE -gt 172800 ]; then
        AGE_HOURS=$(( AGE / 3600 ))
        FAILURES+=("memsearch index may be stale (newest .md is ${AGE_HOURS}h old)")
        send_discord_alert "[INFRA ALERT] memsearch memory index may be stale — newest .md file is ${AGE_HOURS}h old (threshold: 48h)."
      fi
    fi
  fi
fi

# --- Output ---
if [ ${#FAILURES[@]} -eq 0 ]; then
  echo "[infra-health-check] All systems OK"
else
  JOINED=$(IFS="; "; echo "${FAILURES[*]}")
  echo "[infra-health-check] ALERT: ${JOINED}"
fi

exit 0
