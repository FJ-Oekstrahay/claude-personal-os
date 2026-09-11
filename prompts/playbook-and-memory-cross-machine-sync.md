# Cross-machine sync for playbooks and workspace memory

**Model:** Opus for the design decision and the content reconciliation (judgment; creating a
repo is not reversible-by-default). Sonnet is fine for the mechanical clone/move once the
decision is made.
**Run order:** independent of `~/.claude` — that repo is already synced and healthy as of
2026-09-10. Run this on its own.
**Orchestration:** inline. The reconciliation is a judgment pass over prose, not fan-out.
**Can run on either machine** — SSH works both ways (`ssh moltyjoe@macmin`,
`ssh geoffhoekstra@geoffs-macbook-air`).

## The problem

`~/.claude` is synced. **`~/.openclaw/workspace/memory/` is not**, and that is where the
playbooks live — the highest-value accumulated knowledge in the system.

Measured 2026-09-10:

| | MacBook Air | Mac mini |
|---|---|---|
| playbooks | **445** | **418** |
| unique to that machine | **44** | **17** |
| shared | 401 | 401 |
| under git? | `~/.openclaw/workspace` is **not a repo** | `~/.openclaw` **is** a repo (~5714 files, nightly auto-commits) but **no remote**, and `workspace/memory` has only **4** tracked files |

So playbooks have **diverged in both directions** and are **backed up nowhere**. The mini's
`git-object-corruption-triage.md` exists only on the mini; 44 others exist only on the MBA.

`~/mhqws/` on the MBA is an Obsidian vault mirroring the mini's workspace markdown, but it is
**one-way (mini → MBA)**. Work done on the MBA has no path back.

## What the user asked for

> "playbooks created and updated on one machine to benefit the other" — and improvements to
> each system to benefit both, **without** something synced across causing confusion when it
> only applied to one machine.

## Decide first (ask the user, do not assume)

**Recommended — Option A: a private GitHub repo for `~/.openclaw/workspace/memory/`**, cloned
at that path on both machines. Symmetric, gives the first real backup, and reuses the
fetch-before-push discipline now in `CLAUDE.md`. Note both machines already push to
`FJ-Oekstrahay` so auth exists.

- Option B: make the Obsidian sync two-way. Less work, but Obsidian sync is not a backup, has
  no history, and silently resolves conflicts.
- Option C: fold into `~/.claude`. Rejected — mixes Claude config with workspace knowledge,
  and the paths differ (`~/.openclaw/workspace/` vs `~/.claude/`).

## Steps once Option A is chosen

1. **Snapshot both sides first** — `cp -a ~/.openclaw/workspace/memory ~/memory-backup-<stamp>`
   on each machine, verify file counts. These files are almost entirely untracked, so a bad
   reconciliation is permanent. **A git tag protects nothing here.**
2. **Reconcile the 401 shared filenames before creating the repo.** Same name does not mean
   same content — diff them and merge by hand where they differ. Do NOT let one machine's copy
   win wholesale.
3. Create the private repo, push from whichever machine has the reconciled superset, clone to
   the other. Preserve `00_index.md` — it is the entry point every session reads.
4. **Apply the machine-independence test to every playbook** as it lands, per
   `~/.claude/rules/cross-machine-lessons.md`: a playbook naming an absolute home path, a
   username, a host, a service, or a workspace root that may not exist on the other machine is
   machine-specific. The two homes are `/Users/geoffhoekstra` (MBA) and `/Users/moltyjoe`
   (mini) — **absolute home paths are not portable**. Rewrite as `~/`, or move the fact into
   `CLAUDE.machine.md`.
5. **Games playbooks are MBA-only by decision (the user, 2026-09-10)** — all game development
   happens on the MacBook Air and none is planned for the mini. Roblox/Studio/`.rokit`
   playbooks may sync (harmless) but must not assert that tooling exists on the mini.
6. Add the fetch-before-push rule to whatever automation commits this repo. The mini's
   `~/.openclaw` already runs a **nightly auto-commit** — if that repo gains a remote, an
   auto-push without a fetch is exactly the collision that cost 70 days on `claude-config`.

## Also worth deciding in the same session

- **`~/.openclaw` on the mini has no remote and holds ~5714 tracked files** with nightly
  auto-commits going nowhere. Same "only copy on one disk" exposure.
- **`~/.openclaw/workspace/projects/claude-config/` on the mini** — a real ~131-commit repo,
  still the only unbacked-up copy of its history. Open since 2026-09-08, still unanswered.
- **memsearch is per-machine and should stay that way.** `~/.memsearch/milvus.db` is a 261 MB
  local vector index over each machine's own `.memsearch/memory/` dirs. It is derived data —
  rebuildable, machine-specific, and not worth syncing. Sync the *source* markdown; let each
  machine index it.
