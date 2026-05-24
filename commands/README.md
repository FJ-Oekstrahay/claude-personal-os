# Commands

User-invoked slash commands. Type `/batchc`, `/review-sequence`, etc. at the Claude Code prompt.

| Command | When to use | Portable? |
|---|---|---|
| `batchc` | Classify and dispatch a list of work items — groups parallel vs. sequential, sizes waves, routes code edits to subagents | Yes |
| `deploy-public` | Audit READMEs, commit `~/.claude/` private repo, sync to the public mirror, restore the landing page, push | No (requires sync script + OpenClaw paths) |
| `load-handoff` | List recent session handoff files and load one for context at the start of a new session | Partial (references OpenClaw handoff format) |
| `mmguns` | Research-to-integration loop — find SOTA for a capability area, gap-analyze against current project, produce ranked 3-item brief, then dispatch | Yes |
| `new-discord-session` | Bind a Claude Code project directory to a Discord channel — adds the channel to `access.json` and sets `DISCORD_STATE_DIR` in project settings | No (requires OpenClaw Discord bot) |
| `review-sequence` | Run one or more adversarial reviewer roles (Critic, Gadfly, Architect, CTO) in the correct order for the work at hand | Yes |
| `pressure` | Manually override session pressure level (`normal`/`elevated`/`high`) in the state file. All pressure-aware commands (batchc, mmguns, review-sequence) throttle accordingly until cleared with `/pressure normal`. | Yes |
| `session-handoff` | Write a structured handoff file summarizing what was done, what's pending, and lessons to capture | Partial (the Seymour-spawn step requires OpenClaw; rest is portable) |

---

## batchc

A full dispatch protocol, not just a task grouper. When given a list of work items, `batchc` first classifies each item: is it an inline answer, a parallel task, a sequential task, or a code edit that must go to a Cob subagent? It then enforces wave sizing (max 3 concurrent tasks), requires a merge-before-parallelize analysis, and gates on wave results before proceeding to the next wave.

The key constraint it enforces: **all file edits go to a Cob subagent — never inline.** This prevents large batches from burning the main context window on implementation work. Born from experience running multi-file refactors inline and hitting the context limit mid-batch.

## deploy-public

End-to-end public repo deployment in one command. Sequence:

1. Audit `~/.claude/` READMEs against the current directory state — update anything stale or missing
2. Commit `~/.claude/` (private repo) using the batchc grouping: hook/command work as one commit, memory updates as another, other changes individually
3. Run `sync-claude-to-public.sh` — rsyncs `~/.claude/` to the public mirror, auto-commits
4. Restore `docs/index.html` and `docs/hero.jpeg` from `pages/` (the sync wipes `docs/` on every run)
5. Commit and push the docs restore

Uses batchc methodology throughout — classify before acting, no inline diffs returned to main context.

## load-handoff

Lists the 5 most recent `HANDOFF-*.md` files from the workspace, lets you pick by number, reads the chosen file, and delivers a structured summary: what was accomplished, what's pending or blocked, gotchas and surprises, and the suggested first step as a concrete action.

This is the entry point for resuming work after a context clear or a break. Rather than re-reading a raw handoff file, it synthesizes it into a next-action-oriented brief.

## mmguns

Research-to-integration loop for any capability area. Steps:

1. Web-search for current SOTA tools, papers, or patterns in `<topic>`
2. Compare against what's already in the project — gap analysis, not a survey
3. Produce a ranked 3-item brief: quick win (implement now), medium lift (spec stub), non-starter (ruled out with reasoning)
4. Dispatch the quick win via batchc if clear enough to execute immediately

The output must drive action, not just summarize. If nothing actionable emerges, that's the output — but it's explicit, not a default.

## new-discord-session

Not portable — requires an active OpenClaw Discord bot binding.

Binds a Claude Code project directory to a Discord channel. It adds the channel to `~/.claude/channels/discord/access.json` (so the bot listens to it) and sets `DISCORD_STATE_DIR` in the project's `.claude/settings.json` (so the session knows where to find the shared Discord state). No thread router, no `acpx` plugin — just two writes and a confirmation report.

Also writes `DISCORD_CHAT_ID` to the project env so the `discord-notify` hook can identify which channel a session is talking in — useful when the hook posts activity to a centralized log channel.

Included here as an example of a project-binding workflow pattern, even though the infrastructure it targets is OpenClaw-specific.

## review-sequence

Runs 1–4 adversarial reviewer roles against the current artifact:

- **Critic** — quality and bugs: is this correct, clean, and complete?
- **Gadfly** — product friction: would a real user buy or use this?
- **Architect** — structural fragility: does this hold under real load?
- **CTO** — prioritization and scope: what should be built, and in what order?

The non-obvious sequencing rule: **Gadfly must run before CTO.** If CTO runs first, it produces a polished coherent plan that Gadfly can't effectively challenge — the framing anchors subsequent reviewers. Works on code, plans, architecture docs, and specs.

## session-handoff

First checks whether a real handoff is needed — trivial sessions skip. If yes: asks for a short name, writes `HANDOFF-{name}-{YYYY-MM-DD-HHMM}.md` to the workspace, and updates `MEMORY.md` with lessons from the session.

Handoff structure: Accomplished (with file paths and diffs for verification), Pending, Gotchas/Surprises, Lessons Captured, and next-session prompts. The handoff file is the canonical context bridge between sessions — not a summary, a resumption document.
