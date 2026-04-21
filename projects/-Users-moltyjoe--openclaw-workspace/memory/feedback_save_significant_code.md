---
name: Save significant code before session ends
description: Any non-trivial script or tool written during a session MUST be committed to git or saved to a project directory — not left as a temp artifact
type: feedback
---

Always commit or save significant code before a session ends. Do not leave working scripts as temp session artifacts.

**Why:** Python CLI scripts built during the April 6 Dronewhisper session (`seeker3_restore2.py`) were never committed and were lost when the session ended. Geoff had to reconstruct from handoff notes. This is unacceptable for real working code.

**How to apply:**
- After writing any non-trivial script (>~20 lines, or any script that actually runs and works), commit it to the relevant project git repo before the session closes.
- At minimum, surface it during `/session-handoff` with a reminder: "This script was written but not committed — do you want me to commit it now?"
- Don't assume the nightly auto-commit will catch it — it only captures what's already tracked or staged.
