# Selected Playbooks

Playbooks are persistent lessons extracted from real incidents and patterns — not documentation written in advance, but constraints written after something went wrong or a non-obvious pattern was confirmed. Each file records what happened, why it happened, and how to apply the constraint going forward.

---

## The memory stack

Three distinct retrieval mechanisms coexist, each solving a different problem:

**Playbook library (~359 entries)** — Structured domain knowledge written deliberately after debugging failures. Covers FC/Betaflight serial quirks, USB HID gadget mode, macOS scripting gotchas, hook exit code semantics, agent behavior patterns, build/CI patterns, and more. Not session observations — constraints extracted from real failures. Format: YAML frontmatter (`what`, `why`, `how` keys) followed by prose. The frontmatter is machine-searchable; the prose is the actual incident.

**memsearch (Claude Code plugin v0.4.4)** — Semantic vector search over prior session transcripts. Uses ONNX bge-m3 embeddings (~558 MB model, runs entirely on-device, no API call). Vector store: Milvus-lite 2.5 at `~/.memsearch/milvus.db`. A Stop hook auto-captures session transcripts and queues them for indexing. Collections are per-project (per git root). At session start, memsearch injects semantic search hints from prior sessions into the context. Best for "have I seen this error before" and "what did I decide about X" queries — open-ended recall where keyword precision loses to semantic similarity.

**Custom MCP memory server (`mcp-memory-server.py`, ~160 LOC)** — Local stdio MCP server exposing the playbook library directly to Claude Code as tools. Three tools: `list_memory()` (compact index, ~500 tokens), `get_memory(name)` (full file by filename), `search_memory(query)` (keyword grep over ~240 markdown files, ~50ms). Preferred over memsearch for playbook lookup because playbooks are structured domain knowledge where keyword precision beats semantic similarity — "betaflight save" finds the right file; embedding similarity might not.

**Auto-memory (Anthropic, Feb 2026)** — Writes session observations automatically. Different job from the other two: it captures what Claude noticed during a session, not structured domain knowledge or full transcripts. All three coexist without conflict.

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
