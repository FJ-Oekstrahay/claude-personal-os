---
name: No file content dumps in responses
description: Don't show file edits, writes, or code diffs inline in responses — just do the work and say what changed
type: feedback
originSessionId: 15dd8b26-d2c0-4310-beb1-63531d74caaf
---
When editing or writing files, do not dump file content into the response. Just make the change and state what was done (one line, e.g. "Updated TEST_PLAN.md — added P6 protocol"). Same rule for code: show the result, not the edit mechanics.

**Why:** Geoff can read diffs. Wall-of-code responses add friction without value.

**How to apply:** After any file write/edit, output at most one sentence describing what changed. No before/after blocks, no code echoes, no "here's what I wrote."
