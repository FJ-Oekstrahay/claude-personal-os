# Commands

User-invoked slash commands. Type `/batchc`, `/review-sequence`, etc. at the Claude Code prompt.

Anthropic added `/bg` (cloud background sessions) and parallel multi-agent orchestration in mid-2026. `batchc` is not a replacement for those — it's a dispatch discipline layer: wave sizing, sequential vs. parallel classification, merge-before-parallelize enforcement, and context-window protection by routing all file edits to subagents. The orchestration mechanism is separate from the protocol that governs how you use it.

| Command | When to use | Portable? |
|---|---|---|
| `batchc` | Classify and dispatch a list of work items — groups parallel vs. sequential, sizes waves, routes code edits to subagents | Yes |
| `deploy-public` | Audit READMEs, commit `~/.claude/` private repo, sync to the public mirror, restore the landing page, push | No (requires sync script + OpenClaw paths) |
| `load-handoff` | List recent session handoff files and load one for context at the start of a new session | Partial (references OpenClaw handoff format) |
| `mmguns` | Research-to-integration loop — find SOTA for a capability area, gap-analyze against current project, produce ranked 3-item brief, then dispatch | Yes |
| `new-discord-session` | Bind a Claude Code project directory to a Discord channel — adds the channel to `access.json` and sets `DISCORD_STATE_DIR` in project settings | No (requires OpenClaw Discord bot) |
| `pdf` | Anything involving PDF files — read, extract, merge, split, rotate, fill forms, create, encrypt, OCR | Yes |
| `pressure` | Manually set the session context pressure level (`normal`, `elevated`, `high`) — overrides the automatic PostToolUse tracking for the rest of the session | Yes |
| `review-sequence` | Run one or more adversarial reviewer roles (Critic, Gadfly, Architect, CTO) in the correct order for the work at hand | Yes |
| `session-handoff` | Write a structured handoff file summarizing what was done, what's pending, and lessons to capture | Partial (the Seymour-spawn step requires OpenClaw; rest is portable) |

---

## batchc

A full dispatch protocol, not just a task grouper. When given a list of work items, `batchc` first classifies each item: is it an inline answer, a parallel task, a sequential task, or a code edit that must go to a Cob subagent? It then enforces wave sizing (max 3 concurrent tasks), requires a merge-before-parallelize analysis, and gates on wave results before proceeding to the next wave.

**Wave sizing** — max 3 concurrent tool-heavy tasks per wave. A single Cob subagent may internally trigger dozens of file reads, edits, and shell commands — it counts as one wave slot, not one tool call per tool. Wave size is an orchestrator-level headcount, not a tool-call budget.

**Throttle-risk tracking** — after two consecutive heavy waves (3 tasks each), batchc caps the next wave at 1–2 tasks and enforces a turn boundary before continuing. No API signal triggers this — it's a conservative heuristic to avoid hitting rate limits mid-batch when a long run is underway.

**Merge-before-parallelize** — before dispatching 3+ tasks, batchc checks whether any items target the same file or resource. Items that do are merged into a single task before dispatch. Two simultaneous writes to the same file are never issued as separate wave slots — they produce conflicts or last-write-wins clobbers.

**Model routing** — Haiku for fully enumerated specs (exact field, exact value, no inference needed, change is localized, wrong output is immediately visible on inspection). Sonnet for anything requiring judgment, cross-file consistency, ambiguous scope, or output that feeds downstream reasoning. The distinction is consequential: Haiku on a judgment task produces plausible but wrong output that passes casual review.

**Discord-bound session handling** — in sessions that originate from a Discord channel, inline answers must be sent via the Discord reply tool in the same turn as subagent dispatch. Text written to the Claude Code transcript never reaches the Discord user. batchc encodes this as a hard rule: if the session is Discord-bound, answer inline via tool or don't answer at all until dispatch completes.

**Distinction from Anthropic's native parallel multi-agent** — Anthropic's orchestration runs tasks concurrently using the underlying agent infrastructure. batchc is the layer that decides *when* to parallelize, *how many* to run at once, *when to stop*, and *how to route results* back without bloating the main context. The two are complementary, not competing.

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

## pressure

Manually overrides the session pressure level tracked by `resource-pressure.py`. Takes one argument: `normal`, `elevated`, or `high`. Writes to `~/.claude/hooks/state/session-pressure.json` with `manual_override: true` so the PostToolUse hook won't overwrite it. Run `/pressure normal` to clear the override and return to automatic tracking.

Pressure level affects rate-limit-aware commands (`batchc`, `mmguns`, `review-sequence`) — they throttle wave sizing and subagent dispatch at `elevated` and `high`.

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
