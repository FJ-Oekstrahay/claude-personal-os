---
name: gog auth troubleshooting
description: If gog Drive auth fails, ask Geoff to re-auth — don't spiral into workarounds
type: feedback
---

If `gog` ever gives auth errors, ask Geoff to run:
`! gog auth add geoff.k.hoekstra@gmail.com --services drive`

Do not try to work around it — just ask. Geoff confirmed this explicitly.

**Why:** The keyring token can expire or fail to persist. The browser flow is the only fix.
**How to apply:** Any time `gog drive` or other gog commands return "No auth" errors.
