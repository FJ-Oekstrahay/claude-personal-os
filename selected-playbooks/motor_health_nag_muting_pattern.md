---
type: playbook
title: Motor Health Nag-Muting Pattern
agents: [jarface]
tags: [jarface, injection, ui, muting, flags, nag prevention, user experience, motor health, droneteleo]
created: 2026-04-22
updated: 2026-04-22
---

## Problem

JARFACE surfaces motor health flags at session start to prompt inspection. Without muting, it will show the same flag every session until the condition changes, creating fatigue and noise.

## Solution Pattern

Use a **mute counter** + **session gate** pattern:

1. **Log entry schema** tracks:
   - `injection_count`: how many sessions have seen this flag
   - `mute_after_session_n`: threshold (default 3 sessions)
   - `outcome_reported`: whether pilot responded to follow-up question (v1.1)

2. **Injection logic** (in `build_context.py`):
   - Read last `motor_health_log` entry
   - If `any_flagged` AND `injection_count < mute_after_session_n`: inject flag note AND increment `injection_count`
   - If `injection_count >= mute_after_session_n`: suppress injection until a new check run

3. **Reset on new check**:
   - `dt motor check` writes a fresh log entry with `injection_count: 0`
   - This resets the mute counter and allows re-injection if the flag persists

## Key Design Decisions

- **Count is sessions, not time** — catches pilots who return after a week away (3 sessions = 1 week at typical frequency)
- **Threshold is configurable per entry** — allows future tuning without schema migration
- **Fresh check resets globally** — pilot running `dt motor check` is implicit acknowledgment; they get flagged again if drift persists
- **Outcome capture (v1.1) is the validation loop** — without asking "what did you find?", the 10% threshold is never calibrated to real motor behavior

## Implementation Checklist

- [ ] Schema includes both `injection_count` and `mute_after_session_n` at log-entry level
- [ ] `injection_count` incremented before context injection, not after
- [ ] Fresh log entry from `dt motor check` always starts with `injection_count: 0`
- [ ] Injection condition is: `any_flagged AND injection_count < threshold`
- [ ] No logging happens if muted (no side effects to an already-stable log entry)

## Why This Pattern

Prevents alert fatigue without losing safety signal. A flag surfaced 3 times gives the pilot fair chance to notice; suppressing further shows respect for their time. New check run = permission to re-inject, which keeps the feedback loop honest.

## Related Patterns

- [[motor_health_post_flag_outcome_capture]] — v1.1 validation loop
- [[fc_context_injection_staleness_thresholds]] — similar pattern for calendar staleness
