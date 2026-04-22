#!/bin/bash
# Sanitized for public sharing — replace variables in the Config section before use.
#
# sync-to-public.sh
#
# Syncs ~/.claude to a public GitHub repo.
# Personal info is redacted and sensitive directories are excluded.
#
# Strategy: maintain a persistent git working dir at
#   $HOME/.openclaw/public-sync/claude-personal-os/
# On each run: pull latest, wipe + re-copy sanitized content, commit, push.
#
# Runs from cron as part of the nightly backup job.

set -euo pipefail

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
SOURCE_DIR="$HOME/.claude"
SYNC_DIR="$HOME/.openclaw/public-sync/claude-personal-os"
EXCLUDE_FILE="$HOME/.openclaw/bin/claude-public-exclude.txt"
PUBLIC_REMOTE="https://github.com/YOUR_GITHUB_USERNAME/claude-personal-os.git"
LOG="$HOME/.openclaw/logs/sync-claude-public.log"
ALERT="$HOME/.openclaw/workspace/BACKUP-ALERT.md"

# ---------------------------------------------------------------------------
# Logging helpers
# ---------------------------------------------------------------------------
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" >> "$LOG"
}

fail() {
    local msg="$*"
    log "ERROR: $msg"
    # Append to alert file so the agent system or a human notices
    {
        echo ""
        echo "## sync-claude-to-public failure — $(date '+%Y-%m-%d %H:%M:%S')"
        echo ""
        echo "**Error:** $msg"
        echo ""
    } >> "$ALERT"
    exit 1
}

# ---------------------------------------------------------------------------
# Trap: log any unexpected exit
# ---------------------------------------------------------------------------
trap 'status=$?; [ $status -ne 0 ] && fail "Script exited unexpectedly (exit $status)"' EXIT

log "Starting sync-claude-to-public"

# ---------------------------------------------------------------------------
# 1. Ensure the persistent sync directory exists and is a valid git repo
# ---------------------------------------------------------------------------
if [ ! -d "$SYNC_DIR/.git" ]; then
    log "No existing clone found — cloning public repo"
    mkdir -p "$(dirname "$SYNC_DIR")"
    git clone "$PUBLIC_REMOTE" "$SYNC_DIR" >> "$LOG" 2>&1 || fail "git clone failed"
else
    # Always assert the correct remote before pulling (guards against remote drift)
    git -C "$SYNC_DIR" remote set-url origin "$PUBLIC_REMOTE" 2>/dev/null || true
    log "Pulling latest from origin"
    git -C "$SYNC_DIR" pull --rebase origin main >> "$LOG" 2>&1 || {
        log "Pull failed (empty repo or diverged) — resetting to current remote state"
        git -C "$SYNC_DIR" fetch origin >> "$LOG" 2>&1 || true
        git -C "$SYNC_DIR" reset --hard origin/main >> "$LOG" 2>&1 || true
    }
fi

# ---------------------------------------------------------------------------
# 2. Wipe all tracked content from the working dir (keep .git)
# ---------------------------------------------------------------------------
log "Wiping working directory content"
find "$SYNC_DIR" -mindepth 1 -maxdepth 1 ! -name '.git' -exec rm -rf {} +

# ---------------------------------------------------------------------------
# 3. rsync sanitized content from ~/.claude
# ---------------------------------------------------------------------------
log "rsync from $SOURCE_DIR"
rsync -a \
    --exclude-from="$EXCLUDE_FILE" \
    "$SOURCE_DIR/" "$SYNC_DIR/" >> "$LOG" 2>&1 || fail "rsync failed"

# ---------------------------------------------------------------------------
# 4. Use public-facing CLAUDE.md
# ---------------------------------------------------------------------------
# Use public-facing CLAUDE.md instead of redacting the internal one
if [ -f "$SOURCE_DIR/CLAUDE.public.md" ]; then
    log "Using CLAUDE.public.md as public CLAUDE.md"
    cp "$SOURCE_DIR/CLAUDE.public.md" "$SYNC_DIR/CLAUDE.md"
elif [ -f "$SYNC_DIR/CLAUDE.md" ]; then
    log "CLAUDE.public.md not found — redacting internal CLAUDE.md"
    sed -i '' \
        -e 's/your\.real\.email@example\.com/your@email.com/g' \
        -e 's/Real Name/FJ Oekstrahay/g' \
        "$SYNC_DIR/CLAUDE.md" || fail "CLAUDE.md redaction failed"
fi

# ---------------------------------------------------------------------------
# 5a. Global redaction pass — all .md files
# ---------------------------------------------------------------------------
log "Redacting personal info from all .md files"
while IFS= read -r -d '' f; do
    sed -i '' \
        -e 's/your\.real\.email@example\.com/your@email.com/g' \
        -e 's/Real Name/FJ Oekstrahay/g' \
        -e 's/18789/<gateway-port>/g' \
        "$f" 2>/dev/null || true
done < <(find "$SYNC_DIR" -name "*.md" -print0)

# ---------------------------------------------------------------------------
# 5b. Redact settings.json
# ---------------------------------------------------------------------------
if [ -f "$SYNC_DIR/settings.json" ]; then
    log "Redacting settings.json"
    # Email and name substitutions
    sed -i '' \
        -e 's/your\.real\.email@example\.com/your@email.com/g' \
        -e 's/Real Name/FJ Oekstrahay/g' \
        "$SYNC_DIR/settings.json" || fail "settings.json redaction (names) failed"

    # Redact any line whose key contains token, key, password, or secret
    # Matches JSON patterns like:  "someToken": "actual-value",
    sed -i '' \
        -E 's/("(token|key|password|secret)[^"]*"[[:space:]]*:[[:space:]]*)"[^"]*"/\1"<redacted>"/gI' \
        "$SYNC_DIR/settings.json" || fail "settings.json redaction (secrets) failed"
fi

# ---------------------------------------------------------------------------
# 6. Commit and push if there are changes
# ---------------------------------------------------------------------------
git -C "$SYNC_DIR" add -A

if git -C "$SYNC_DIR" diff --cached --quiet; then
    log "No changes to commit — public repo is already up to date"
    # Disarm the trap before clean exit
    trap - EXIT
    exit 0
fi

COMMIT_MSG="sync: $(date '+%Y-%m-%d')"
log "Committing: $COMMIT_MSG"
git -C "$SYNC_DIR" commit -m "$COMMIT_MSG" >> "$LOG" 2>&1 || fail "git commit failed"

log "Pushing to origin main"
git -C "$SYNC_DIR" push --force origin main >> "$LOG" 2>&1 || fail "git push failed"

log "Done — sync complete"

# Disarm the trap on clean exit
trap - EXIT
