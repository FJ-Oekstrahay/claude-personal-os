# Commands

User-invoked slash commands. Type `/batchc`, `/review-sequence`, etc. at the Claude Code prompt.

| Command | When to use | Portable? |
|---|---|---|
| `batchc` | Classify and dispatch a list of work items — groups parallel vs. sequential, sizes waves, routes code edits to subagents | Yes |
| `deploy-public` | Audit READMEs, commit `~/.claude/` private repo, sync to the public mirror, restore the landing page, push | No (requires sync script + OpenClaw paths) |
| `load-handoff` | List recent session handoff files and load one for context at the start of a new session | Partial (references OpenClaw handoff format) |
| `mmguns` | Research-to-integration loop — find SOTA for a capability area, gap-analyze against current project, produce ranked 3-item brief, then dispatch | Yes |
| `new-discord-session` | Bind a Claude Code project directory to a Discord channel — adds the channel to `access.json` and sets `DISCORD_STATE_DIR` in project settings | No (requires OpenClaw Discord bot) |
| `pressure` | Manually set the session context pressure level (`normal`, `elevated`, `high`) — overrides the automatic PostToolUse tracking for the rest of the session | Yes |
| `review-sequence` | Run one or more adversarial reviewer roles (Critic, Gadfly, Architect, CTO) in the correct order for the work at hand | Yes |
| `session-handoff` | Write a structured handoff file summarizing what was done, what's pending, and lessons to capture | Partial (the Seymour-spawn step requires OpenClaw; rest is portable) |

---

> **On what's native vs. custom:** The `.claude/commands/` infrastructure for custom slash commands is a native Claude Code feature. The commands here are protocols built on top of that infrastructure — the content, not the container, is what's valuable. For each command below, there's a note on what Claude Code now provides natively and why looking at the implementation here is still useful.

## batchc

A full dispatch protocol, not just a task grouper. When given a list of work items, `batchc` first classifies each item: is it an inline answer, a parallel task, a sequential task, or a code edit that must go to a Cob subagent? It then enforces wave sizing (max 3 concurrent tasks), requires a merge-before-parallelize analysis, and gates on wave results before proceeding to the next wave.

The key constraint it enforces: **all file edits go to a Cob subagent — never inline.** This prevents large batches from burning the main context window on implementation work. Born from experience running multi-file refactors inline and hitting the context limit mid-batch.

> **Native:** Claude Code's Agent tool and parallel tool calls are native — you can dispatch subagents without any custom command. **Still worth reading:** The batchc protocol enforces discipline that native tooling doesn't: wave sizing based on context pressure, merge-before-parallelize analysis, subagent output discipline (no diffs or code blocks returned to main context). The specific rules — when a dependency is "hard" vs. "soft," when throttle risk triggers a forced pause — transfer to any parallel dispatch work, even without the command.

## deploy-public

End-to-end public repo deployment in one command. Sequence:

1. Audit `~/.claude/` READMEs against the current directory state — update anything stale or missing
2. Commit `~/.claude/` (private repo) using the batchc grouping: hook/command work as one commit, memory updates as another, other changes individually
3. Run `sync-claude-to-public.sh` — rsyncs `~/.claude/` to the public mirror, auto-commits
4. Restore `docs/index.html` and `docs/hero.jpeg` from `pages/` (the sync wipes `docs/` on every run)
5. Commit and push the docs restore

Uses batchc methodology throughout — classify before acting, no inline diffs returned to main context.

> **Not portable:** Requires the private sync infrastructure and OpenClaw paths. Worth reading as an example of how to structure a multi-step deploy command: classify before acting, checkpoint between phases, use batchc methodology throughout.

## load-handoff

Lists the 5 most recent `HANDOFF-*.md` files from the workspace, lets you pick by number, reads the chosen file, and delivers a structured summary: what was accomplished, what's pending or blocked, gotchas and surprises, and the suggested first step as a concrete action.

This is the entry point for resuming work after a context clear or a break. Rather than re-reading a raw handoff file, it synthesizes it into a next-action-oriented brief.

> **Native:** Claude Code's context compression summarizes prior sessions automatically. **Still worth reading:** The handoff approach here is different in intent — it's a human-authored resumption document, not an auto-summary. The format (accomplished, pending, gotchas, first step) is optimized for picking up mid-work with full context, not for compression efficiency.

