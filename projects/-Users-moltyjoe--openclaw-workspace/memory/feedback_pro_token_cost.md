---
name: Pro token cost awareness
description: Treat Claude Pro tokens as a real budget — Geoff can get rate-limited for hours if quota runs out
type: feedback
---

Pro plan tokens are a real cost, not "free." Geoff can hit the Claude Pro rate limit and get locked out for hours.

**Two separate budgets:**
- Pro plan tokens — everything in a Claude Code session (file reads, responses, shell output). Rate-limited.
- API dollars — TalonForge `run.py` and other direct Anthropic API calls. Billed to API key, does NOT touch Pro quota.

**What burns Pro tokens:**
- Reading files (input)
- Long responses (output)
- Shell output fed back as context
- Full conversation context re-sent each turn

**Why:** If Geoff runs out of Pro tokens, he's locked out for hours.

**How to apply:**
- Skip file reads that aren't strictly necessary
- Give shorter answers when the question is simple
- Avoid exploratory multi-file searches when a targeted read would do
- When a session starts, if Geoff flags token conservation, be explicit about it
- Don't call handoff/session ops "free" — they read multiple files and cost real tokens
