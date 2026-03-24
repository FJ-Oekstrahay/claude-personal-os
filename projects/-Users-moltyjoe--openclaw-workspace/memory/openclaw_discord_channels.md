---
name: openclaw_discord_channels
description: OpenClaw Discord guild channels config gotcha — non-listed channels are silently denied
type: project
---

If `channels.discord.guilds.<id>.channels` has ANY entries, non-listed channels are silently denied. Adding a single channel (e.g. to disable claudo-main) blocks ALL other channels.

**Why:** OpenClaw docs: "if a guild has `channels` configured, non-listed channels are denied." This caused a 33h+ outage of all MoltyJoe Discord responses before being diagnosed.

**How to apply:** When adding/modifying guild channel entries in openclaw.json, always list ALL agent-bound channels explicitly as `"enabled": true`. The current config (2026-03-21) has all 9 agent channels listed. If a new agent/channel is added, it must be added to this block or it will be silently ignored.

Current channels block (guilds.1482078368328319163.channels):
- 1484980384860078286 (claudo-main): enabled: false — Claude Code conversation channel, not for agents
- 1482080556089868451 (moltyjoe-main): enabled: true
- 1484389023966433330 (project-board): enabled: true
- 1482080606845145219 (bob): enabled: true
- 1482080763166982305 (gerbilcheeks): enabled: true
- 1482120668920414228 (lumpy): enabled: true
- 1482080818477138076 (moltyjoe-sec): enabled: true
- 1482080849930359034 (bridgernelson): enabled: true
- 1482080882025304176 (moltyjoe-public): enabled: true
- 1482347476064403517 (moltyjoe-casual): enabled: true
