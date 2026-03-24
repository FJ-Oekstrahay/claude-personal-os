---
name: Lessons learned from bootstrap session
description: Mistakes made during Claude Code bootstrap — hook contracts, permissions, git staging, skills
type: feedback
---

When writing Claude Code hooks:
- Exit 2 blocks. Exit 0 allows. Exit 1 does NOT block — it's non-blocking.
- Block reasons go to stderr, not stdout. Claude only sees stderr.
- Matcher covers tool names. `Write|Edit` misses all Bash-based writes. Include `Bash`.
- Fail closed: if parsing fails, exit 2, not 0.
- `tool_input` is the correct JSON key in PreToolUse payloads.

**Why:** Shipped a hook with exit 1, stdout messages, and no Bash coverage — the entire protection layer was ineffective until The Architect caught it.

**How to apply:** Any time I write a PreToolUse hook, check all four of these before finishing.

---

When writing permission allow-lists:
- `Bash(git *)` is too broad — auto-approves `push --force`, `reset --hard`, `clean`.
- Always add deny rules for `kill`, `pkill`, `killall` when a live process must be protected.

**Why:** Broad git allow let destructive operations through without confirmation.

---

When staging files in git:
- Read the file before staging, even if it looks like a non-secret identifier. `identity/device.json` looked like a device ID but contained a plaintext private key.

**Why:** Almost committed a private key in the initial baseline commit.

---

When writing skills that reference files or directories:
- If a skill writes to a directory, add `mkdir -p` — directories don't auto-create.
- If a skill reads from a file containing secrets (e.g., openclaw.json), specify the exact `jq` extraction — don't instruct reading the whole file. Tokens end up in context.

**Why:** compact-checkpoint would fail on first use; openclaw-status and debug-agent would dump live tokens into context window.
