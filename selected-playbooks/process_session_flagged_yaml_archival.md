---
name: Process-Session Flagged YAML Archival
description: Archive processed flagged YAMLs to logs/flagged_processed/ to prevent re-surfacing in future process-session runs
type: feedback
---

## Rule

After running `process-session` and applying approved changes, archive all processed flagged YAML files from `logs/flagged_*.yaml` to `logs/flagged_processed/`. This prevents them from re-appearing in future `process-session` inventory scans.

**Why:** The `process-session` skill scans `logs/flagged_*.yaml` files to inventory session artifacts. Without archival, fixed flags reappear on every run, creating duplicates in the review file and noise in subsequent process-session sessions. Archive signals "this flag has been reviewed and acted upon."

**How to apply:**

In the `process-session` workflow, after Step 6 (apply approved items):

1. List all files in `logs/flagged_*.yaml` that were processed:
   ```bash
   ls -1 logs/flagged_*.yaml
   ```

2. Move them to `logs/flagged_processed/`:
   ```bash
   mv logs/flagged_*.yaml logs/flagged_processed/ 2>/dev/null
   ```

3. Verify the directory exists (create if needed):
   ```bash
   mkdir -p logs/flagged_processed
   ```

4. Do not commit archived files — they're runtime artifacts only. Add to `.gitignore` if not already present:
   ```
   logs/flagged_processed/
   ```

## Related pattern

**Cross-reference prior session-review files** before running process-session to avoid re-processing old flags:

1. Check for existing `logs/session-review-*.md` files from prior runs
2. If a flag is already handled (listed in an older session-review), don't re-include it in the current run
3. Prioritize new flags over old ones in the review file

## Example

```bash
# After process-session completes and changes are committed:
ls logs/flagged_*.yaml 2>/dev/null | xargs -I {} mv {} logs/flagged_processed/

# Verify:
ls logs/flagged_processed/  # Should list the archived files
ls logs/flagged_*.yaml 2>/dev/null  # Should be empty or non-existent
```

## Related

- [[process_session_command]] — the parent process-session skill that orchestrates artifact processing
- [[agent_system_stale_capability_instruction]] — common flagged pattern: stale capability instructions
