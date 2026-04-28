---
name: /batchc skill usage, constraints, and throttle avoidance
description: /batchc skill (smartbatch protocol) usage, throttling rules, harness constraints, code-dump prevention
type: feedback
---

The `/batchc` skill (smartbatch execution protocol) implements wave-based batch scheduling with throttle protection.

**Why:** Bursty batch dispatch — all parallel tasks fired at once, repeated full-context re-sends, rapid re-dispatching between waves — causes Claude Code to be throttled.

## Throttle avoidance rules (added 2026-04-25)

- **Wave cap**: max 3 concurrent tool-heavy tasks per wave. Fewer if tasks are large or context-heavy.
- **Wave gating**: do not dispatch the next wave until the current wave has produced results. Pre-initializing all future waves upfront is a throttle risk.
- **Burst guard**: if you feel urgency to immediately fire the next wave, treat that as a risk signal and slow down.
- **Context discipline**: send only incremental context needed for the next wave. No full-prompt recaps. Reuse stable prompt structure across waves (cache-friendly).

## How to use `/batchc` correctly

- Type `/batchc` followed by your task list in the SAME message — items after `/batchc` become `$ARGUMENTS`
- If you type `/batchc` alone (no items), it applies to items in the current user message
- Do NOT type `/batchc` as a standalone message expecting it to pick up items from a prior message

## Code-dump prevention

`/batchc` explicitly prohibits inlining code changes. Any code edit/write goes to a Cob subagent. Only a one-line summary is reported back to main context.

## Harness/eval contexts

`/batchc` cannot be invoked inside a skill context where `disable-model-invocation` is enabled. Draft the batch classification manually instead (inline classification, parallel dispatch, then sequential).

**Why:** Prior incident where batch invocation returned "cannot be used due to disable-model-invocation" during Architect session on Tier 3 event architecture.
