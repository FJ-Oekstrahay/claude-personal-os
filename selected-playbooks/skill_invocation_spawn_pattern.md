---
name: Skill invocation — spawn output pattern
description: Understanding skill output vs auto-spawn behavior; manual Agent tool invocation required
type: feedback
---

Skill invocations (`/gadfly`, `/safety-review`, `/cto`, etc.) output detailed persona prompts and instructions but do not automatically spawn a subagent. The skill is a *prompt generator*, not an executor.

**Pattern discovered:** Session motor-night (2026-04-21) invoked `/gadfly` and `/safety-review` skills. Both produced detailed review prompts with framing instructions. Neither spawned agents automatically. The output had to be read and manually fed to the Agent tool (`/agent --persona <name>` or `Skill("agent")`).

**Behavior:**
- Skill outputs the complete persona prompt (framing, questions, decision points, examples)
- The skill **does not** call the Agent tool or spawn a subagent
- You must read the output and invoke Agent manually with the persona name or prompt text

**How to apply:**

When you run `/gadfly`, `/cto`, `/safety-review`, `/architect`:

1. Read the skill output completely — it is the review prompt
2. Note the persona name (Gadfly, CTO, Safety Officer, Architect)
3. Call `Skill("agent")` with the prompt as context, or manually invoke the appropriate agent via Claude Code's agent dispatch
4. Feed the persona prompt as context to the agent session

Don't assume the skill will spawn the agent. Skills provide prompts; Claude Code sessions invoke agents.

**Why:** Separation of concerns — the skill generates structured prompts (deterministic, reusable), agent invocation is a separate decision. This allows skills to be version-controlled and reused across multiple agent systems without hardcoding spawn logic.
