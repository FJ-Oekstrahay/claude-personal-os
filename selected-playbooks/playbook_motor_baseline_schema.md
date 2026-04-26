---
name: Motor Baseline Schema (CTO Decisions 2026-04-20)
description: Firmware version + DSHOT protocol tracking; motor_map list-of-objects; efficiency → rpm_response rename
type: feedback
---

Motor baseline schema has three CTO-decided changes (2026-04-20) to improve reproducibility and context for motor tuning.

**Field additions:**

- `firmware_version` — Betaflight firmware version at time of baseline (string, e.g. "4.5.0")
- `dshot_protocol` — DSHOT protocol version (e.g. "600" for DSHOT600)
- Why: Motor behavior varies significantly across firmware versions and DSHOT rates; future tuning advice must know which baseline this came from
- How to apply: Capture these from `get_status()` (firmware_version from flight_controller.firmware_version or BF CLI `version`; dshot_protocol from `dshot_bitrate` config parameter)

**Field restructure:**

- `motor_map` changes from list-of-strings `["M1", "M2", "M3", "M4"]` to list-of-objects:
  ```json
  [
    {"motor": "M1", "spin_direction": "normal"},
    {"motor": "M2", "spin_direction": "reversed"},
    ...
  ]
  ```
- Why: Motor direction (normal vs reversed) is fundamental to asymmetry diagnosis; static list-of-strings loses this info
- How to apply: During motor test baseline capture, read `motor_direction` BF config (or infer from motor_stop behavior if available)

**Field rename:**

- `efficiency` → `rpm_response` (throughout motor_baseline schema)
- Why: "efficiency" is ambiguous (electrical efficiency? thermal? speed response?); "rpm_response" is specific to what we measure (throttle-to-RPM linearity)
- How to apply: Update any extraction prompts, schema validators, and write-back code that touches this field

**Version isolation:**

Motor baseline is versioned at capture time. Future tuning operations read baseline metadata to understand whether advice applies.

Example: If a baseline was captured on Betaflight 4.4 with DSHOT300, and pilot upgrades to 4.5 with DSHOT600, the baseline is still valid for historical comparison but tuning advice must account for the upgrade.

Why: Firmware updates change PID tuning, DSHOT rates affect filtering behavior, and motor direction affects oscillation diagnosis.

