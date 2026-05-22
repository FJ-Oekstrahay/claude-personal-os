#!/bin/bash
# SessionStart hook: pre-seed {session_id}.chatid from DISCORD_CHAT_ID env var.
#
# Tool calls (PreToolUse) can fire before the first Discord message arrives, so
# {session_id}.chatid doesn't exist yet and routing falls through to the
# hardcoded LOGS_WEBHOOK_URL fallback. Seeding it here at session start ensures
# resolve_log_webhook() routes correctly from the very first tool call.
#
# Guards:
#   - Only writes if DISCORD_CHAT_ID is set (project-scoped env var)
#   - Only writes if the file does NOT already exist (UserPromptSubmit owns it)
#   - Only writes .chatid — never .routechatid (that's thread-resolution state)

INPUT=$(cat)

SESSION_ID=$(echo "$INPUT" | /usr/bin/jq -r '.session_id // empty' 2>/dev/null)
[ -z "$SESSION_ID" ] && exit 0
[ -z "$DISCORD_CHAT_ID" ] && exit 0

STATE_DIR="$HOME/.claude/hooks/state"
CHATID_FILE="${STATE_DIR}/${SESSION_ID}.chatid"

# Only seed if the file doesn't already exist
[ -f "$CHATID_FILE" ] && exit 0

mkdir -p "$STATE_DIR"
echo "$DISCORD_CHAT_ID" > "$CHATID_FILE"

exit 0
