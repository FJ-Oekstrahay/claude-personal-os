---
name: AGENT_SYSTEM ownership decision
description: CTO decided Option B — client owns AGENT_SYSTEM, proxy passes it through. DO NOT re-review this.
type: feedback
originSessionId: 9ff3d3fa-fdc6-428b-a714-03898fdf7f63
---
**Decision: Option B — client owns AGENT_SYSTEM, proxy passes it through.**

This has been decided. Do not run another CTO review on this topic.

**What was decided:** `AGENT_SYSTEM` in `agent.py` is the single source of truth. All call paths — BYOK and bundled — use it. The proxy forwards whatever `system=` the client sends; it does not own or override it.

**Why:** AGENT_SYSTEM changes frequently (weekly during tuning). Baking it in the Worker requires a `wrangler deploy` on every change. Two copies diverge silently. Client ownership = single source of truth.

**What was fixed:** `_ask_proxy()` in `cli/ai.py` now accepts `system: str = ''` and includes it in the payload for non-classify calls. `ask()` passes `system=system` through. Worker's `SYSTEM_PROMPT` constant is now dead code (never reached because client always sends system).

**Worker change needed:** None. Worker already does `system || buildSystemPrompt(user_profile)` — client-supplied system wins.

**How to apply:** If AGENT_SYSTEM ownership ever comes up again: the decision is made, the fix is shipped. Point here. Do not re-review.
