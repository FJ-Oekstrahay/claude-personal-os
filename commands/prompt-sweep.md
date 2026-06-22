# Prompt Sweep

Sweep the current project's `prompts/` directory, assess completion status of each prompt, archive completed ones, and report a summary.

## Steps

### 1. List prompts

List all `.md` files in `<project-cwd>/prompts/` excluding `prompts/archive/`:

```
find <project-cwd>/prompts -maxdepth 1 -name "*.md"
```

If the directory does not exist or is empty, report that and stop.

### 2. Assess each prompt

Read each file briefly and assign one of these statuses:

- **DONE** — The deliverable is committed or published, no open questions remain, and no follow-up action is pending in `OPEN-TOPICS.md` or advisor notes. The prompt has served its purpose and will not be needed again.
- **PENDING** — Work has not started or is blocked. Leave in `prompts/`.
- **IN-PROGRESS** — Work is underway but not complete. Leave in `prompts/`.
- **STANDING** — A recurring template (quarterly sweep, periodic review, etc.). **Never archive these.** Leave in `prompts/`.

When in doubt, leave it in `prompts/`. Prefer false negatives (leave too many) over false positives (archive something still needed).

To assess DONE accurately, check:
- Whether the prompt's output (report, file, commit, analysis) exists in the repo or was delivered
- Whether `OPEN-TOPICS.md` references any open items from this prompt
- Whether `advisor-notes/conversation-log.md` shows the work as complete with no pending follow-up

### 3. Archive DONE prompts

For each prompt assessed as DONE, move it to `prompts/archive/`:

```
mv <project-cwd>/prompts/<filename>.md <project-cwd>/prompts/archive/<filename>.md
```

Create `prompts/archive/` if it does not exist.

### 4. Update prompts/archive/AAA-archived.md

Open or create `<project-cwd>/prompts/archive/AAA-archived.md`.

If prompts were moved: add a dated section with today's date, listing each archived prompt and a one-line reason why it was archived (what deliverable was completed, what the status was).

If nothing was moved: add a brief dated entry noting the sweep ran with no changes.

Format:

```markdown
## YYYY-MM-DD

- **prompt-name.md** — [reason archived: deliverable completed / output committed / etc.]
```

Append new sections at the top of the file (most recent first) if the file already exists.

### 5. Report summary

Return:
- Total prompts reviewed
- How many moved to archive
- Names and one-line reason for each archived prompt
- Names of any STANDING prompts (so the user knows they were seen and intentionally left)
- Any prompts that were ambiguous — briefly note why you left them in place
