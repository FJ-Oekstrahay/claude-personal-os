# Selected Playbooks

Playbooks are persistent lessons extracted from real incidents and patterns — not documentation written in advance, but constraints written after something went wrong or a non-obvious pattern was confirmed. Each file records what happened, why it happened, and how to apply the constraint going forward.

Format: YAML frontmatter (`what`, `why`, `how` keys or equivalent) followed by prose. The frontmatter is designed to be machine-searchable; the prose is the actual lesson.

This is a curated subset of a larger library (~150 entries). Excluded: project-specific playbooks for DroneTeleos, Jarface, personal financial tooling, and BMX sourcing — entries that only make sense with private context.

---

## Categories in this selection

**Agent behavior** — How multi-agent systems fail and how to prevent it. Model selection for instruction-following, context injection gaps, system prompt execution model, third-person language removal. These are the most transferable lessons for anyone building with Claude agents.

**Claude Code / hooks** — Exit codes, matcher scope, fail-closed design, Discord channel access, model tiering. The companion to the `hooks/` directory in this repo.

**macOS / shell scripting** — BSD sed vs. GNU sed gotchas, Homebrew Python venv requirements, FAT32 permissions, shell error propagation with `set -euo pipefail`. Practical scripting constraints specific to macOS development environments.

**Betaflight / FC / hardware** — CLI parameter renames, `save` command serial port behavior, MSP framing, blackbox analysis, OSD coordinate validation. Technical notes about public tools, not project-specific configuration.

**Cloudflare Workers** — KV namespace gotchas, user-agent bypass patterns, rate limiting. Short but precise.

**Review and planning protocols** — The four-role adversarial review sequence (Critic, Gadfly, Architect, CTO), sequencing rules, when to escalate to Opus. Pairs with the `/review-sequence` command.

**Infrastructure / ops** — launchd cron patterns, git backup, public/private repo sync, token migration verification, signal handling.

**Python** — venv requirements, ARM64 porting, async global flags, YAML parsing edge cases.

---

## How to use these

These are searchable by keyword — filename convention is `{domain}_{topic}.md`. The most valuable entries for Claude Code users are in the **Agent behavior** and **Claude Code / hooks** categories.

When Claude references a playbook constraint in a response, the source file is the canonical explanation. The frontmatter `why` field is the concise version; the prose is the full incident.

This directory is regenerated nightly by the sync script from the full playbook library.
