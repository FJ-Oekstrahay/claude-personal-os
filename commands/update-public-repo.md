Update the public repo and GitHub Pages landing page. Use batchc methodology: read everything first, classify what's stale, then write in parallel where files don't conflict.

## Phase 1 — Read (parallel)

Read all of these simultaneously:
- `~/.openclaw/public-sync/claude-personal-os/README.md`
- Every README.md in subdirectories of `~/.openclaw/public-sync/claude-personal-os/` (check: commands/, docs/, hooks/, skills/, selected-playbooks/, agent-memory/)
- `~/.openclaw/workspace/projects/git-public-repo/pages/draft.md`
- `~/.openclaw/workspace/projects/git-public-repo/pages/index.html`
- The actual contents of each subdirectory to understand current state: `ls` each one

## Phase 2 — Classify

For each README: is it accurate? Is anything missing or stale? Only flag what's actually wrong — don't rewrite for cosmetic reasons.

For index.html: does it reflect what draft.md says the intent is? Is any content outdated relative to the current system state?

## Phase 3 — Write (parallel where no file conflicts)

Update only the files that need changes. For READMEs: fix stale sections, add missing sections, remove things that no longer exist. Keep the existing voice and structure unless it's broken.

For index.html: update to reflect current system state per draft.md intent. Do not change the visual design or layout — only update text content that is stale or missing.

Paths are fixed:
- Public repo root: `~/.openclaw/public-sync/claude-personal-os/`
- Pages source: `~/.openclaw/workspace/projects/git-public-repo/pages/index.html`

## Phase 4 — Commit and push

In `~/.openclaw/public-sync/claude-personal-os/`:

```
git add -A
git commit -m "docs: update READMEs and landing page to reflect current state"
git push origin
```

If there are no changes to commit, say so and stop — do not create an empty commit.

After pushing, confirm what changed and what was already accurate.
