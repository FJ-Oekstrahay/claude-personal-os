# Run this ON THE MAC MINI, after the MBA's cross-machine-sync commit lands

**Model:** Sonnet (sequential, live surfaces, no fan-out). Run inline, no subagent.
**Run order:** this prompt must run on the mini BEFORE the mini pushes anything to
`github.com/FJ-Oekstrahay/claude-config`.
**Not parallelizable** — every step depends on the previous one.

## Why

On 2026-09-10 the MacBook Air split `~/.claude` into a shared half (in git) and a
machine-local half (gitignored), so both machines can share config without overwriting each
other's local specifics. The MBA did its own half. **The mini's half has to be done on the
mini** — the MBA has no SSH key to the mini and `~/mhqws` is a one-way markdown mirror, so
nothing could be done remotely.

The commit you are about to pull **untracks ~3100 files.** That is intentional, but a pull
will DELETE those paths locally unless you save them first. Read the whole prompt before
running anything.

## What the commit changes

Newly gitignored and untracked (`git rm --cached`, content untouched on the MBA):
`discord-router/node_modules/`, `discord-router/logs/`, `discord-router/router.pid`,
`daemon.log`, `hooks/discord-activity.log`, `hooks/.backups/`, `jobs/`, `tmp/`,
`settings.json.bak-*`, `settings.local.json`, `CLAUDE.machine.md`.

New shared files: `CLAUDE.machine.md.example`, and a `@~/.claude/CLAUDE.machine.md` import
at the top of `CLAUDE.md`.

Still shared, deliberately NOT untracked: `discord-router/routes.json`,
`hooks/discord-channels.json`, `hooks/discord-channel-context.json`. Their history shows
additions only, and the channel IDs are Discord-global with per-machine channels already
distinguished by name. Untracking them would break the other machine's router for no gain.

## Steps

1. **Preserve what the pull would delete.** Before pulling:
   ```
   cd ~/.claude
   mkdir -p ~/claude-premerge-backup
   cp -a settings.local.json daemon.log ~/claude-premerge-backup/ 2>/dev/null
   cp -a hooks/.backups hooks/discord-activity.log ~/claude-premerge-backup/ 2>/dev/null
   cp -a discord-router/logs discord-router/router.pid ~/claude-premerge-backup/ 2>/dev/null
   cp -a jobs ~/claude-premerge-backup/ 2>/dev/null
   ls -la ~/claude-premerge-backup
   ```
   `node_modules/` does NOT need backing up — reinstall it in step 4.

2. **Pull.** Confirm you are on the same lineage first (`git log --oneline -1` should be an
   ancestor of origin/main, not a fork):
   ```
   git fetch origin && git log --oneline HEAD..origin/main | head
   git merge --ff-only origin/main
   ```
   If `--ff-only` refuses, STOP — that means the mini has diverged and this is the deferred
   cross-lineage merge (`prompts/claude-repo-divergence-merge.md`), not a fast-forward.
   Do that first; do not force anything.

3. **Restore the machine-local files** from `~/claude-premerge-backup/` to their original
   paths. They are gitignored now, so they will stay put and stop syncing.

4. **Reinstall the router's dependencies** — the pull removed `node_modules` from git, and
   if the directory was deleted the router will not restart without it:
   ```
   cd ~/.claude/discord-router && bun install
   ```
   Only restart the router if it was already running here.

5. **Write the mini's `CLAUDE.machine.md`.** Copy the template and fill it in for the mini:
   ```
   cd ~/.claude && cp CLAUDE.machine.md.example CLAUDE.machine.md
   ```
   It must record, at minimum:
   - that `~/.openclaw/workspace/projects/claude-config/` IS a real git repo here (~131
     commits) — on the MBA that path is a one-file stub;
   - that `~/.openclaw/workspace/projects/claude-config/distillation/pairs/` exists here
     (`commands/capture-pair.md` writes there);
   - that `~/.openclaw/workspace/projects/claude-config-mba/` and `~/mhqws/` do NOT exist
     here — they are MBA-only;
   - whether SSH from the mini to the MBA works, and any launchd services running here.
   Keep it short: it loads into every session's context.

6. **Verify.** Start a session on the mini and run `/context`. `CLAUDE.machine.md` must
   appear under **Memory files**. If it does not, the `@` import did not resolve — check
   that the file exists at `~/.claude/CLAUDE.machine.md` and is not a symlink.

## Two things to tell the user while you are here

- **`settings.local.json` at `~/.claude/` is almost certainly dead.** Evidence from the
  2.1.267 binary: every `settings.local.json` reference is project- or worktree-scoped, and
  the loader's indirection gate requires the file to sit "inside a real `.claude`
  directory" — which `~/.claude/settings.local.json` only satisfies when the project root
  *is* `~/.claude`. Sessions launched from `~/.openclaw/workspace/...` never read it. If the
  mini has one too, its `allow` rules have not been in effect either. This was NOT migrated
  automatically — moving permission rules is a live security surface and is the user's call.
  Do not carry `Bash(git:*)` across if you do migrate: his own CLAUDE.md warns it
  auto-approves destructive git ops.
- **Auto memory under `~/.claude/projects/<encoded-path>/memory/` is tracked in this repo,**
  but Claude Code's docs say auto memory is machine-local and "not shared across machines."
  The directory name is derived from the project path, so both machines write to the same
  names. It is additive in practice, but it is a deliberate deviation from the documented
  design — worth a decision rather than drift.

## Still open, not part of this prompt

- Where the mini's `~/.openclaw/workspace/projects/claude-config` repo's ~131 commits should
  live. **Only unbacked-up copy on any disk.** Asked 2026-09-08, still unanswered.
- Rotating the two Discord webhook URLs still present in this repo's history
  (blob `d0cee5a`, added in the initial commit `ecb3113`).
