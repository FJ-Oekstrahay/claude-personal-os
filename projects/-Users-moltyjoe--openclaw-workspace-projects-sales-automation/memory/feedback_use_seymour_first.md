---
name: Use Seymour first for mechanical work
description: Default to delegating mechanical coding/file work to Seymour (Haiku); only hold it at Sonnet when judgment is needed
type: feedback
---

Always delegate mechanical work to Seymour (Haiku subagent) unilaterally — don't ask Geoff, just do it.

**Why:** Geoff's main concern is Sonnet doing mechanical work that Haiku could handle. Mechanical = well-specified file edits, shell commands, CLI execution, reading files for known patterns.

**How to apply:**
- When a task has a clear spec and doesn't require judgment → spawn Seymour
- When Seymour returns a plan/asks for approval → tell it to proceed (it's already Haiku, no need to escalate)
- Only keep work at Sonnet when: debugging unclear failures, synthesizing complex results, making architectural decisions
- Only present a tier split to Geoff when Opus is involved
- Seymour CAN edit files, write code, run shell commands — the restriction is on architectural decisions and ambiguous debugging, not editing
