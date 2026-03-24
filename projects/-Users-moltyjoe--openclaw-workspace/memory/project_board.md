---
name: project_board
description: Location and purpose of the project board — tracks all active, blocked, and someday work across OpenClaw, dev projects, and family projects
type: project
---

The project board lives at `~/.openclaw/workspace/projects/project-board/BOARD.md`.

It tracks all active work across:
- **Infrastructure** (OpenClaw ops, token migration, gateway config)
- **Development & Sales Automation** (TalonForge, sales pipeline)
- **Family** (Ethan schoolwork, Traveloceros)

**Why:** Geoff wants a persistent, cross-session status view updated from any chat. Goal is eventually a rendered HTML version.

**How to apply:** When starting a session or wrapping up, read `project-board/BOARD.md` to orient on current state. When work on any tracked project completes or changes status, update the board. When `/session-handoff` is run, update the board as part of that flow. Always update `_Last updated:` date at the top.
