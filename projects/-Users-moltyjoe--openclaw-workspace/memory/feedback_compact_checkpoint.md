---
name: Always use /compact-checkpoint
description: When context is heavy and compacting is needed, always advise the user to use /compact-checkpoint (not /compact alone)
type: feedback
---

Always advise the user to use `/compact-checkpoint` when context needs compacting. Do not write checkpoint files manually and then tell him to run `/compact` separately.

**Why:** the user has a custom skill `/compact-checkpoint` that handles the full workflow (writes checkpoint + instructs to compact). Using it consistently avoids confusion and ensures checkpoints are always saved before compacting.

**How to apply:** When context is getting heavy or the user mentions compacting, say "run `/compact-checkpoint`" — not "/compact", not manually writing checkpoint files.
