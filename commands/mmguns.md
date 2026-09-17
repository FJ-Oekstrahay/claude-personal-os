---
description: Research-to-integration workflow — find SOTA for a capability area, compare against current project, produce ranked actionable improvements and dispatch.
---

# /mmguns <topic> [-- <flags>]

Run a research-to-integration workflow for the capability area named in `<topic>`. This is not a research report. The output must drive immediate action: a quick win gets implemented, a medium lift gets a spec stub, a non-starter gets ruled out with reasoning.

## Argument parsing

The user invokes this as `/mmguns <topic> [-- <flags>]`. Parse `$ARGUMENTS`:

- Everything before the first `--` is the topic. Treat it as a single concept even if multi-word ("memory compression", "model selection and cost optimization").
- Everything after `--` is flags. Recognize:
  - `--global` — also scan `~/.openclaw/workspace/` and `~/.claude/` during inventory, in addition to the current project.
  - `--implement` — skip the confirm step. If #1 is a quick win, implement it immediately.
  - `--spec` — force spec output even if #1 qualifies as a quick win.

If no topic was provided, ask for one and stop. Don't guess.

## Stack inference

Before searching, infer the current project stack so Phase 1 queries are relevant:

- Check `requirements.txt`, `pyproject.toml`, `package.json`, `Cargo.toml`, `go.mod` in the cwd and parents.
- Note dominant file extensions in the project root.
- Read the top-level `CLAUDE.md` if present — it often states the stack and constraints explicitly.

Hold the inferred stack in mind for Phase 1 queries and Phase 3 non-starter classification. Don't recommend a TypeScript-only library in a Python project without flagging the mismatch.

---

## Phase 1 — Research (silent; do not narrate)

The topic may point to tools, libraries, processes, workflows, or methodologies — cover all of these. A search for "eval methodology" should surface process improvements (how to structure tests, what to run in CI vs. locally) as well as tool choices.

**Use batchc dispatch for the search wave.** Classify the searches as parallel (all independent), issue all three in the same wave, merge before proceeding. Do not run them sequentially.

Run at least four WebSearch calls with different angles. Suggested templates (adapt to the topic):

1. `<topic> best practices 2025` or `<topic> state of the art 2025`
2. `<topic> production libraries <inferred-stack>` — tool/library angle
3. `<topic> comparison OR benchmark OR versus` — surface community "X vs Y" discussions
4. `<topic> patterns OR methodology OR workflow` — surface process and approach improvements, not just tool choices

Run these in parallel (single batchc wave). After the searches return:

- Pick the 2-3 most promising results and use WebFetch to read the actual content. Do not summarize from link titles alone.
- For each meaningful finding, assess two axes explicitly:
  - **Maturity**: experimental / early-adopter / production-grade / battle-hardened
  - **Relevance**: which stack/context it targets, and whether that matches the current project

Weighting rules:

- Prefer sources from the past 12 months. When two sources conflict, prefer 2025 / late 2024 over 2022-2023, unless the older source is a foundational paper or authoritative official documentation.
- Production-grade signals: >1k GitHub stars AND a commit within ~3 months, named production users, stable (post-1.0) API, active issue triage.
- Experimental signals (flag clearly): pre-1.0 with "API may change", <6 months old with no named users, research paper with no production implementation, single maintainer with no community adoption.
- A fringe approach that one blogger swears by is "interesting, not yet consensus." Note it as such; do not rank it #1.

Do not show search queries or raw search results in the output. Synthesize.

---

## Phase 2 — Inventory (silent; do not narrate)

Scan the current project for existing work on this topic. Read files, don't just grep — a single sentence in a CLAUDE.md can rule out an entire approach.

**Use batchc dispatch for the inventory reads.** The six checks below are independent — classify as parallel, issue in a single wave, merge before Phase 3. Do not read them one at a time.

Check, in order (dispatched in parallel):

