Produce a proposed batchc wave plan for this session. Do NOT dispatch any work — stop and present for approval only.

## Step 1 — Find the most recent handoff

Run:
```
ls -t "$(pwd)"/HANDOFF-*.md 2>/dev/null | head -1
```

If that returns nothing, fall back to:
```
ls -t ~/.openclaw/workspace/HANDOFF-*.md 2>/dev/null | head -1
```

If still nothing, note "no handoff found" and skip to Step 3.

Read the full handoff file found.

## Step 2 — Read OPEN-TOPICS.md if present

Check whether `"$(pwd)"/OPEN-TOPICS.md` exists. If it does, read it in full. If not, skip silently.

## Step 3 — Read the project board summary

Read the first 30 lines of `~/.openclaw/workspace/BOARD.md`. If the file doesn't exist, skip silently.

## Step 4 — Produce the wave plan

Using what you've read, emit a proposed batchc wave plan. Format:

```
## Proposed Session Wave Plan

**Source:** [handoff filename] + [OPEN-TOPICS.md if found] + BOARD.md

### Wave 1 (parallel)
- [Task A] — [Haiku | Sonnet] — reason
- [Task B] — [Haiku | Sonnet] — reason

### Wave 2 (after Wave 1)
- [Task C] — depends on A — [Haiku | Sonnet] — reason

### Deferred / out of scope
- [anything in the handoff marked blocked or someday]

**Model routing rationale:** [one line — why you chose Haiku vs Sonnet for each task]
```

Model routing rules (batchc §7b):
- **Haiku**: mechanical edits, fully-enumerated spec, single-file, failure obvious on inspection
- **Sonnet**: judgment calls, cross-file consistency, governance/playbook text, ambiguous spec, output feeds downstream reasoning

## Step 5 — Stop

Present the wave plan. Do not execute anything. Wait for the user to approve, modify, or reject before taking any action.
