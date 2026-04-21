---
name: Batch skill invocation method
description: How to correctly invoke the batch protocol; why Skill tool fails for it
type: feedback
originSessionId: 0efddafe-550f-48f6-826f-a3148fbb2927
---
Never call `Skill({skill: "batch"})`. `/batch` is a slash command in `.claude/commands/batch.md`, not a registered Skill. Calling it via the Skill tool fails with "disable-model-invocation" error.

**Why:** Slash commands run in a different execution context. The Skill tool can't invoke them.

**How to apply:** When Geoff says "batch this", "use slash batch", or "use your batch skill" — read the protocol from the commands file and apply it directly. No tool call needed. Items must follow the request in the same message.
