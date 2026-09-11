**If this session is Discord-bound (a `<channel>` tag has appeared), try thread/channel-scoped matching first**, since a project can accumulate handoffs from several unrelated Discord threads:
1. Get the current `chat_id` from the most recent `<channel>` tag, and its parent (if any) from `~/.claude/hooks/state/$CLAUDE_CODE_SESSION_ID.parentchatid`, same as session-handoff does.
2. Search ALL handoffs, including `archive/`, for a `discord_chat_id:` line matching the current `chat_id`:
   `grep -l "discord_chat_id: <chat_id>" "$(pwd)"/handoffs/HANDOFF-*.md "$(pwd)"/handoffs/archive/HANDOFF-*.md 2>/dev/null`
3. If nothing matches, retry the same grep against `discord_parent_channel_id:` (broader — same project, different/no thread).
4. If any matches were found (step 2 or 3), sort them newest-first (by filename timestamp) and use that list in place of the full listing below — mention how many other handoffs exist outside this thread, in case the user wants those instead.
5. If nothing matches at all (including non-Discord sessions), fall back to the full listing below.

If the user invokes as 'load-handoff latest' then just load the most recent HANDOFF file from whichever list applies (thread-matched or full) — no need to show a list.
Full listing: `ls -t "$(pwd)"/handoffs/HANDOFF-*.md 2>/dev/null || ls -t ~/.openclaw/workspace/handoffs/HANDOFF-*.md 2>/dev/null`

This lists only active handoff files (not archived ones), sorted newest first — archived ones are only searched in the Discord-scoped match above, not shown here.

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
