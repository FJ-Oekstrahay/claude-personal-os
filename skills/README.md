# Skills

Invoked by Claude via the Skill tool, triggered by context rather than explicit user command. Each skill has a `when to use` guard in its SKILL.md that tells Claude when to fire it automatically.

As of late 2025, Anthropic loads `SKILL.md` files at session start automatically — no marketplace registration needed. That's already the format used here. The loading mechanism is now native; what's here is the content: specific cognitive workflows, sequencing rules, and dispatch protocols that don't come built-in.

| Skill | What problem it solves |
|---|---|
| compact-checkpoint | Preserves work across `/compact` — writes a session summary before context compaction so the resumed session knows what was accomplished. |
| critic | You want harsh adversarial review before committing to a plan or shipping code — runs a focused critic role that looks for what fails, not what works. Use when you want real objections, not validation. |
| cto | Spawns a CTO subagent to review the current artifact for prioritization and scope: what should be built and in what order. Runs after Gadfly in the review sequence. |
| debug-agent | An OpenClaw agent is misbehaving and you need a focused investigation workflow — reads the agent's session history, identity, and logs to diagnose the issue without thrashing the main context. |
| deploy-task | Prevents skipping steps before a live system change — enforces the OpenClaw governance model: write a change envelope, do a dry run, get an explicit go-ahead before touching anything. |
| gadfly | Spawns a Gadfly subagent for product-friction review: would a real user actually buy or use this? Must run before CTO or the CTO's plan anchors the framing. |
| gog | Gives Claude access to your Google Workspace — Gmail search and send, Calendar event creation, Drive search, and Sheets write — using your locally-authenticated gog install. No OAuth flow at runtime. (Skill files excluded from public mirror.) |
| openclaw-status | Snapshots the live OpenClaw system state: gateway health, agent status, channel bindings. Use at session start or when something seems off. |
| snapshot | Point-in-time session capture without triggering the full end-of-session ritual — writes a named snapshot file and returns. Useful mid-session to checkpoint progress. |

---

## Key skill internals

### batchc

A parallel subagent dispatch protocol, not a task grouper. Wave sizing is capped at ≤3 concurrent tool-heavy tasks. A single Cob subagent may internally trigger dozens of tool calls — it counts as one wave slot, not one tool call.

Throttle-risk tracking: after two consecutive heavy waves, batchc caps the next wave at 1–2 tasks and enforces a turn boundary before proceeding. This is manual rate-limit protection — the API doesn't tell you when you're approaching the edge.

Merge-before-parallelize: before dispatching 3+ tasks, batchc checks for items targeting the same file or resource and merges them into a single task. Two simultaneous edits to the same file are never dispatched as separate wave slots.

Model routing: Haiku for fully enumerated specs (exact field, exact value, no inference required). Sonnet for anything requiring judgment, cross-file consistency, or ambiguous scope. The distinction matters — Haiku on a judgment task produces plausible but wrong output.

Discord-bound session handling: in sessions that originate from Discord, inline answers must be sent via Discord reply tool in the same turn as dispatch. Text written to the transcript never reaches the Discord user.

This is a discipline layer above Anthropic's native parallel orchestration, not a replacement for it. Anthropic's mechanism runs tasks concurrently. batchc governs when to parallelize, how many to run, when to stop, and how to route results back.

### review-sequence

Runs adversarial reviewer roles in a fixed causal order: **Gadfly → CTO**. Gadfly finds friction and failure modes; CTO works from Gadfly's findings to produce a technically sound plan. Running CTO first produces a polished coherent plan that subsequent critics can't effectively challenge — the framing anchors them. The ordering is not arbitrary.

Full sequence: Critic (quality/bugs) → Gadfly (product friction) → Architect (structural fragility) → CTO (prioritization and scope). Each reviewer's output becomes input to the next. Works on code, architecture docs, specs, and plans.

### mmguns

Research-to-integration loop. Steps: web-search for current SOTA in a capability area, gap-analyze against the current project (not a survey — a comparison), produce a ranked 3-item brief (quick win / medium lift / non-starter with explicit reasoning), dispatch the quick win via batchc if the spec is clear enough to execute immediately. Output must drive action. If nothing actionable emerges, that's the explicit output — not a default silence.

### Opinionated cognitive workflows

`critic`, `gadfly`, `cto`, `debug-agent`, `snapshot`, `compact-checkpoint`, `session-handoff`, `load-handoff` are opinionated workflows with sequencing rules and output discipline requirements built into their SKILL.md files. They're not generic tools — each encodes a specific pattern for when to fire, what to produce, and what not to return to the main context.

---

## Personal infrastructure skills

Skills that require the OpenClaw companion system: [`personal-infrastructure/`](personal-infrastructure/README.md).
These are included as examples of how skills can delegate to named subagents with their own runtime context — not portable tools.
