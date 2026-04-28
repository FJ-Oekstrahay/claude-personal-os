# Selected Playbooks

Playbooks are constraints extracted from real incidents and confirmed patterns — written after something went wrong or a non-obvious approach was validated, not in advance. Each file records what happened, why it happened, and how to apply the constraint. The frontmatter is machine-searchable; the prose is the full lesson.

This is a curated subset of a larger library. Excluded: project-specific playbooks that require private context to interpret.

---

## Categories in this selection

**Agent behavior** (7 entries) — How multi-agent systems fail and how to prevent it. Covers context injection gaps, model selection for instruction-following, system prompt execution model, stale capability instructions, and persona drift. The most transferable category for anyone building with Claude agents.

**Claude Code / AI tooling** (6 entries) — Constraints specific to Claude Code and the Anthropic API: multimodal content field format, batch skill invocation constraints, Edit tool unicode failures, safety language in system prompts, the four-role review sequence protocol, and skill spawn patterns.

**CLI / shell / scripting** (5 entries) — Gotchas that burn time in practice: macOS BSD sed vs. GNU sed differences, Homebrew Python venv requirements, subparser completeness for CLIs, signal handling for interrupt propagation, and the pre-search codebase check before writing new specs.

**macOS / infrastructure** (4 entries) — launchd cron patterns, device path vs. file path distinction, FAT32 permissions behavior on macOS, and public/private repo sync durability.

**Testing patterns** (5 entries) — Dev-volume flag pattern for toggling test behavior, hardware isolation testing, mock daemon virtual testing, serial port contention, and serial delimiter false positives. Useful for embedded and hardware-adjacent work.

**APIs / integrations** (4 entries) — API key placement UX friction, config diff completeness, pandoc DOCX image extraction, and Pillow EXIF stripping for JPEG/WebP.

**Python** (2 entries) — Async global flag patterns and YAML parsing edge cases in venv environments.

**Cloudflare Workers** (2 entries) — KV namespace gotchas and user-agent bypass patterns.

**Planning / research** (1 entry) — CTO-role triage for research questions: when to investigate vs. decide.

---

## How to use these

Searchable by keyword — filename convention is `{domain}_{topic}.md`. Start with **Agent behavior** and **Claude Code / AI tooling** if you're building with Claude.

When Claude references a playbook constraint in a response, the source file is the canonical explanation. The frontmatter `why` field is the concise version; the prose is the full incident.
