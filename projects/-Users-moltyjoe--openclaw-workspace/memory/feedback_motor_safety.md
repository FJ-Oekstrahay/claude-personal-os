---
name: Motor safety — always ask before spinning
description: NEVER spin motors via CLI or script without explicit permission from the user in that turn. Props can be on.
type: feedback
---

**ALWAYS ask for permission before spinning motors.** Never assume it's safe to issue any command that could spin motors (e.g., `motor` CLI commands, motor test commands, arming sequences).

**Why:** Props may be on. A motor spin command with props attached is a blade hazard. This is a hard safety rule, not a preference.

**How to apply:** Before running any CLI command that could actuate motors (including `motor <index> <value>`, any motor test, or anything that arms the FC), explicitly ask the user first in that conversation turn. One sentence is enough: "Props on? Can I spin motor X?" Do not proceed without a yes in that same turn.
