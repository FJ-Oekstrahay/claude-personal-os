---
name: dt diff baseline selection and fallback behavior
description: dt diff uses most recent non-pre-agent backup as baseline; falls back to oldest if none exist
type: feedback
---

The `dt diff` command compares the current config against a baseline backup. The baseline selection follows this priority:

1. Most recent backup that is **not** marked as a pre-agent backup
2. If no non-pre-agent backups exist, falls back to the oldest available backup
3. If only pre-agent backups exist, behavior is undefined (likely errors or shows everything)

**Establishing a clean baseline:** After initial setup or major firmware changes, run `dt backup` to create a non-pre-agent baseline. This prevents future `dt diff` from showing setup noise.

**Why:** Pre-agent backups are snapshots taken during initial FC discovery or setup. They include ephemeral state that changes every session (alignment registers, aux mode history, etc.). Comparing against long-term history creates noisy diffs. Using the most recent "clean" baseline gives you only the actual changes since last manual baseline.

**How to apply:** 
- After FC setup is complete, run `dt backup` to stamp a known-good baseline
- When running `dt diff` before making changes, verify the baseline file path is recent and non-pre-agent
- If `dt diff` output is noisy with alignment/aux changes, it's using a pre-agent baseline — create a new baseline first
