---
name: gog auth troubleshooting
description: If gog Drive auth fails, ask the user to re-auth — don't spiral into workarounds
type: feedback
---

If `gog` ever gives auth errors, ask the user to run:
`! gog auth add author@example.com --services drive`

Do not try to work around it — just ask. the user confirmed this explicitly.

**Why:** The keyring token can expire or fail to persist. The browser flow is the only fix.
**How to apply:** Any time `gog drive` or other gog commands return "No auth" errors.
