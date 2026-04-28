# Skills

Invoked by Claude via the Skill tool, triggered by context rather than explicit user command. Each skill has a `when to use` guard in its SKILL.md that tells Claude when to fire it automatically.

| Skill | What problem it solves |
|---|---|
| critic | You want harsh adversarial review before committing to a plan or shipping code — runs a focused critic role that looks for what fails, not what works. Use when you want real objections, not validation. |
| debug-agent | An OpenClaw agent is misbehaving and you need a focused investigation workflow — reads the agent's session history, identity, and logs to diagnose the issue without thrashing the main context. |
| deploy-task | Prevents skipping steps before a live system change — enforces the OpenClaw governance model: write a change envelope, do a dry run, get an explicit go-ahead before touching anything. |
| gog | Gives Claude access to your Google Workspace — Gmail search and send, Calendar event creation, Drive search, and Sheets write — using your locally-authenticated gog install. No OAuth flow at runtime. |

## Personal infrastructure skills

Skills that require the OpenClaw companion system: [`personal-infrastructure/`](personal-infrastructure/README.md).
These are included as examples of how skills can delegate to named subagents with their own runtime context — not portable tools.