## mmguns

Research-to-integration loop for any capability area. Steps:

1. Web-search for current SOTA tools, papers, or patterns in `<topic>`
2. Compare against what's already in the project — gap analysis, not a survey
3. Produce a ranked 3-item brief: quick win (implement now), medium lift (spec stub), non-starter (ruled out with reasoning)
4. Dispatch the quick win via batchc if clear enough to execute immediately

The output must drive action, not just summarize. If nothing actionable emerges, that's the output — but it's explicit, not a default.

> **Native:** Web search via MCP and parallel tool dispatch are native. **Still worth reading:** The loop structure — four parallel search angles, gap analysis against the current project (not a survey), ranked brief with a required dispatch action — isn't a native pattern. The design principle ("a research command that stops at a report is just expensive grep") transfers to any research workflow.

## new-discord-session

Not portable — requires an active OpenClaw Discord bot binding.

Binds a Claude Code project directory to a Discord channel. It adds the channel to `~/.claude/channels/discord/access.json` (so the bot listens to it) and sets `DISCORD_STATE_DIR` in the project's `.claude/settings.json` (so the session knows where to find the shared Discord state). No thread router, no `acpx` plugin — just two writes and a confirmation report.

Also writes `DISCORD_CHAT_ID` to the project env so the `discord-notify` hook can identify which channel a session is talking in — useful when the hook posts activity to a centralized log channel.

Included here as an example of a project-binding workflow pattern, even though the infrastructure it targets is OpenClaw-specific.

> **Not portable:** Requires an active OpenClaw Discord bot. Included as an example of a project-binding workflow: two targeted writes (access list + project settings) and a confirmation report. The pattern of writing channel state into project settings so hooks route correctly is transferable.

## pressure

Manually overrides the session pressure level tracked by `resource-pressure.py`. Takes one argument: `normal`, `elevated`, or `high`. Writes to `~/.claude/hooks/state/session-pressure.json` with `manual_override: true` so the PostToolUse hook won't overwrite it. Run `/pressure normal` to clear the override and return to automatic tracking.

Pressure level affects rate-limit-aware commands (`batchc`, `mmguns`, `review-sequence`) — they throttle wave sizing and subagent dispatch at `elevated` and `high`.

> **Native:** No direct native equivalent. **Still worth reading:** Only relevant if you're running `resource-pressure.py`. The design pattern — a manual override that sets a flag preventing the automatic tracker from overwriting it — is a simple, durable way to handle "I know better than the auto-tracker right now."

## review-sequence

Runs 1–4 adversarial reviewer roles against the current artifact:

- **Critic** — quality and bugs: is this correct, clean, and complete?
- **Gadfly** — product friction: would a real user buy or use this?
- **Architect** — structural fragility: does this hold under real load?
- **CTO** — prioritization and scope: what should be built, and in what order?

The non-obvious sequencing rule: **Gadfly must run before CTO.** If CTO runs first, it produces a polished coherent plan that Gadfly can't effectively challenge — the framing anchors subsequent reviewers. Works on code, plans, architecture docs, and specs.

> **Native:** Claude Code now ships Gadfly, CTO, Critic, and The Architect as default named agents. **Still worth reading:** The sequencing rule — Gadfly before CTO — is the critical part, and it isn't documented by Anthropic. If CTO runs first, it produces a polished coherent plan that Gadfly can't effectively challenge. The framing anchors subsequent reviewers. Run Gadfly first, then CTO with Gadfly's findings as context. This transfers regardless of whether you use these specific skill files.

## session-handoff

First checks whether a real handoff is needed — trivial sessions skip. If yes: asks for a short name, writes `HANDOFF-{name}-{YYYY-MM-DD-HHMM}.md` to the workspace, and updates `MEMORY.md` with lessons from the session.

Handoff structure: Accomplished (with file paths and diffs for verification), Pending, Gotchas/Surprises, Lessons Captured, and next-session prompts. The handoff file is the canonical context bridge between sessions — not a summary, a resumption document.

> **Native:** Claude Code's auto-compression summarizes context across sessions. **Still worth reading:** A well-written handoff and an auto-summary serve different purposes. The handoff is written to answer "what do I do next?" — it's structured for action, not for completeness. The format here (with explicit "gotchas" and "lessons captured" sections) encodes institutional knowledge that auto-compression would treat as low-priority.
