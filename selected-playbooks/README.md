# Selected Playbooks

Playbooks are persistent lessons extracted from real incidents and patterns — not documentation written in advance, but constraints written after something went wrong or a non-obvious pattern was confirmed. Each file records what happened, why it happened, and how to apply the constraint going forward.

Format: YAML frontmatter (`what`, `why`, `how` keys or equivalent) followed by prose. The frontmatter is designed to be machine-searchable; the prose is the actual lesson.

This is a curated subset of a larger library (~220 entries). Excluded: project-specific playbooks for DroneTeleos, Jarface, personal financial tooling, and BMX sourcing — entries that only make sense with private context.

> **On what's native vs. custom:** Claude Code ships with an auto-memory system that captures behavioral feedback across sessions. The memsearch plugin indexes session transcripts for semantic recall. Neither produces what's in this directory. Playbooks are written after something breaks — they encode root cause, constraint, and how to apply the lesson going forward. That format doesn't emerge automatically from session memory. The notes below each category explain what, if anything, overlaps with native Claude Code features and why these particular lessons are still worth reading.

---

## Categories in this selection

**Agent behavior** — How multi-agent systems fail and how to prevent it. Model selection for instruction-following, context injection gaps, system prompt execution model, third-person language removal. These are the most transferable lessons for anyone building with Claude agents.

> No native equivalent. Anthropic's documentation covers what agents *can* do; these playbooks cover what goes wrong in multi-agent systems and why — confirmation loops, context injection gaps, model tier selection tradeoffs under real instruction load. Derived from extended production use.

**Claude Code / hooks** — Exit codes, matcher scope, fail-closed design, Discord channel access, model tiering. The companion to the `hooks/` directory in this repo.

> Now partially in official docs. Still worth reading: the playbooks here frame these as production failure post-mortems — what broke, why, and the specific constraint that prevents it recurring. That framing is more useful for building intuition than reference documentation covering the same facts.

**macOS / shell scripting** — BSD sed vs. GNU sed gotchas, Homebrew Python venv requirements, FAT32 permissions, shell error propagation with `set -euo pipefail`. Practical scripting constraints specific to macOS development environments.

> No native equivalent. These are macOS-specific gotchas that only surface in production use — BSD sed behaves differently from GNU sed in ways that break scripts that work fine on Linux CI. Not in any Anthropic documentation.

**Betaflight / FC / hardware** — CLI parameter renames, `save` command serial port behavior, MSP framing, blackbox analysis, OSD coordinate validation. Technical notes about public tools, not project-specific configuration.

> No native equivalent. Domain-specific. Useful if you're doing any FC tooling work.

**Cloudflare Workers** — KV namespace gotchas, user-agent bypass patterns, rate limiting. Short but precise.

**Review and planning protocols** — The four-role adversarial review sequence (Critic, Gadfly, Architect, CTO), sequencing rules, when to escalate to Opus. Pairs with the `/review-sequence` command.

> Gadfly, CTO, Critic, and The Architect now ship as default Claude Code agents. Still worth reading: the sequencing rule (Gadfly before CTO) and when to escalate to a more capable model aren't documented by Anthropic. The playbooks here explain the reasoning behind the sequence, not just the sequence itself.

**Infrastructure / ops** — launchd cron patterns, git backup, public/private repo sync, token migration verification, signal handling.

> No native equivalent. macOS launchd and git sync pipeline specifics that aren't covered anywhere else.

**Python** — venv requirements, ARM64 porting, async global flags, YAML parsing edge cases.

> No native equivalent. Production-discovered Python gotchas, particularly on Apple Silicon.

---

## How to use these

These are searchable by keyword — filename convention is `{domain}_{topic}.md`. The most valuable entries for Claude Code users are in the **Agent behavior** and **Claude Code / hooks** categories.

When Claude references a playbook constraint in a response, the source file is the canonical explanation. The frontmatter `why` field is the concise version; the prose is the full incident.

This directory is regenerated nightly by the sync script from the full playbook library.

