Spawn a `gadfly` subagent (subagent_type: "gadfly") with the content to review passed as context.

After the subagent returns its review:

1. Determine the current date (run `date +%Y-%m-%d` if needed).
2. Choose a short kebab-case topic slug from the reviewed content (e.g., `onboarding-flow`, `pid-tuning-wizard`).
3. Save the full review output to:
   `/Users/moltyjoe/.openclaw/workspace/projects/droneteleo/reviews/YYYY-MM-DD-gadfly-[topic].md`
   replacing YYYY-MM-DD with the actual date and [topic] with the slug.
4. Confirm the file path to the user.

If the review contains **[OPUS RECOMMENDED]**, tell the user explicitly.

Sequencing reminder: Gadfly runs BEFORE CTO. If the user wants both, run `/gadfly` first, then pass Gadfly's findings to `/cto`.

This skill does not execute anything beyond spawning the subagent and saving output. No code changes.