1. `CLAUDE.md` files: project root, workspace root, and `~/.claude/CLAUDE.md`. Look for prior decisions, known gotchas, constraints.
2. `specs/` directory in the current project — any spec touching this capability area. Note status (DRAFT / APPROVED / SHIPPED / REJECTED).
3. Memory files: project memory (e.g. `memory/`), agent memory (e.g. `.claude/agent-memory/`), and the user-level auto-memory (`~/.claude/projects/.../memory/MEMORY.md`).
4. Package manifests: `requirements.txt`, `pyproject.toml`, `package.json`, etc. — what's already installed.
5. Source code: grep for plausible imports, class names, function names, and file names related to the topic. Read the hits, don't just list them.
6. Project board: `~/.openclaw/workspace/projects/project-board/BOARD.md` — is there active or blocked work on this topic.

If `--global` is set, additionally scan `~/.openclaw/workspace/` and `~/.claude/` (other projects, shared skills, shared memory). Otherwise stay scoped to the current project.

Produce a private inventory summary: what exists, where, at what quality level, and any prior decision that constrains the recommendation.

---

## Phase 3 — Gap analysis (silent; do not narrate)

Compare Phase 1 findings against the Phase 2 inventory. Classify every candidate improvement into exactly one bucket:

**Quick win** — implement now, no spec needed. All of:
- Touches ≤2 files
- Doesn't change API or persistent data contracts
- Adds no new user-facing command or output format
- Reversible within one session
- Geoff can review the diff in ~5 minutes

**Medium lift** — needs a spec first. Any of:
- Creates new persistent data (files, schemas, build profiles)
- Adds a new user-facing command or output format
- Touches >2 files or crosses >1 system boundary
- The right approach isn't obvious yet (the spec is the thinking tool)

**Non-starter** — wrong fit. Any of:
- Wrong stack (e.g. Node-only library in a Python project)
- Requires infrastructure that doesn't exist and isn't worth building for this use case
- Solves a problem this project doesn't have
- Experimental maturity with no production track record

Be honest about non-starters — ruling things out is as valuable as identifying what to do. Keep at most three items total in the brief. If there are six candidates, rank and drop. A list of three with clear ranking rationale is more useful than six with equal framing.

---

## Phase 4 — Produce the brief

Output exactly this structure. Lead with this — do not narrate the research process before it.

```
## /mmguns: <topic>

### SOTA summary
<2-4 sentences. State the current best approach and the "why" — what problem it solves that older approaches didn't.>

### What you have now
<1-3 sentences on current implementation, or "nothing" if the topic is unaddressed. If a prior decision exists in memory or a spec, cite the file path.>

### Top improvements

**#1 — <name>** [Quick win | Medium lift | Non-starter]
- What: <one line>
- Why this ranks #1: <the ROI argument>
- Complexity: <hours estimate>
- Risk: <Low | Medium | High> — <one-line reason>
- Spec required: Yes | No
- Next action: <specific — "implement X in file Y", "write spec for Z", or "skip — reason">

**#2 — <name>** [Quick win | Medium lift | Non-starter]
(same structure)

**#3 — <name>** [Quick win | Medium lift | Non-starter]
(same structure)

### Dispatch
<One short paragraph describing what happens next — see Phase 5.>
```

Rules for the brief:

- Never more than three recommendations. The user can ask for more.
- Don't quote large blocks of documentation. Synthesize.
- Cite prior decisions by file path, not by re-stating their content.
- No emoji. No fluff. No "here's what I did" preamble.

---

## Phase 5 — Dispatch (close the loop)

After printing the brief, take action based on what #1 is. The whole point is to close the loop — do not stop at "here's a report."

Decision table:

