# Personal Infrastructure Skills

These skills are tied to the OpenClaw multi-agent system (not public yet, separate repo coming). They're included here as concrete examples of how skills plug into a larger system — but they require OpenClaw and its agents (Seymour, MoltyJoe, etc.) to function.

If you're adapting these patterns, the transferable idea is: skills can delegate to named subagents, and those subagents can have their own runtime context (identity, config, logs). The skills here assume that runtime exists.

The skills that previously lived in this directory (`compact-checkpoint`, `openclaw-status`, `snapshot`, `debug-agent`, `deploy-task`) have been promoted to the top-level `skills/` directory as they've matured into standalone entries. See [`../README.md`](../README.md) for the current skill listing.
