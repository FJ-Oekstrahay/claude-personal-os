---
type: playbook
title: Research Question Triage via CTO Agent
description: Bouncing research questions off a CTO persona agent before dispatching a researcher avoids out-of-scope work and sharpens scope
agents: [moltyjoe, gerbilcheeks]
tags: [research, delegation, triage, agent workflow, scope, efficiency]
updated: 2026-04-12
---

## Goal
Before dispatching a researcher agent (e.g., Seymour, Lumpy) on multi-part research work, bounce the research questions off a CTO agent in the same thread to sharpen scope and eliminate out-of-scope questions. This cuts wasted research effort by ~30–50% and improves result quality.

## When to Use
- Multi-part research requests with 5+ questions or unclear boundaries
- Areas where business context and scope could hide technical assumptions (e.g., hardware benchmarks, infrastructure cost models, competitive landscape)
- When the asker is not an expert in the domain being researched

## Pattern (Two-Round Workflow)

### Round 1: CTO Triage (5–15 min)
1. Spawn a CTO agent with a brief prompt:
   - Include the raw research request or questions
   - Ask: "Which of these questions are worth answering? Which are out of scope or flawed? Rank by business impact."
   - CTO should push back on ambiguous questions, suggest rewording, and flag assumptions

2. CTO returns:
   - Ranked questions (highest impact first)
   - Flagged questions (out of scope, duplicative, or based on false premises)
   - Clarifications or better-formed versions of fuzzy questions
   - Rough expected effort per question

### Round 2: Researcher Dispatch
1. Use the CTO's triage output to draft the research request for the researcher agent
2. Include **only** the high-impact, in-scope questions from Round 1
3. Researcher now works with clear scope and avoids tangents

## Example (Hardware LLM Benchmarks)

**Initial (unfiltered) questions:**
- What 7B models can run on Raspberry Pi?
- Why does quantization help?
- What's the best ONNX conversion workflow?
- How fast can Pi 4 run inference?
- Should we use CUDA?
- What about Coral TPU?

**CTO feedback:**
- "Q1, Q4: core to your hardware selection" ✓
- "Q2: background noise for now; only if Q1 answer depends on understanding why" 
- "Q3: **out of scope** — you don't own the build pipeline yet"
- "Q5: **false premise** — Pi has no CUDA support"
- "Q6: different hardware path; separate decision"
- "**Reframe Q1 as:** 'What's the inference speed (tok/s) of Llama 3.2 3B vs 7B on Pi 5 8GB, with evidence, not estimates?'"

**Researcher dispatch (focused):**
- Q1 (reframed): Llama 3.2 3B vs 7B performance on Pi 5 8GB with citations
- Q4: Pi 4 4GB baseline (expect OOM for 7B)

## Gotchas

**Over-filtering:** Don't let CTO kill exploratory questions entirely. If a question is "lower impact but interesting," note it as exploratory rather than out-of-scope.

**Scope creep in Round 2:** Researcher will sometimes uncover a better angle mid-work. Plan to read the result and optionally do a second research round if the first round surfaces surprising findings.

**CTO hallucination on evidence:** CTO may claim something is "common knowledge" or "well-established" without evidence. Treat CTO triage as guidance, not fact. Researcher's job is to verify.

## Related Playbooks
- [[cto_agent_adversarial_review]] — full product critique pattern (heavier weight)
- [[agent_model_selection]] — when to use which agent for multi-part work
- [[knowledge_compounding]] — how to route the triage lessons into playbooks

## Standing Metrics
- **Before this pattern:** 5–7 questions dispatched, ~2–3 turned out out-of-scope or based on false assumptions
- **After this pattern:** ~3–4 questions dispatched, all answerable; research time cut by 30–50%
