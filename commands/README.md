# Commands

User-invoked slash commands. Type `/batchc`, `/review-sequence`, etc. at the Claude Code prompt.

| Command | When to use | Portable? |
|---|---|---|
| `batchc` | Classify and dispatch a list of work items — groups parallel vs. sequential, sizes waves, routes code edits to subagents | Yes |
| `load-handoff` | List recent session handoff files and load one for context at the start of a new session | Partial (references OpenClaw handoff format) |
| `new-discord-session` | Wire a Discord channel into the thread router so new threads auto-provision Claude Code sessions | No (requires OpenClaw Discord binding) |
| `review-sequence` | Run one or more adversarial reviewer roles (Critic, Gadfly, Architect, CTO) in the correct order for the work at hand | Yes |
| `session-handoff` | Write a structured handoff file summarizing what was done, what's pending, and lessons to capture | Partial (the Seymour-spawn step requires OpenClaw; rest is portable) |
