---
name: JARFACE output filtering — debug-only "What I learned" panel
description: Stripped gear/settings recaps from "What I learned"; kept debug content only
type: feedback
---

The "What I learned" panel was cleaned up to remove gear/settings recaps that cluttered output without adding value.

**Why:** Users were seeing noise like "I learned your radio is a Radiomaster Pocket" in the session summary, which is already known context. Debug-only content (discoveries, rule changes, failures) is valuable; inventory recaps are not.

**How to apply:**
- In agent output summarization, filter summaries to include only:
  - New discoveries or insights (e.g., "motor 2 has 15% efficiency drop")
  - Rule changes or decisions (e.g., "switched to 6000 Hz gyro sample rate")
  - Errors or failures surfaced (e.g., "DJI O4 voltage sagging under 11.2V")
- Exclude:
  - Detected hardware (already in context)
  - Known settings that were read but not changed
  - Routine parameter confirmations
- This keeps the summary signal-to-noise ratio high and reduces cognitive load
