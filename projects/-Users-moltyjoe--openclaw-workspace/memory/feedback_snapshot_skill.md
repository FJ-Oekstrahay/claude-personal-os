---
name: Snapshot skill and load-handoff behavior
description: /snapshot skill exists for lightweight session saves; /load-handoff shows 5 most recent top-level files; cross-app conversation access is not possible
type: feedback
originSessionId: 9e45d924-896e-4569-97c9-1f32ea27a92f
---
`/snapshot` is a lightweight manual save — Claude picks the name from context, writes a HANDOFF-{name}-{datetime}.md to `~/.openclaw/workspace/`, and stops. No prompts, no agents, no board updates.

`/load-handoff` shows the 5 most recent top-level HANDOFF files (excluding archive/) sorted newest-first using `ls -t`. Geoff picks by number.

Claude Code cannot access conversations from the Claude iPad app, Mac app, or claude.ai. Those are cloud-siloed. Only the current session, CLAUDE.md files, and on-disk memory/handoff files are visible.

**Why:** Geoff wanted a fast "just save this" command without the full session-handoff overhead. The old load-handoff was showing all 17+ files including archived ones with no sort guarantee.

**How to apply:** Recommend `/snapshot` when Geoff wants to save context quickly. Don't suggest cross-app context access is possible.
