---
name: feedback_gateway_restart
description: When Geoff approves config changes that need a gateway restart, just do the restart — don't tell him to do it manually
type: feedback
---

When Geoff has approved changes to agent config (IDENTITY.md, openclaw.json tool grants, etc.) and a gateway restart is needed to pick them up, just run the restart. Don't present it as a manual step for him to do.

**Why:** Geoff already approved the changes — the restart is the obvious next step, not a separate decision point.

**How to apply:** After editing agent config files with Geoff's approval, run `launchctl kickstart -k gui/$(id -u)/ai.openclaw.gateway` immediately as part of the same flow.