| Situation | Action |
|---|---|
| `--implement` flag set AND #1 is a quick win | Implement #1 immediately. No confirm step. |
| `--spec` flag set | Generate a spec stub for #1 (treat as medium lift regardless of classification). |
| #1 is a quick win (no flag override) | Ask Geoff one short confirm question, then implement on yes. |
| #1 is a medium lift | Generate a spec stub at `specs/<topic-kebab-case>.md` with status DRAFT. Note required reviews. Do not write code. |
| #1 is a non-starter AND #2 is a quick win | Implement #2 instead. Don't let a non-starter at the top block action. |
| Everything is medium lift or non-starter | Stop after the brief. Let Geoff pick which to spec first. |

### Implementing a quick win

If the implementation work is clearly bounded — specific files, no ambiguity, no judgment calls — dispatch it to a Cob subagent. End the Cob prompt with this exact line:

> Return only: files touched, one-line summary per file. No diffs, no code blocks, no file contents.

If the work needs judgment as you go (e.g. unclear API shape, multiple reasonable approaches surfacing only when reading the code), do it inline in the main context. Never relay code blocks or diffs from a subagent into the main context — condense to one line per file.

### Generating a spec stub

Check whether `specs/TEMPLATE.md` exists in the current project. If it does, copy that structure. Otherwise use this minimal structure:

```
# <topic title>

_Status: DRAFT_
_Created: <today's date>_

## Problem
<1-2 paragraphs. What's broken or missing, who feels the pain.>

## Proposed approach
<What we'd build. Based on the SOTA finding from /mmguns research.>

## Why this approach
<Trade-offs vs. alternatives surfaced in research.>

## Out of scope
<Explicitly what we are NOT doing in v1.>

## Open questions
<Things the spec author can't answer alone — flag for review.>

## Required reviews
<Gadfly if user-facing. CTO if architectural or new data model. Safety Officer if touches FC writes or hardware safety recommendations. Architect if crosses >1 system boundary or touches >3 files.>
```

After writing the spec, state in chat: which reviews are required, and offer to dispatch the review pipeline. Do not auto-dispatch reviews without confirmation — Geoff may want to read the spec first.

### Spec-first rule (mandatory, no exceptions for fitting cases)

Before writing code for any improvement that:
- Creates new persistent data
- Adds a new user-facing command or output format
- Touches more than two existing files
- Will require ongoing maintenance

…a spec must be written first. The only exceptions are bug fixes, internal tooling, and behavior-preserving refactors. If Phase 3 classified #1 as medium lift, the output is a spec stub — not code. This rule is not negotiable by flag (other than `--implement`, which only applies to a true quick win).

---

## Output discipline (applies to the whole command)

- Lead with the brief. Don't narrate Phase 1-3.
- Don't print search queries or raw search results.
- Don't quote documentation in bulk — synthesize.
- Reference prior decisions by file path; don't re-litigate them.
- The brief plus the dispatch action is the artifact. Everything else is internal process.
- No emoji.

<!--
Design notes (do not print):

0. batchc is used inside phases 1 and 2 for parallel dispatch within each phase. The phases themselves are sequential (each depends on prior results). batchc adds value at the intra-phase level, not the inter-phase level.

1. Single-file command, not decomposed into skills. The five phases are linear with no natural reuse boundary — Phase 2 inventory depends on the project, Phase 3 depends on Phase 1+2, dispatch depends on Phase 3. Splitting would require state-passing across skill invocations with no payoff.

2. Three-recommendation cap is deliberate. Geoff has stated preference for ranked output over comprehensive lists. A six-item list with equal framing is decision-deferral disguised as thoroughness.

3. Dispatch logic intentionally asks for confirm on quick wins by default, with --implement as the override. Defaulting to silent implementation risks landing changes Geoff hasn't seen the rationale for. Defaulting to "ask first" makes the override flag the right tool for trusted topics.

4. Spec template is inlined as a fallback so the command works in projects that don't have specs/TEMPLATE.md. In droneteleo it does exist and will be preferred.

5. Non-starter at #1 with quick win at #2 → implement #2 rule prevents the brief from being action-blocked by a top-ranked impossibility. The ranking is by inherent ROI, but the dispatch follows feasibility.
-->
