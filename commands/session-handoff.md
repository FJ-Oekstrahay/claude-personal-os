Ask the user for a short name for this handoff (e.g. "sales-automation", "infra-cleanup"). Then write the session handoff note to `~/.openclaw/workspace/HANDOFF-{name}-{YYYY-MM-DD-HHMM}.md` where `{YYYY-MM-DD-HHMM}` is the current date and time (e.g. `HANDOFF-sales-automation-2026-03-19-1432.md`). This file is the canonical handoff between Claude Code sessions.

Structure it as follows:

## Accomplished
What was done this session, with enough specificity that the next session can verify it (file paths, command output, diffs). Group by topic. Note if the user did something manually.

## Pending / Not Done
Items that were discussed, started, or intended but not completed. Note why (blocked, skipped, deprioritized).

## Gotchas / Surprises
Anything unexpected encountered — config quirks, command failures, behavior that differed from expectation. These prevent the next session from hitting the same walls.

## Lessons Captured
**REQUIRED before writing this section.**

First, do a self-check from this session:
- Is project MEMORY.md (auto-memory) current? If anything was learned this session that isn't in MEMORY.md, update it now.
- Is there a playbook that should be created or updated from a pattern, gotcha, or procedure discovered this session? Name it. Write it if it takes under 5 minutes.

Then **spawn a Seymour agent** (subagent_type: "seymour", model: "haiku") with this task:

> This task has two independent jobs — do both regardless of session type.
>
> **Job 1 — OpenClaw agent learnings:** Read the agent daily logs for today and yesterday:
> - `~/.openclaw/workspace/memory/YYYY-MM-DD.md` (today)
> - `~/.openclaw/workspace/memory/YYYY-MM-DD.md` (yesterday, if exists)
> For each entry, decide: is this a reusable procedure, gotcha, or pattern worth capturing? If yes, write or update the appropriate playbook in `~/.openclaw/workspace/memory/playbooks/`. This is the only promotion path for OpenClaw agent learnings — nothing gets captured if you skip it.
>
> **Job 2 — Claude Code session learnings:** Based on the session summary below, check whether any playbooks in `~/.openclaw/workspace/memory/playbooks/` should be created or updated to capture patterns from this Claude Code session.
> [INSERT 2-3 sentence summary of session learnings before spawning — be specific about gotchas, new procedures, or decisions made]
>
> Use existing playbooks as format reference. Add any new playbooks to `~/.openclaw/workspace/memory/00_index.md`.
>
> Return: what daily log entries you found, what was promotable from each job, what playbooks you created/updated (with paths), and what you left alone.

Wait for Seymour to finish. Use its report to fill in this section. If any playbooks were created or updated, run `openclaw memory index --force --agent moltyjoe` to make them searchable.

List what Seymour found and what was done. If nothing was promotable, say so explicitly — not just "none needed."

## Suggested First Step for Next Session
One concrete action to start with, not a list of everything. The one thing that would have the most momentum.

Rules:
- Write a new handoff file — do NOT update old handoff files. Old handoffs are archives; once written they are not needed again. New sessions load the most recent handoff.
- If this session changed any system config (new/removed agents, plugins toggled, integrations added, hardware changed), update `~/.openclaw/workspace/memory/system_info.md` to reflect it and note it under Lessons Captured.
- Evidence-based only. Don't claim something is done without a file path, command, or diff to back it up.
- Be specific about what the user did manually vs what you did.
- Update `~/.openclaw/workspace/BOARD.md` first if any board items changed status this session, then reference the board in the handoff rather than duplicating the full backlog.
- Keep it under ~60 lines. If it's longer, you're putting too much in the handoff instead of the board.
- Use Obsidian wiki-links (`[[filename]]`) when referencing workspace .md files — playbooks, BOARD, AGENTS, GOVERNANCE, etc. Use the filename without extension and without path (e.g. `[[launchd_git_backup_cron]]` not the full path). This makes the handoff navigable in Obsidian.

After writing the handoff, auto-archive old ones:
- Run: `find ~/.openclaw/workspace -maxdepth 1 -name 'HANDOFF-*.md' -mtime +3 -exec mv {} ~/.openclaw/workspace/handoffs/archive/ \;`
- mkdir -p the archive dir first if needed.
- Report how many were archived (if any). Don't ask for confirmation — this is routine cleanup.
