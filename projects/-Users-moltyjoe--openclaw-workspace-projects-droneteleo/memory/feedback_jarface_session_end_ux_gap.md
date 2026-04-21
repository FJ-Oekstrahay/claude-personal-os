---
name: JARFACE session-end learning UX gap
description: JARFACE doesn't tell Geoff what it wrote back at session end — silent learning flywheel is a near-term fix priority
type: project
originSessionId: 09a8b03a-b469-47a8-9999-07d5f12a32df
---
JARFACE writes back applied commands, outcomes, and discoveries to `builds/<craft>.json` at session end, but shows no summary to the pilot. Geoff has to read the JSON manually to see what was learned.

**Why:** Identified 2026-04-19 after Geoff asked "how do I observe the system learning?" — the answer was "you can't, without digging into files." This breaks the learning feedback loop.

**How to apply:** When implementing any session-end UX work, include a one-line learning summary printout. Suggested format: "Wrote back: d_roll 14→15 (outcome=pending), 1 new discovery." Treat this as near-term priority, not backlog.
