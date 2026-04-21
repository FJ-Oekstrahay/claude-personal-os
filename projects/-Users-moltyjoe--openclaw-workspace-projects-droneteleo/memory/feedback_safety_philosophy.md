---
name: Safety philosophy — bench testing and motor safety
description: Geoff's stance on how much JARFACE should guard against bench testing risks
type: feedback
originSessionId: 75734cf9-e980-455c-8296-ecf9aff60c51
---
Don't engineer JARFACE as if pilots might have props on during a config session. Betaflight already owns motor safety: motor enable toggle, "I accept the risk" acknowledgment, and multiple safety screens. JARFACE doesn't need to add a fourth gate.

**Why:** BF's existing system is sufficient. Treating pilots like they need hand-holding on basic bench safety is condescending to experienced FPV pilots.

**How to apply:**
- PID value warnings (unusual P/D/I values): show a warning but don't block with a secondary confirmation. BF owns the risk of "what if it oscillates."
- Failsafe/motor_protocol/arming params: keep secondary confirmation — these affect *in-flight* behavior, not bench safety. That's a different risk category.
- "Props off" reminders: fine to keep, everyone knows this already but it's a quick reminder not a safety gate.
- Don't add new confirmation layers for parameter changes that only matter if the motors are spinning on the bench.
