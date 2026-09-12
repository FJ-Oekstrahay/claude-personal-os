#!/bin/bash
# memsearch-reindex.sh — rebuild the memsearch/Milvus index over every dir Claude
# actually writes memory to, and stamp the time on success.
#
# WHY: Claude writes memory to ~/.openclaw/workspace/memory and
# ~/.claude/projects/*/memory, but memsearch's index was frozen because nothing
# re-indexed those dirs. This runs daily via launchd (com.geoff.memsearch-reindex)
# so recall stays fresh. Canonical dir set = the user's decision 2026-07-07
# ("index everything including projects"): the two legacy .memsearch dirs +
# workspace memory + every project auto-memory dir (globbed so new projects are
# picked up automatically).
#
# The STAMP file's mtime is the single source of truth for "when did the index
# last successfully refresh" — infra-health-check.sh Check 2 reads it.
# Pure shell + uvx; no API tokens (fits the Max plan).

set -u
STATE_DIR="$HOME/.claude/hooks/state"
STAMP="$STATE_DIR/memsearch-last-reindex"
LOG="$STATE_DIR/memsearch-reindex.log"
LOCK="$STATE_DIR/memsearch-reindex.lock"
mkdir -p "$STATE_DIR"

# launchd runs with a minimal PATH — resolve uvx explicitly.
UVX="$HOME/.local/bin/uvx"
[ -x "$UVX" ] || UVX="$(command -v uvx 2>/dev/null)"

# Under launchd's minimal env, uvx's interpreter discovery falls back to
# /usr/bin/python3 (Apple's system stub, 3.9.6) instead of the Homebrew
# python3.10+ available interactively. memsearch[onnx] requires >=3.10, so
# every scheduled run failed silently from 2026-07-28 to 2026-09-11 — see
# playbook memsearch_launchd_python_version_mismatch. Pin a version range
# (not an exact version) so this survives either machine's Homebrew python
# being upgraded independently.
UVX_PYTHON='>=3.10'

log() { echo "$(TZ=America/New_York date '+%F %T') $*" >> "$LOG"; }

# Single-writer guard: mkdir is atomic. Skip (not fail) if a run is in progress —
# a piled-up second run would only fight the MilvusLite single-writer lock.
if ! mkdir "$LOCK" 2>/dev/null; then
  log "SKIP: another reindex holds the lock ($LOCK)"
  exit 0
fi
trap 'rmdir "$LOCK" 2>/dev/null' EXIT

if [ -z "$UVX" ]; then
  log "ERROR: uvx not found (looked at ~/.local/bin/uvx and PATH)"
  exit 1
fi

# Build the canonical dir set.
dirs=()
[ -d "$HOME/.memsearch/memory" ]          && dirs+=("$HOME/.memsearch/memory")
[ -d "$HOME/.openclaw/.memsearch/memory" ] && dirs+=("$HOME/.openclaw/.memsearch/memory")
[ -d "$HOME/.openclaw/workspace/memory" ]  && dirs+=("$HOME/.openclaw/workspace/memory")
for d in "$HOME"/.claude/projects/*/memory; do
  [ -d "$d" ] && dirs+=("$d")
done

if [ ${#dirs[@]} -eq 0 ]; then
  log "ERROR: no memory dirs found — nothing to index"
  exit 1
fi

# Keep the log from growing unbounded: retain only the last ~200 lines.
if [ -f "$LOG" ] && [ "$(wc -l < "$LOG" 2>/dev/null || echo 0)" -gt 400 ]; then
  tail -200 "$LOG" > "$LOG.tmp" && mv "$LOG.tmp" "$LOG"
fi

log "START reindex over ${#dirs[@]} dirs"
if "$UVX" --python "$UVX_PYTHON" --from 'memsearch[onnx]' memsearch index "${dirs[@]}" >> "$LOG" 2>&1; then
  # Stamp success — mtime is what the health check measures.
  TZ=America/New_York date '+%F %T %z' > "$STAMP"
  # Log the mtime we actually observe right after the write, plus wall clock,
  # so a later "stale index" alert can be checked against this append-only
  # record instead of trusting the write happened (2026-08-03 stamp-revert
  # incident: the write silently failed to persist for 5 days and this log
  # kept saying "OK" regardless).
  log "OK reindex complete — stamped $STAMP (observed mtime $(stat -f '%Sm' "$STAMP" 2>/dev/null), wall clock $(date))"
  exit 0
else
  rc=$?
  log "ERROR reindex failed rc=$rc — stamp NOT updated"
  exit "$rc"
fi
