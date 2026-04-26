---
name: dt agent startup diff comparison scope
description: Agent startup diff should compare against previous session pre-agent backup, not long-term history
type: feedback
---

When running startup diff on an agent-controlled FC, the comparison baseline should be the **previous session's pre-agent backup**, not archived backups from many sessions ago.

**Problem:** Comparing against long-term history backups produces noisy diffs with aux mode changes, alignment register drift, and other ephemeral state that cycles every session. These aren't "real" config changes; they're hardware state that naturally evolves.

**Solution:** Use the most recent pre-agent backup (the one taken at the start of the previous session when the agent was spinning down) as the baseline.

**Why:** Pre-agent backups mark the moment before the agent resumed control, capturing the "clean" state from last session's shutdown. Comparing the new pre-agent backup against this one shows only config changes the agent made, filtering out natural state drift.

**How to apply:** 
- When implementing `dt agent startup` workflows, compare `${CURRENT_SESSION_PRE_AGENT}` against `${PREVIOUS_SESSION_PRE_AGENT}`
- Do not use `dt diff --from-archive` or oldest-backup patterns for agent startup checks
- Pre-agent backups are already marked with metadata — use that to select the right baseline
