---
what: Public showcase repo durability under wipe-before-rsync sync
why: Files created directly in the public repo are silently deleted on the next nightly sync because the script wipes the working directory before rsync runs.
how:
  - Any "evergreen" file that should persist must live in the rsync source (~/.claude/).
  - Structural changes needed only for public presentation go in post-rsync transformation steps in the sync script.
  - Before adding a file to the public repo, trace it: "Is this in ~/.claude/? If not, where does it come from?"
  - Use the sync script as the source of truth for what the repo will look like after the next run, not the current repo state.
  - Test durability by mentally running the sync: wipe, rsync, transformations — does the file survive?
---

## The wipe-before-rsync pattern

The sync script deletes the entire working directory before running rsync. This is correct behavior for idempotent syncs — it prevents stale files from accumulating if the source removes something. The public repo always reflects exactly what rsync deposited, plus any post-rsync steps. Nothing more.

The trap is that the public repo looks like a normal git repo. You can create files, commit them, push them — and they'll exist right up until the next nightly run, when the wipe removes them without warning. There's no error. The file is just gone.

## Two categories of durable files

**Source-carried files** live in `~/.claude/` and rsync copies them on every run. This is the default durability path. Any file meant to be a permanent part of the showcase must be mirrored here first, then committed to the private config. The public repo gets it as a side effect of sync.

**Generated artifacts** are files that shouldn't exist in the private source — either because they contain public-specific restructuring, or because they're built from dynamic data (e.g., a README assembled from a directory listing). These survive via post-rsync transformation steps added to the sync script. The script runs them after rsync deposits the source files. Without an explicit transformation step, these files do not exist.

## The specific risk

A file created in the public repo during a work session looks permanent. It's committed. It's pushed. But if it didn't originate from `~/.claude/` and there's no transformation step that generates it, it will be gone after the next nightly run. This is especially dangerous for documentation files, reorganized directory structures, or anything added "just to the showcase."

## How to test durability

For any new file in the public repo, ask:
1. Is it present in `~/.claude/`? If yes, rsync carries it. Done.
2. Is there a post-rsync step in the sync script that generates it? If yes, it's durable as long as that step runs.
3. If neither — it won't survive the next sync. Either mirror it to the source or add a transformation step.

When in doubt, read the sync script. The repo state after the next run is determined by the script, not by what's currently checked in.

## Two sync scripts — keep them in sync

There are two sync scripts: `~/.openclaw/bin/sync-claude-to-public.sh` (runs in cron, private) and `~/.claude/sync-to-public.sh` (rsync'd to the public repo, serves as the public template). They share the SELECTED_PLAYBOOKS allowlist and the post-rsync transformation steps. When you change one, change both — they're not automatically derived from each other.

Concrete failure (2026-04-28): the last session pruned project-specific entries from SELECTED_PLAYBOOKS in the private script but not the public template. The public template had 48 entries (including dt_*, droneteleo_*, jarface_*, betaflight_* project-specific playbooks); the private had 36. On the next nightly sync, the public template would have pushed the unfiltered list back to the repo.

Similarly: step 5d in both scripts was still generating a thin stub `selected-playbooks/README.md` that overwrote the rsync-carried version. Fix was applied to both scripts in the same session as the pruning, but the public template was lagging the private by one session.

**Rule:** After any change to SELECTED_PLAYBOOKS or transformation steps in the private script, immediately mirror the change to the public template. Treat them as a pair.

## Concrete examples (2026-04-27)

**gog skill** — Added `skills/gog/SKILL.md` to the public repo. Not in `~/.claude/`. Fix: mirrored to `~/.claude/skills/gog/SKILL.md` so rsync carries it.

**`.claude/settings.json`** — Project-level settings file (UserPromptSubmit hook + DISCORD_STATE_DIR env). `~/.claude/` has no `.claude/` subdirectory, so rsync never writes this file. Fix: added step 3c to both sync scripts (`~/.openclaw/bin/sync-claude-to-public.sh` and `sync-to-public.sh` in public repo) that writes a sanitized copy after every rsync.

**Key signal:** If `git status` shows a new file in `.claude/` or any non-`~/.claude/`-backed directory, ask "does this survive the wipe?" before pushing.
