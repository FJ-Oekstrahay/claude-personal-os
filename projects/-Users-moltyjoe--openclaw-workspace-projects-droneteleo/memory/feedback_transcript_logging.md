---
name: Interactive session transcript logging
description: Every dt agent session should write a transcript log; use it for debugging, don't pull into context blindly
type: feedback
originSessionId: 5df9e0ff-849f-479d-9e93-3f120e911f31
---
Every interactive `dt agent` session should produce a transcript log in `logs/session_<ts>_<fc_name>.txt`.
Without it, debugging failures requires Geoff to paste terminal output manually.

**When debugging:** Check `logs/` for the relevant session transcript before asking Geoff what happened.
Only read/search the transcript when you actually need to bring specific content into context — don't
pull entire transcripts in as a matter of course.

**How to apply:**
- If transcript logging isn't implemented: prompt 17 (Gap 3) builds it
- If it is implemented: `ls -t logs/session_*.txt | head -5` to find recent sessions
- Use Grep on the transcript to find the specific turn that failed before reading the whole file

The scripted bench test already writes transcripts (`logs/jarface_test_*.txt`).
Interactive sessions need the same treatment.
