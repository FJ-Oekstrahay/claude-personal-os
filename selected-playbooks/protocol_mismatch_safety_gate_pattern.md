---
type: playbook
title: Protocol Mismatch Safety Gate Pattern
agents: []
tags: [safety, firmware, dshot protocol, betaflight, motor check, validation, safety gates, droneteleo]
created: 2026-04-22
updated: 2026-04-22
---

## Pattern

When comparing motor performance against a baseline (e.g., `dt motor check` vs. stored `motor_baseline`), **check firmware version and DSHOT protocol before trust**.

If either changed since baseline:
```
⚠ Firmware changed since baseline (4.5.0 → 4.5.1). Results may not be comparable.
  Consider re-running `dt motor test` to reset baseline.
```

Rationale: firmware or protocol changes can alter motor behavior at the same throttle point, making historical baseline comparison meaningless. User must explicitly consent by re-running the baseline.

## Implementation Location

This check belongs in the **comparison logic**, not in the baseline creation:

- **Where:** `cmd_health()` or equivalent command that reads a baseline and compares current state
- **Current location in droneteleo:** `motor.py:699`
- **Condition:** `if fw_version != baseline_fw or protocol_name != baseline_proto:`
- **Action:** Warn and exit without logging. Do not produce a partial result.

## Why It Works

- **One check, both conditions:** A single OR covers firmware-only mismatch, protocol-only mismatch, or both
- **User consent:** Requiring a fresh `dt motor test` is explicit — pilot must actively opt into a new baseline
- **Prevents confusion:** Pilot sees drift reported, troubleshoots the motor, then realizes the baseline was from 4.4.3 and firmware is now 4.5.1

## Discovery Note

Safety Officer review of `motor-health-drift.md` spec discovered this check already exists in the codebase but was **not documented in the spec**. The spec was updated to document the pre-existing implementation explicitly, avoiding redundant implementation during coding.

**Lesson:** When a spec claims a feature is "needed", grep the codebase first — it may already be done.

## Related Patterns

- [[spec_presearch_codebase_check]] — verify module existence and prior art before writing spec
- [[config_diff_completeness]] — checking multiple dimensions (not just one field) for safety-critical comparisons
