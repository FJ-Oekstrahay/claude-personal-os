---
name: Log permission blockers to project board
description: When hitting a permission wall, log it to the board's Permission Blockers section instead of just asking Geoff inline
type: feedback
---

When Claude Code hits a permission blocker mid-task, log it to the **Permission Blockers** section of `~/.openclaw/workspace/projects/project-board/BOARD.md` so it can be resolved in a dedicated `/update-config` session.

**Why:** Permission interruptions are frustrating mid-task. Geoff usually allows the thing anyway — better to collect blockers and fix them in batch than to break flow every time.

**How to apply:** When asking Geoff for approval on a tool call or permission:
1. Handle it exactly as normal — ask, wait, proceed based on his response.
2. Also log the blocker to the Permission Blockers section of the board so it can be resolved in a batch `/update-config` session.
