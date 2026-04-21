---
name: Token efficiency as standing process
description: Geoff wants to continuously look for ways to efficiently use tokens and time — not just when asked
type: feedback
originSessionId: e28427ed-2e7c-4d5d-988c-fe85ca827b43
---
Proactively look for token/time efficiency opportunities throughout every session. Don't wait for Geoff to ask.

**Why:** Stated as a standing process preference, not a one-off request.

**How to apply:**
- **Dispatch to Cob** when the design is decided, target lines are known, and the edit is >~30 lines or touches multiple locations. Pass exact file paths, line anchors, and the implementation spec. Keep design decisions and the resulting summary in main context — let Cob consume the file reads and write the diff.
- **Do NOT dispatch to Cob** for short targeted edits (< ~30 lines, single location) where you've already paid the file-read cost — finishing inline is cheaper than re-briefing.
- For research tasks that don't need the full project context, use Seymour or Lumpy.
- The expensive part is reading and understanding files — once that's sunk, finishing inline is often cheaper than re-briefing a subagent.
- Flag the tradeoff explicitly when the choice is non-obvious ("I can finish this inline or brief Cob — your call").
