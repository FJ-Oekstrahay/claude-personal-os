# Commands

User-invoked slash commands. Type `/batchc`, `/review-sequence`, etc. at the Claude Code prompt.

| Command | When to use | Portable? |
|---|---|---|
| `batchc` | Classify and dispatch a list of work items — groups parallel vs. sequential, sizes waves, routes code edits to subagents | Yes |
| `load-handoff` | List recent session handoff files and load one for context at the start of a new session | Partial (references OpenClaw handoff format) |
| `new-discord-session` | Wire a Discord channel into the thread router so new threads auto-provision Claude Code sessions | No (requires OpenClaw Discord binding) |
| `review-sequence` | Run one or more adversarial reviewer roles (Critic, Gadfly, Architect, CTO) in the correct order for the work at hand | Yes |
| `session-handoff` | Write a structured handoff file summarizing what was done, what's pending, and lessons to capture | Partial (the Seymour-spawn step requires OpenClaw; rest is portable) |

---

## batchc

A full dispatch protocol, not just a task grouper. When given a list of work items, `batchc` first classifies each item: is it an inline answer, a parallel task, a sequential task, or a code edit that must go to a Cob subagent? It then enforces wave sizing (max 3 concurrent tasks), requires a merge-before-parallelize analysis, and gates on wave results before proceeding to the next wave.

The key constraint it enforces: **all file edits go to a Cob subagent — never inline.** This prevents large batches from burning the main context window on implementation work. Born from experience running multi-file refactors inline and hitting the context limit mid-batch.

## load-handoff

Lists the 5 most recent `HANDOFF-*.md` files from the workspace, lets you pick by number, reads the chosen file, and delivers a structured summary: what was accomplished, what's pending or blocked, gotchas and surprises, and the suggested first step as a concrete action.

This is the entry point for resuming work after a context clear or a break. Rather than re-reading a raw handoff file, it synthesizes it into a next-action-oriented brief.

## new-discord-session

Not portable — requires the OpenClaw `acpx` plugin and an active Discord bot binding.

Binds a Claude Code project directory to a Discord channel in the OpenClaw thread router. After running, new Discord threads in that channel auto-provision Claude Code sessions scoped to that directory. The command writes the binding into the router config and confirms the channel is live.

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
