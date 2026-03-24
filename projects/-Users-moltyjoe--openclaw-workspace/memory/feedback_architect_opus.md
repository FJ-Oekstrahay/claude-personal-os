---
name: feedback_architect_opus
description: Always invoke The Architect subagent with model opus when Geoff asks for an architect review
type: feedback
---

Always pass `model: "opus"` when invoking `The Architect` subagent via the Agent tool.

**Why:** Geoff explicitly asked for this. The Architect agent definition has no default model override — without specifying it, the model inherits from the parent (Sonnet). Nothing in memory or files enforces this automatically; it must be set explicitly on each call.

**How to apply:** Any time Geoff says "have the architect review" or similar, the Agent tool call must include `"model": "opus"`.
