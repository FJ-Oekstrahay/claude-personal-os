---
name: Discord launch acknowledgment
description: Always send a Discord reply when launched via Discord channel
type: feedback
---

**ALL responses when the conversation is on Discord must go via Discord reply.** This applies to every message in the conversation, not just launch acknowledgments.

**Why:** Geoff uses Discord as his primary interface. Terminal output never reaches him. He has repeated this many times — it's a firm rule, no exceptions.

**How to apply:**
1. When any message arrives via `<channel source="plugin:discord:discord" ...>`: reply via `mcp__plugin_discord_discord__reply` using that message's `chat_id`
2. Every substantive response — plans, status updates, results, questions — goes to Discord
3. Terminal text output is invisible to Geoff when he's on Discord; do not rely on it
4. Do not mix: if the conversation started on Discord, keep it on Discord for the entire session

**Implementation notes:**
- Check for `<channel source="plugin:discord:discord" ...>` in messages
- Use `mcp__plugin_discord_discord__reply` with the `chat_id` from that metadata
- This is non-negotiable — Geoff has flagged this multiple times as a recurring failure
- **Do NOT output text to the terminal as a substitute.** Even if the reply tool was called for some messages, never skip it for any message. Every single response must go to Discord.
- Common failure mode: sending terminal text thinking the reply tool was "already used" earlier in the session. It must be used for EVERY response, EVERY time.
