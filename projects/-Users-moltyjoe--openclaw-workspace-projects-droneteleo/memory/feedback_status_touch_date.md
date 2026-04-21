---
name: Status file touch date rule
description: When updating any STATUS file, maintain a most-recent touch date in each section header or entry
type: feedback
originSessionId: 71632421-9bec-45f1-9c04-1f065a366c6d
---
When updating a STATUS file (e.g., STATUS.md, STATUS2.md, PLANNING-STATUS.md), maintain a **most recent touch date** in each section — typically as part of the section header or a `Last updated:` line within it.

**Why:** Makes it easy to see at a glance which sections are stale vs. actively maintained, without needing to diff git history.

**How to apply:** On every STATUS file edit, update the touch date for any section you modify. Do not retroactively update sections you didn't touch. Format TBD by file convention — match what's already there, or add `Last updated: YYYY-MM-DD` if none exists.
