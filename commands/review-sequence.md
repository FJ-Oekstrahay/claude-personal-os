# /review-sequence — Multi-role adversarial review protocol

When invoked, read the current task or artifact being discussed, then use this protocol to determine which reviewer(s) to run and in what order.

---

## The four reviewer roles

| Role | Invoked via | Question it answers | Posture |
|---|---|---|---|
| **Critic** | `/critic` | Is this correct, clean, and complete? | Quality reviewer — finds bugs, slop, and missed edge cases |
| **Gadfly** | `/gadfly` | Would a real user buy or use this? | Adversarial product — challenges assumptions, spots friction |
| **Architect** | subagent (architect type) | Does this structure hold under real load and scale? | Adversarial technical — flags coupling, fragility, hidden complexity |
| **CTO** | `/cto` | What should be built, and in what order? | Constructive planning — prioritizes, scopes, resolves tradeoffs |

---

## Decision tree

Run through each question in order. Multiple reviewers may apply.

```
Is the work user-visible, OR does it commit a product direction?
→ YES: run Gadfly — before CTO if CTO will also run (see sequencing rule below)

Is the work code or implementation that will be shipped?
→ YES: run Critic — after writing, before merging/committing

Does the work touch core architecture: data models, module/service boundaries,
API contracts, or spans multiple files or system boundaries?
→ YES: run Architect — before coding if possible; before merging if scope crept

Is the work a major feature plan, roadmap decision, or "what next?"
→ YES: run CTO — after Gadfly if product direction is involved

Is the work a minor bug fix, internal refactor, or tooling-only change?
→ NONE required (Critic is cheap insurance if uncertain)
```

---

## Sequencing rule (critical)

**Gadfly before CTO, not after.**

If CTO runs first, it produces a polished, internally coherent plan. Gadfly responding inside that frame is already anchored and outgunned — it argues at the margins instead of questioning the premise.

Running Gadfly first on the raw idea gives unbiased product pushback. CTO then incorporates it.

**Exception:** if you need CTO's output to scope what Gadfly should evaluate, run CTO first but bump Gadfly to Opus for the follow-up to match the model tier.

---

## When to trigger Gadfly

Gadfly is triggered by *direction commitment*, not by feature complexity.

Ask: "Am I about to lock in a decision that's expensive to reverse?"

**High trigger value (run Gadfly):**
- Naming decisions — product, feature, command, API names
- Pricing and tier decisions
- User-facing copy, onboarding flows, or error messages
- Feature scope decisions (what's in v1 vs. later)
- Any "we won't do X" decision
- Interface or schema choices that external parties will depend on

**Low / skip Gadfly:**
- Internal tooling, test harnesses, eval infrastructure
- Bug fixes and refactors
- Parameter tuning, threshold adjustments, config tweaks
- Anything that takes less than an hour to reverse

---

## When to escalate to Opus

| Role | Default | Escalate to Opus when |
|---|---|---|
| Critic | Sonnet | Not needed — quality review doesn't require deep strategy |
| Gadfly | Sonnet | Responding to a CTO-on-Opus output (match tiers) |
| Architect | Sonnet | Touching more than 3 files or more than 1 system boundary |
| CTO | Sonnet | Genuine strategic inflection point (pricing model, platform pivot, open-source decision) |

**CTO on Opus warning:** Opus writes persuasive, comprehensive plans that feel authoritative. This anchors downstream reviewers. Reserve it for genuine strategic inflection points — not routine planning or feature ordering.

---

## The gap neither Gadfly nor Architect covers

Neither "would users buy this?" (Gadfly) nor "does the structure hold?" (Architect) answers: *"Is this the right hill at all, given the competitive landscape and actual constraints?"*

When a session involves a roadmap fork or a "why this vs. alternatives?" question, explicitly frame the Gadfly or CTO prompt around that axis — or note it as an open question if no reviewer session is being run.

---

## Quick reference by work type

| Work type | Reviewers | Order |
|---|---|---|
| New user-facing feature | Gadfly, Critic, possibly CTO | Gadfly → CTO → implement → Critic |
| Architecture decision | Architect, possibly CTO | Architect → CTO → implement |
| Roadmap / feature prioritization | Gadfly, CTO | Gadfly → CTO |
| Code-only implementation (spec already exists) | Critic | Implement → Critic |
| Config or infrastructure change | Critic, possibly Architect | Architect (if non-trivial) → implement → Critic |
| Writing, docs, copy | Gadfly (if user-facing) | Gadfly → revise |
| Bug fix or internal refactor | None required | Critic if uncertain |

---

## Iteration guidance

- If a reviewer surfaces a blocker, resolve it before proceeding to the next reviewer.
- If Gadfly kills the direction, don't run CTO — there's nothing to plan.
- If Architect flags a structural problem, bring it back to CTO before coding.
- Critic is the last gate before committing. Don't skip it because earlier reviews went well — implementation drift is real.
