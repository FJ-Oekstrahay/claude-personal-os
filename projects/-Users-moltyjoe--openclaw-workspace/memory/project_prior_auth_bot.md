---
name: Prior Auth Bot project context
description: How to trigger a test call to the prior-auth-bot voice agent; 5053063104 is Geoff's test line
type: project
---

Prior-auth-bot is a voice AI agent that automates insurance prior authorization calls (Pipecat + Gemini Live + Twilio). Project at `/Users/moltyjoe/.openclaw/workspace/projects/prior-auth-bot`.

**Why:** When Geoff says "call 5053063104 test prior auth bot" or similar, run `pa-test-call 5053063104` from any directory. The script handles server + ngrok startup automatically.

**How to apply:** Recognize any variant of "call [number] test prior auth bot" as a trigger to run `pa-test-call [number]`. Read the playbook at `~/.openclaw/workspace/memory/playbooks/prior_auth_test_call.md` for full context.
