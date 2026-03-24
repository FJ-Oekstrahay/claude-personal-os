Glob `~/.openclaw/workspace/HANDOFF-*.md`. The Glob tool returns results sorted by modification time (newest first) — use that order as-is, do not re-sort.

If no files are found, tell Geoff there are no handoff files in `~/.openclaw/workspace/` and stop.

Print a numbered list of the files found, using just the filename (not full path), formatted as:
  1) HANDOFF-name-YYYY-MM-DD-HHMM.md
  2) HANDOFF-name-YYYY-MM-DD-HHMM.md
  ...

Ask Geoff to pick a number. If he enters an invalid selection (out of range, non-numeric, or blank), tell him the valid range and ask again.

Once he picks, read the full file. Then:
1. Summarize what was accomplished
2. List what's still pending or blocked
3. Call out any gotchas or surprises
4. State the suggested first step as a concrete action

Do not act on the handoff content until Geoff confirms his selection.

After presenting the handoff summary, fetch recent Discord history for additional context:
- Call fetch_messages with chat_id `1484725914263617666` (Geoff's Claude Code chat channel), limit 30
- Scan the messages for anything relevant to the current session context (ongoing tasks, decisions, questions asked)
- If anything relevant is found, briefly note it as "Recent Discord context:" after the handoff summary
- If nothing relevant, skip the Discord section silently
