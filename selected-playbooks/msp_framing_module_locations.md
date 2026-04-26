---
name: MSP framing — where it lives across modules
description: Reference guide for MSP implementation locations in droneteleo CLI; avoid creating duplicate implementations
type: reference
---

MSP framing is not a single module. It's implemented in multiple places depending on operational context:

| Module | MSP Scope | Use Case |
|---|---|---|
| `cli/blackbox.py` | MSP flash read protocol | Pulling blackbox logs from FC via serial; handles dataflash payload unpacking |
| `cli/motor.py` | MSP motor telemetry (cmd 139) | Live motor state polling; jitter sampling; RPM + temperature streaming |
| `cli/bf_bridge.py` | **Not MSP** — Playwright/CDP GUI automation | Betaflight Configurator automation via web browser; no serial/MSP involvement |

**Key gotcha:** bf_bridge is commonly mistaken for MSP handling because it touches Betaflight. It's actually web UI automation (screenshots, clicks, form filling). MSP lives in `blackbox.py` and `motor.py`.

**How to apply:**

When writing a spec that needs MSP framing:
- **Blackbox log reads?** → Extend `cli/blackbox.py`
- **Live telemetry polling?** → Extend `cli/motor.py` or add a new telemetry command there
- **GUI automation / Configurator interaction?** → bf_bridge is already the pattern

Never create a third MSP framing implementation. Check existing code in these modules first; extend rather than duplicate.

**Reference:** Session motor-night (2026-04-21) initially proposed new MSP framing module before discovering `cli/motor.py` already handles it.
