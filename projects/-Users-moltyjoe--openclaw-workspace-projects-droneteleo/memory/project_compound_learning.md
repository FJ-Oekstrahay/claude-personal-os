---
name: Compound learning — note to discuss
description: Geoff wants compound learning built into the droneteleo plan; captured for future session discussion
type: project
originSessionId: 0ffe1c8f-3e75-44df-b82b-e4880308157d
---
Geoff flagged that when commands fail or behave unexpectedly (e.g. BF 2025.12.2 renamed params, `acc_calibration` triggering rather than reading, port dying on save), those discoveries should be captured as compound learning for:
1. The droneteleo system itself (so the CLI/AI layer knows these quirks)
2. The broader OpenClaw/session memory (so future sessions don't repeat the same trial-and-error)

**Why:** Each unexpected behavior is a signal — the system should accumulate firmware-specific knowledge over time, not re-learn it per session.

**How to apply:**
- When a CLI command fails or returns unexpected output, immediately write a gotcha to project memory
- The droneteleo product roadmap should include a "firmware knowledge base" feature — structured storage of FC/firmware-specific quirks that the AI layer can consult
- This is different from user memory; it's product memory (what BF 2025.12.2 does, what ESC firmware versions support, etc.)

**TODO for future session:** Design how compound learning fits into the droneteleo architecture — where it's stored, how it's surfaced to the AI, how it's updated.
