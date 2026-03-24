Ask Geoff for a short name for this handoff (e.g. "sales-automation", "infra-cleanup"). Then write the session handoff note to `~/.openclaw/workspace/HANDOFF-{name}-{YYYY-MM-DD-HHMM}.md` where `{YYYY-MM-DD-HHMM}` is the current date and time (e.g. `HANDOFF-sales-automation-2026-03-19-1432.md`). This file is the canonical handoff between Claude Code sessions.

Structure it as follows:

## Accomplished
What was done this session, with enough specificity that the next session can verify it (file paths, command output, diffs). Group by topic. Note if Geoff did something manually.

## Pending / Not Done
Items that were discussed, started, or intended but not completed. Note why (blocked, skipped, deprioritized).

## Gotchas / Surprises
Anything unexpected encountered — config quirks, command failures, behavior that differed from expectation. These prevent the next session from hitting the same walls.

## Lessons Captured
Check `~/.openclaw/workspace/memory/YYYY-MM-DD.md` logs and this session's gotchas. If anything is reusable (a procedure, a gotcha, a pattern), write or update a playbook in `~/.openclaw/workspace/memory/playbooks/`. Use existing playbooks as format reference. Add new playbooks to `~/.openclaw/workspace/memory/00_index.md`. List playbooks created/updated here, or "none needed." If any playbooks were created or updated, run `openclaw memory index --force --agent moltyjoe` to make them immediately searchable.

## Suggested First Step for Next Session
One concrete action to start with, not a list of everything. The one thing that would have the most momentum.

Rules:
- Evidence-based only. Don't claim something is done without a file path, command, or diff to back it up.
- Be specific about what Geoff did manually vs what you did.
- Update `~/.openclaw/workspace/BOARD.md` first if any board items changed status this session, then reference the board in the handoff rather than duplicating the full backlog.
- Keep it under ~60 lines. If it's longer, you're putting too much in the handoff instead of the board.
