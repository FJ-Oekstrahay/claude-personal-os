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
| gog | Gives Claude access to your Google Workspace — Gmail search and send, Calendar event creation, Drive search, and Sheets write — using your locally-authenticated gog install. No OAuth flow at runtime. |
| openclaw-status | Snapshots the live OpenClaw system state: gateway health, agent status, channel bindings. Use at session start or when something seems off. |
| snapshot | Point-in-time session capture without triggering the full end-of-session ritual — writes a named snapshot file and returns. Useful mid-session to checkpoint progress. |

## Personal infrastructure skills

Skills that require the OpenClaw companion system: [`personal-infrastructure/`](personal-infrastructure/README.md).
These are included as examples of how skills can delegate to named subagents with their own runtime context — not portable tools.
