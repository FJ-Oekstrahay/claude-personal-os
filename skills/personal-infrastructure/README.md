# Personal Infrastructure Skills

These skills are tied to the OpenClaw multi-agent system (not public yet, separate repo coming). They're included here as concrete examples of how skills plug into a larger system — but they require OpenClaw and its agents (Seymour, MoltyJoe, etc.) to function.

---

## What "personal infrastructure" means here

These are skills that delegate to named agents with their own runtime context — identity files, session logs, channel bindings, and tool permissions that are configured outside the Claude Code session and persist across it. The skill acts as an orchestration entry point; the agent does the work in an isolated context.

The pattern: a skill reads the current task, constructs a prompt, spawns a subagent (Cob for implementation work, Seymour for mechanical tasks), and enforces output discipline on the return path. The main session context stays clean — no diffs, no file contents, no tool-call noise.

**Why this matters for multi-agent design:** Claude Code's context window is shared across the whole session. When implementation work is done inline, the accumulated tool calls, file reads, and diffs fill the window. Routing to a subagent gives that work its own fresh context, and the result comes back as a short summary. The cost is coordination overhead; the benefit is that long-running sessions don't degrade.

---

## Transferable pattern

If you're building similar infrastructure, the structure that makes these work:

1. **Named subagents with identity files** — each agent has an `IDENTITY.md` that sets its role, constraints, and output format. The skill references the agent by name; the runtime resolves which context to load.
2. **Output discipline at the boundary** — the skill prompt ends with a hard constraint on what the subagent may return (file paths, one-line summary, no diffs). The parent session enforces this by summarizing before continuing.
3. **Separate credential scopes** — agents that need channel access (Discord, iMessage) carry their own auth profiles, not the parent session's.
4. **Model routing by task type** — mechanical spec-application tasks go to Haiku; anything requiring cross-file reasoning or ambiguous scope goes to Sonnet. The routing decision happens at dispatch time, not at skill definition time.

---

## Promoted skills

The skills that previously lived in this directory (`compact-checkpoint`, `openclaw-status`, `snapshot`, `debug-agent`, `deploy-task`) have been promoted to the top-level `skills/` directory as they matured into standalone entries that work without a full OpenClaw installation. See [`../README.md`](../README.md) for the current skill listing.
