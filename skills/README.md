# Skills

Invoked by Claude via the Skill tool, triggered by context rather than explicit user command. Each skill has a `when to use` guard in its SKILL.md that tells Claude when to fire it automatically.

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

## Personal infrastructure skills

Skills that require the OpenClaw companion system: [`personal-infrastructure/`](personal-infrastructure/README.md).
These are included as examples of how skills can delegate to named subagents with their own runtime context — not portable tools.

---

## What Anthropic now provides natively

The skill and subagent infrastructure is native:

- Agent definition files in `~/.claude/agents/` (specifying model, description, and behavioral instructions) are a native Claude Code feature.
- Context-triggered dispatch via the Skill tool is native.
- Several named agent types used here — Gadfly, CTO, Critic, The Architect, Safety Officer, Seymour, Cob — now ship as default named agents in the Claude Code fleet (available without custom definitions).
- Subagent spawning with the Agent tool, including `subagent_type` dispatch, is fully native and documented.

---

## Why these skill definitions are still worth reading

The agent infrastructure is native; the behavioral definitions and sequencing discipline are not.

- **Review sequencing** — The Gadfly-before-CTO ordering rule is the critical transferable pattern. If CTO runs first, its plan anchors subsequent review and Gadfly's product objections come too late to change the structure. This isn't documented by Anthropic — it's derived from use.
- **`compact-checkpoint`** and **`snapshot`** — The PostCompact hook covers part of this natively, but the skill-based checkpoint workflow gives more explicit control over what gets preserved and how it's structured for resumption.
- **Custom persona refinements** — The skill definitions here predate the native fleet and contain behavioral refinements from production use (specific instructions for what not to do, failure modes that were corrected). Even where a native equivalent exists, the specific prompts may differ from defaults in ways that matter.
- **`debug-agent`** and **`deploy-task`** — OpenClaw-specific, but included as examples of how skills can delegate to named subagents with their own runtime context. The delegation pattern transfers even if the specific infrastructure does not.
