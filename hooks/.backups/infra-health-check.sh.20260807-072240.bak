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

# --- Check 2: memsearch index freshness (last-reindex stamp) ---
# The daily reindex (com.geoff.memsearch-reindex -> memsearch-reindex.sh) writes
# this stamp on success; its mtime = when the index last actually refreshed. This
# measures index freshness directly, instead of statting orphan .memsearch dirs
# that Claude never writes to (the old, permanently-firing proxy).
MEMSEARCH_STAMP="$HOME/.claude/hooks/state/memsearch-last-reindex"
if [ ! -f "$MEMSEARCH_STAMP" ]; then
  FAILURES+=("memsearch reindex stamp missing — daily reindex may not be running")
  send_discord_alert "[INFRA ALERT] memsearch last-reindex stamp missing ($MEMSEARCH_STAMP). Is com.geoff.memsearch-reindex loaded? Check: launchctl list | grep memsearch"
else
  NOW=$(date +%s)
  STAMP_MTIME=$(stat -f "%m" "$MEMSEARCH_STAMP" 2>/dev/null)
  if [ -n "$STAMP_MTIME" ]; then
    AGE=$(( NOW - STAMP_MTIME ))
    if [ $AGE -gt 172800 ]; then
      AGE_HOURS=$(( AGE / 3600 ))
      FAILURES+=("memsearch index stale — last reindex ${AGE_HOURS}h ago")
      send_discord_alert "[INFRA ALERT] memsearch index stale — last successful reindex was ${AGE_HOURS}h ago (threshold: 48h). Check com.geoff.memsearch-reindex."
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
