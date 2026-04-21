---
name: project_memory_troubleshooting
description: Cross-agent memory search reliability — root causes, fixes applied, architecture decisions
type: project
---

## Problem
Cheaper LLM agents (GPT-4.1-mini, Haiku) don't reliably search memory before starting tasks, even with tools available and instructions present.

## Test Results (2026-03-24 through 2026-03-25)
- Bob (Haiku): PASS when told "search your memory"
- Gerbilcheeks (Haiku): PASS when told "search your memory"
- Gerbilcheeks (GPT-4.1-mini): FAIL even when explicitly told — model not capable enough

## Root Causes and Fixes Applied (2026-03-25)

### Phase 1 fixes (2026-03-24):
1. Added `group:fs` to Gerbilcheeks
2. Added `group:memory` to Bob and Gerbilcheeks
3. IDENTITY.md now points directly to AGENTS.md (was going through GOVERNANCE.md)

### Phase 2 fixes (2026-03-25):
4. **Switched Gerbilcheeks from GPT-4.1-mini to Haiku** — mini can't reliably follow system prompt instructions
5. **Created AGENTS-WORKER.md** — extracted worker-only standing orders from AGENTS.md (240 lines of orchestrator content was diluting instructions for workers). Workers now read AGENTS-WORKER.md instead of AGENTS.md.
6. **Restructured IDENTITY.md** — memory search is now the mandatory first step (before reading any other file), with imperative language and "do not skip" guardrails
7. **Added memory search to AGENTS.md standing orders** — step 0 in MoltyJoe's mandatory checklist, so orchestrator also searches before delegating
8. **Task envelope preamble** — delegation playbook now requires "FIRST: Call memory_search" at the top of every task string, because worker models fixate on user-turn content over system prompt

## Architecture Decision
- Workers (Bob, Gerbilcheeks) read `AGENTS-WORKER.md` (focused, ~60 lines)
- Orchestrator (MoltyJoe) reads `AGENTS.md` (full routing/delegation/cost rules)
- No duplication — shared rules live in AGENTS-WORKER.md, AGENTS.md is orchestrator-specific

## Tool Group Reference
- `group:fs` -> read, write, edit, apply_patch
- `group:runtime` -> exec, process
- `group:memory` -> memory_search, memory_get
- `group:sessions` -> sessions_list/history/send/spawn, subagents, session_status
- `group:messaging` -> message
- `group:web` -> web_search, web_fetch
- `group:automation` -> cron, gateway
- `group:ui` -> browser, canvas
- `group:agents` -> agents_list
- `group:media` -> image, tts

**Why:** Understanding tool groups is critical — agents silently lack capabilities when groups are missing.

**How to apply:** When an agent can't do something, check its tool group allow list against this mapping. When changing agent behavior, check if the instruction structure works for the model class (cheap models need imperative user-turn instructions, not just system prompt hints).

## Final State (2026-03-25)
Instruction-following approach has a ceiling — cheap models are probabilistic about system prompt instructions even with imperative language and restructured IDENTITY.md. "Search your memory" still needs to be in the prompt for reliability.

Accepted workaround: include "search your memory" proactively or when something goes wrong.

Better fix (not implemented): have MoltyJoe pre-load memory search results into the task envelope before spawning workers (Option A). Reliable because Sonnet does the search. Only covers spawned sessions, not direct-chat. Deferred.
