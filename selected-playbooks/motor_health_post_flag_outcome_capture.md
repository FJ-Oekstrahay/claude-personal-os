---
type: playbook
title: Motor Health Post-Flag Outcome Capture Loop (v1.1)
agents: [jarface]
tags: [jarface, outcome capture, validation loop, threshold calibration, motor health, feedback loop, droneteleo]
created: 2026-04-22
updated: 2026-04-22
---

## Problem

The 10% motor drift flag threshold is a heuristic with no field calibration. Without learning what pilots actually find when motors are flagged, the threshold is never refined against real motor behavior and failure modes.

## Solution: Post-Flag Outcome Question

After a motor is flagged (e.g., Motor 2 down 16% from baseline), the next session JARFACE asks:

> "Last session Motor 2 flagged 16% drift — did you inspect it? What did you find?"

Pilot responses are logged back to the specific flagged entry, creating a validation dataset:

```json
{ "outcome_reported": true, "outcome_text": "Found some debris between bell and stator, cleaned it out." }
```

## Data Schema (v1.0 Stubs)

Every log entry includes v1.1 fields as stubs in v1.0, so v1.1 can write back without a schema migration:

```json
{
  "outcome_reported": false,
  "outcome_text": null
}
```

When v1.1 injects the question:
- `outcome_reported` → `true` once pilot responds
- `outcome_text` → free-form text of what they found (e.g., "cleaned out debris", "bearing is rough", "prop was loose")

If pilot dismisses (says "skip" or ignores): `outcome_reported` stays `false`, do not re-ask in subsequent sessions.

## Injection Logic (v1.1)

In `build_context.py`:

1. After injecting a flag, check if `outcome_reported` is `false`
2. If so, inject follow-up question
3. On next session, read pilot's response and log it
4. Do not re-ask once answered

## Why This Is a Commitment, Not Optional

**Without outcome data:**
- 10% threshold is never validated against actual failures
- We're flying blind on whether the signal is too sensitive, too loose, or useless
- Future refines (e.g., "maybe 15% is better") are guesses with no ground truth

**With outcome data:**
- Real events become calibration points: "Motor flagged at -16%, pilot found debris and fixed it" = signal working
- Accumulation of outcomes enables threshold refinement: "In 100 events, 80 at -10 to -15% are fixed by inspection; threshold is good"
- Builds confidence in the signal for prod rollout and competitive positioning

## Implementation Checklist (v1.1 future session)

- [ ] JARFACE injection checks `outcome_reported` field
- [ ] Follow-up question is triggered once per flagged entry (not per session)
- [ ] Pilot response captured to `outcome_text`
- [ ] Response marked as `outcome_reported: true` to prevent re-asking
- [ ] Schema supports free-form text (no structured form fields — natural conversation)

## Related Patterns

- [[motor_health_nag_muting_pattern]] — v1.0 mute counter to prevent fatigue
- [[compound_knowledge_outcome_capture]] — outcome loop as general pattern for threshold validation
