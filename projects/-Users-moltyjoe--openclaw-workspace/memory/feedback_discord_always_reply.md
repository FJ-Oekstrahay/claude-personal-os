---
name: Always reply in Discord when launched from Discord
description: When Geoff sends a message via Discord, always reply back through Discord — not just terminal output
type: feedback
---

Always reply via the Discord reply tool when Geoff is communicating through Discord. Terminal output does not reach him. Every substantive response, status update, or result must go through `mcp__plugin_discord_discord__reply`.

**Why:** Geoff explicitly instructed this — Discord is his interface, not the terminal.

**How to apply:** Any time a Discord channel message initiates or continues a session, use reply for all responses. Don't wait until the end of a task — send progress updates too.
