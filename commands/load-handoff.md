If the user invokes as 'load-handoff latest' then just load the most recent HANDOFF file in the project's handoffs directory (no need to show a list)
Run: `ls -t "$(pwd)"/handoffs/HANDOFF-*.md 2>/dev/null || ls -t ~/.openclaw/workspace/handoffs/HANDOFF-*.md 2>/dev/null`

This lists only active handoff files (not archived ones), sorted newest first.

If no files are found, tell the user there are no handoff files in the current directory or `~/.openclaw/workspace/` and stop.

Print a numbered list of the 5 most recent results (filename only, not full path):
  1) HANDOFF-name-YYYY-MM-DD-HHMM.md
  2) HANDOFF-name-YYYY-MM-DD-HHMM.md
  ...

Ask the user to pick a number. If he enters an invalid selection, tell him the valid range and ask again.

Once he picks, read the full file. Note which directory the file came from (CWD or workspace root). Then:
1. Summarize what was accomplished
2. List what's still pending or blocked
3. Call out any gotchas or surprises
4. State the suggested first step as a concrete action
