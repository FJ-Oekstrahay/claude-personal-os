---
type: playbook
title: Review Sequence Protocol — Four-Role Adversarial Review
agents: [moltyjoe]
tags: [review, adversarial, critic, gadfly, architect, cto, planning, quality, code review]
created: 2026-04-21
updated: 2026-04-21
---

## Goal

Apply the right reviewer(s) to the right work in the right order. Four roles exist; each answers a different question. Running them out of order wastes the review or anchors it to the wrong frame.

## The Four Roles

| Role | Invoked via | Question it answers | Posture |
|---|---|---|---|
| **Critic** | `/critic` | Is this correct, clean, and complete? | Quality reviewer — bugs, slop, missed edge cases |
| **Gadfly** | `/gadfly` | Would a real user buy or use this? | Adversarial product — challenges assumptions, spots friction |
| **Architect** | subagent (architect type) | Does this structure hold under real load? | Adversarial technical — coupling, fragility, hidden complexity |
| **CTO** | `/cto` | What should be built, and in what order? | Constructive planning — prioritizes, scopes, resolves tradeoffs |

## Decision Tree

```
User-visible work OR committing a product direction?
→ YES: run Gadfly (before CTO if CTO will also run)

Code or implementation being shipped?
→ YES: run Critic (after writing, before merging)

Touches core architecture: data models, module/service boundaries,
API contracts, or spans multiple files/system boundaries?
→ YES: run Architect (before coding if possible; before merging if scope crept)

Major feature plan, roadmap decision, or "what next?"
→ YES: run CTO (after Gadfly if product direction is involved)

Minor bug fix, internal refactor, tooling-only?
→ NONE required (Critic is cheap insurance if uncertain)
```

## Critical Sequencing Rule: Gadfly Before CTO

CTO produces polished, coherent plans. Gadfly responding inside that frame is already anchored — it argues at the margins instead of questioning the premise. Run Gadfly first on the raw idea, then let CTO incorporate the pushback.

**Exception:** if you need CTO output to scope what Gadfly evaluates, run CTO first but bump Gadfly to Opus to match tiers.

## When to Trigger Gadfly

Gadfly is triggered by **direction commitment**, not feature complexity.

Run Gadfly when locking in something expensive to reverse:
- Naming decisions (product, feature, command, API names)
- Pricing and tier decisions
- User-facing copy, onboarding flows, error messages
- Feature scope (what's in v1 vs. later)
- "We won't do X" decisions
- Interface/schema choices external parties will depend on

Skip Gadfly for:
- Internal tooling, test harnesses, eval infrastructure
- Bug fixes and refactors
- Config tweaks, parameter tuning
- Anything reversible in under an hour

## Model Escalation

| Role | Default | Escalate to Opus when |
|---|---|---|
| Critic | Sonnet | Never — quality review doesn't need deep strategy |
| Gadfly | Sonnet | Responding to a CTO-on-Opus output (match tiers) |
| Architect | Sonnet | >3 files or >1 system boundary |
| CTO | Sonnet | Genuine strategic inflection point (pricing, platform pivot, open-source decision) |

**CTO on Opus warning:** Opus plans feel authoritative and anchor downstream reviewers. Reserve for real inflection points.

## Quick Reference by Work Type

| Work type | Reviewers | Order |
|---|---|---|
| New user-facing feature | Gadfly, Critic, possibly CTO | Gadfly → CTO → implement → Critic |
| Architecture decision | Architect, possibly CTO | Architect → CTO → implement |
| Roadmap / feature prioritization | Gadfly, CTO | Gadfly → CTO |
| Code-only (spec exists) | Critic | Implement → Critic |
| Config / infrastructure change | Critic, possibly Architect | Architect → implement → Critic |
| Writing, docs, copy | Gadfly (if user-facing) | Gadfly → revise |
| Bug fix / internal refactor | None | Critic if uncertain |

## Iteration Rules

- If a reviewer surfaces a blocker, resolve it before proceeding to the next reviewer.
- If Gadfly kills the direction, don't run CTO — there's nothing to plan.
- If Architect flags a structural problem, bring it back to CTO before coding.
- Critic is the last gate before committing. Don't skip it because earlier reviews went well — implementation drift is real.

## The Gap These Roles Don't Cover

Neither Gadfly nor Architect answers: "Is this the right hill at all, given competitive landscape and actual constraints?" When a session involves a roadmap fork or "why this vs. alternatives?", explicitly frame the Gadfly or CTO prompt around that axis — or note it as an open question.

## Related playbooks

- [[cto_agent_adversarial_review]] — the CTO agent spawn pattern in detail
- [[architect_review_early]] — when and how to run Architect review
