# Personal Infrastructure Skills

These skills are tied to the OpenClaw multi-agent system (not public yet, separate repo coming). They're included here as concrete examples of how skills plug into a larger system — but they require OpenClaw and its agents (Seymour, MoltyJoe, etc.) to function.

If you're adapting these patterns, the transferable idea is: skills can delegate to named subagents, and those subagents can have their own runtime context (identity, config, logs). The skills here assume that runtime exists.

| Skill | What it does |
|---|---|
| compact-checkpoint | Writes a session summary before context compaction, preserving work across /compact |
| openclaw-status | Snapshots the live OpenClaw system state: gateway, agents, channels |
| snapshot | Point-in-time session capture without triggering the full end-of-session ritual |
