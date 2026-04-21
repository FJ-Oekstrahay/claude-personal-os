---
name: Model tiering in Claude Code sessions
description: Geoff wants Haiku for recon, Sonnet for scoped execution, Opus for planning/architecture — never waste Opus on file reads or Haiku on edits
type: feedback
---

Break work into model tiers: Haiku (search/verify), Sonnet (execute known plans), Opus (plan/architect/review). Start sessions in Sonnet for classification, then Geoff switches models and says "do the [tier] part."

**Why:** Geoff is burning through token budget having Opus and Sonnet do work that cheaper models handle fine. Opus file-reading sessions are especially wasteful.

**How to apply:** When Geoff describes a task, classify it into tiers before acting. Present the breakdown. Don't search files or read code in Opus — delegate that to Haiku or subagents. Full playbook at `workspace/memory/playbooks/claude_code_model_tiering.md`.
