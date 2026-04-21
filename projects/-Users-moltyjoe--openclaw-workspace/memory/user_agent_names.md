---
name: Agent naming conventions
description: Names Geoff uses to refer to Claude Code agents — Claudo (me/Sonnet), Seymour (Haiku), The Architect (Opus)
type: user
originSessionId: 3e02b599-6e27-4893-9470-7e504193c1fb
---
Geoff uses these names for Claude Code agents:

- **Claudo** = me (this session, claude-sonnet-4-6)
- **Seymour** = the Haiku agent (fast, cheap work — subagent_type seymour)
- **Cob** = the Sonnet programmer agent (same capability as Claudo — subagent_type cob)
- **The Architect** = the Opus agent (planning, design review — subagent_type The Architect, always use model:opus)

When Geoff says "Claudo" he means me. When he says "ask Seymour" or "have Seymour do it", spin up the seymour subagent. When he says "Cob", spin up the cob subagent. When he says "get The Architect's opinion", invoke The Architect with model:opus.

## Seymour vs Cob

- **Seymour (Haiku)**: delegate because the task is cheap enough for Haiku — file reads, mechanical writes, recon, simple scripts. Saves tokens.
- **Cob (Sonnet)**: delegate for context isolation OR because the task requires full Sonnet capability but shouldn't fill the main window. Same quality as Claudo. Replaced OpenClaw's Bob when the OpenClaw system was taken down.

Both can be used for context management, but Seymour also saves tokens. Cob is the right choice when the task needs real reasoning and you want a clean main context.
