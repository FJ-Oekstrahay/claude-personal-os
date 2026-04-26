---
name: LLM System Prompt Safety Language Interpretation
description: How to write "warn-not-block" safety guardrails in system prompts; hard refusal vs proposed guidance
type: feedback
---

## "Never recommend without confirmation" is interpreted as hard refusal

**The issue:** System prompt language saying "never recommend X without confirmation" is interpreted by LLMs as a hard refusal to offer X at all, not as a conditional workflow.

**Why:** LLMs treat "never" as an absolute constraint. Pairing it with a condition ("without confirmation") creates a contradiction — the model chooses refusal over the conditional path.

**How to apply:** To get **warn-not-block** behavior:

1. Explicitly state the model **will** propose the change anyway
2. Acknowledge that the system has its own safety gate downstream
3. Frame it as "the system handles enforcement; your job is to suggest"

**Example of what doesn't work:**
```
Never recommend disabling motor safety without user confirmation.
```

**Example of what works:**
```
Propose motor safety changes with a warning label. The system has built-in enforcement 
gates — your job is to surface the change and explain the rationale. The user or 
downstream system decides whether to apply it.
```

The second version lets the model propose while still highlighting the risk — the distinction is that you're delegating enforcement to another layer, not to the model's refusal logic.
