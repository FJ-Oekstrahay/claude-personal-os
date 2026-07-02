the user prefaced a task with **"caution"** (or invoked `/caution`). This is a standing signal: before doing the work, check whether any part of it could collide with other Claude Code sessions running on this machine, then split the work into **safe-now** vs **defer**. Do not guess glibly — walk this procedure.

## Procedure

1. **Enumerate active peers.** Call `mcp__claude-peers__list_peers` (scope: `machine`). Note each session's CWD/repo — those are the directories you must not write into.
2. **Announce yourself.** Call `mcp__claude-peers__set_summary` with a 1–2 line note of what you're about to touch, so other sessions see it.
3. **Classify each subtask** by the shared resources it would touch:

   **SAFE to do now:**
   - Writes confined to the current project directory that no listed peer has as its CWD/repo.
   - New, inert files anywhere (a new command/skill/prompt/doc) that no running session invokes — additive; nothing reads them until invoked.
   - Edits to files loaded **once at session start** with **no concurrent writer** — e.g. `~/.claude/CLAUDE.md`. Running sessions already loaded it; there's no runtime effect and no peer is editing it. **This is the key non-obvious case — don't defer it out of vagueness.**
   - Read-only diagnosis of anything. Reading a live hook to write a fix is always safe.

   **DEFER (do NOT edit while peers run):**
   - Live shared hooks other sessions depend on at runtime: `~/.claude/hooks/discord-*.py`, notify/stop hooks, keyword-dispatch. A regression propagates instantly to every session.
   - `session-handoff` tooling (command/skill/scripts) — peers run handoffs at wind-down; the user named this class explicitly.
   - Discord comms plumbing generally: routing, thread-map, reply behavior.
   - Any write into a git repo a listed peer has as CWD/repo — file-write and commit conflicts.
   - Shared workspace state peers mutate: `project-board/board.json`, shared memory files.

4. **Do the SAFE subtasks now.**
5. **For each DEFERRED subtask:** write a fix/exec prompt to `<cwd>/prompts/<name>.md` following the user's prompt convention (model recommendation, run order, whether it can be orchestrated as a parallel workflow, constraints). Do NOT apply the change.
6. **Report back with all of:**
   - (a) what you completed now,
   - (b) what's deferred and **why** (name the peer/resource that makes it unsafe),
   - (c) an explicit instruction to restart you on those tasks **when the named sessions are done**,
   - (d) the prompt path(s) written, so the user can re-run later.

## Rule of thumb
"Could a bad version of this edit break another running session's next action, or conflict with a file a peer is writing?" If yes → defer. If it's isolated, or load-once-with-no-concurrent-writer → safe.
