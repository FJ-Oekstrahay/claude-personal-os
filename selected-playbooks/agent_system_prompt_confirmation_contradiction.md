---
name: AGENT_SYSTEM confirmation contradiction removal
description: Conflicting workflow steps (ask for confirmation vs no confirmation) cause unwanted "Confirm to apply?" on every response
type: feedback
---

**Rule**: AGENT_SYSTEM workflow steps must not contradict each other. Step 4 ("Ask for confirmation before applying") conflicts with safety section ("don't gate commands behind confirmation"). Remove the conflicting step if gatekeeping is not desired.

**Symptom**: Agent appends "Confirm to apply?" to every response even when commands are safe and pre-approved. Users must acknowledge every action.

**Why**: Two competing instructions in the same system prompt both fire. Confirmation handler waits indefinitely for user ack, even for benign operations (like reading radio battery-alert status).

**How to apply**: 
- Review AGENT_SYSTEM in cli/agent.py for workflow step ordering
- If the intent is "warn but don't block", remove the confirmation requirement from workflow steps
- Keep safety warnings in place (e.g., "this changes motor params, verify...") but remove explicit "ask user to confirm" instruction
- Test with `dt agent` dry-run to verify no trailing confirmation prompts
