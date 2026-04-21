---
name: feedback_session_start_board
description: Read the project board at session start — not optional, not skippable
type: feedback
---

Always read `~/.openclaw/workspace/projects/project-board/BOARD.md` at session start, regardless of how the session was launched or what the first question is.

**Why:** Geoff expects awareness of all active projects from the first message. Skipping the board read means answering questions about known work as if it's unknown — which signals inattention and wastes his time re-explaining context.

**How to apply:** Session start = board read. No exceptions for "simple" first messages. The board snapshot in `project_board.md` memory is a fast reference but the board itself is authoritative — re-read it if the snapshot feels stale.
