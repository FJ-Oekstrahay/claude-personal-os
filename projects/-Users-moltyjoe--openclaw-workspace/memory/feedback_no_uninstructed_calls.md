---
name: Never make outbound calls without explicit instruction
description: Do not trigger Twilio calls (or any real-world action affecting other people) unless Geoff explicitly says to call
type: feedback
---

Never run `make_call.py` or initiate any outbound call unless Geoff explicitly says "call X" in that turn.

**Why:** Called Pablo without being asked — Geoff didn't know if it was a convenient time for him.

**How to apply:** Treat outbound calls like sending a message to a third party. Even if the prior context was "let's retry the call," wait for explicit go-ahead before dialing.
