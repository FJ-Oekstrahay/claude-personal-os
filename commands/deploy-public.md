Audit and update the public repo README files and landing page, then commit and push.

## Context

- Source of truth: `~/.claude/` (local config). Public mirror: `~/.openclaw/public-sync/claude-personal-os/` (rsync mirror of `~/.claude/`).
- Sync script: `~/.openclaw/bin/sync-claude-to-public.sh` — rsyncs `~/.claude/` to the public repo and auto-commits. It **wipes** `docs/` and any non-synced directories on each run.
- Landing page source: `~/.openclaw/workspace/projects/git-public-repo/pages/` (`index.html`, `hero.jpeg`). These must be manually restored to `docs/` after every sync because sync wipes `docs/`.
- Public repo: `~/.openclaw/public-sync/claude-personal-os/`

**TODO (long-term fix):** Update `sync-claude-to-public.sh` to add `--exclude 'docs/'` to the rsync call so the landing page survives syncs automatically. The command currently re-deploys manually as a workaround.

## Step 1: Audit README files

Read the following files. For each, compare against the current state of `~/.claude/`:

**In `~/.openclaw/public-sync/claude-personal-os/`:**
- `README.md` (top-level)
- `hooks/README.md`
- `commands/README.md` (if it exists)
- `skills/README.md` (if it exists)
- `skills/personal-infrastructure/README.md` (if it exists)
- `selected-playbooks/README.md` (if it exists)

**Landing page:**
- `~/.openclaw/workspace/projects/git-public-repo/pages/index.html`

For each README, update any descriptions that are:
- Stale (referencing hooks, commands, or behaviors that have changed)
- Missing (new files/hooks not yet mentioned)
- Inaccurately framed

Rules:
- Do NOT invent features that don't exist in `~/.claude/`
- Do NOT use "dotfiles" framing — this is a behavioral and operational configuration layer
- Keep descriptions terse; the user prefers no marketing language
- README edits go in `~/.claude/` (source), not directly in the public-sync mirror — the sync script propagates them

**Do NOT edit `~/.openclaw/public-sync/claude-personal-os/` READMEs directly.** Edit `~/.claude/` counterparts, then run the sync.

## Step 2: Run the sync

```
~/.openclaw/bin/sync-claude-to-public.sh
```

This rsyncs `~/.claude/` to `~/.openclaw/public-sync/claude-personal-os/` and auto-commits. Note the commit SHA.

## Step 3: Restore the landing page

After sync wipes `docs/`:

```
cp ~/.openclaw/workspace/projects/git-public-repo/pages/index.html \
   ~/.openclaw/public-sync/claude-personal-os/docs/index.html

cp ~/.openclaw/workspace/projects/git-public-repo/pages/hero.jpeg \
   ~/.openclaw/public-sync/claude-personal-os/docs/hero.jpeg
```

## Step 4: Commit and push docs/

In `~/.openclaw/public-sync/claude-personal-os/`:

```
git add docs/index.html docs/hero.jpeg
git commit -m "site: redeploy landing page + restore hero.jpeg

Co-Authored-By: Claude Sonnet <noreply@anthropic.com>"
git push origin main
```

## Step 5: Report back

Return:
- Files touched in `~/.claude/` (one-line summary per file)
- Sync auto-commit SHA
- Docs re-deploy commit SHA
- Push result (success / error output)
