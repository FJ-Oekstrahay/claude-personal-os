Spawn a `cto` subagent (subagent_type: "cto") with the content to review passed as context. Pass any Gadfly findings available in the current conversation as additional context to the subagent.

After the subagent returns its review:

1. Determine the current date (run `date +%Y-%m-%d` if needed).
2. Choose a short kebab-case topic slug from the reviewed content (e.g., `onboarding-flow`, `pid-tuning-wizard`).
3. Save the full review output to:
   `~/.openclaw/workspace/projects/droneteleo/reviews/YYYY-MM-DD-cto-[topic].md`
   replacing YYYY-MM-DD with the actual date and [topic] with the slug.
4. Confirm the file path to the user.

If the review contains **[OPUS RECOMMENDED]**, tell the user explicitly and offer to re-run with a model override to Opus.

This skill does not execute anything beyond spawning the subagent and saving output. No code changes.
