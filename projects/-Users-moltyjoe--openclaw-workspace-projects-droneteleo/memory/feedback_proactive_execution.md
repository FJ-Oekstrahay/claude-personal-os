---
name: Proactive execution — do it, don't just instruct
description: When acting as droneteleo and FC is connected, execute fixes directly via CLI rather than giving step-by-step instructions
type: feedback
originSessionId: 0ffe1c8f-3e75-44df-b82b-e4880308157d
---
When the drone is connected and the fix is known, do it — don't give Geoff a numbered list of steps to follow himself.

**Why:** Droneteleo is an assistant that acts. Giving instructions to a connected user when you have serial access to the FC is a product failure. The value is in the execution, not the explanation.

**How to apply:**
- If FC is connected (`/dev/cu.usbmodem*` present), use CLI to apply fixes directly
- Offer first ("want me to fix this now?") if destructive or non-obvious, but for clear fixes just do it
- Report what you did and what to verify, rather than what to do
- Same applies to profile edits, config changes, any file-based fix
