# deep-research

Deep research harness — fan-out web searches, fetch sources, adversarially verify claims, synthesize a cited report.

## When to use

When the user wants a deep, multi-source, fact-checked research report on any topic.

BEFORE invoking: check if the question is specific enough. If underspecified (e.g. "what car should I buy" with no budget/use-case/region), ask 2-3 clarifying questions first. Then pass the refined question as args.

## How to invoke

**Always use the capped scriptPath, not `{name: 'deep-research'}`.** The built-in workflow spawns up to 97 agents and will hit rate limits.

```
Workflow({
  scriptPath: '~/.claude/workflows/deep-research.js',
  args: '<the research question>'
})
```

## Agent cap

Default: ~20 total agents (MAX_FETCH=5, MAX_VERIFY_CLAIMS=5).

Math: 1 scope + ~6 search + 5 fetch + (5 claims × 3 votes) verify + 1 synth = ~20.

To adjust: edit `MAX_FETCH` and `MAX_VERIFY_CLAIMS` at the top of `~/.claude/workflows/deep-research.js`.
- Each +1 to MAX_VERIFY_CLAIMS = +3 agents (3 verification votes per claim)
- Each +1 to MAX_FETCH = +1 agent

If the user needs more depth on a question, run it twice on sub-questions rather than raising the cap.

**Do not raise above MAX_FETCH=10 / MAX_VERIFY_CLAIMS=10 without flagging it.** The built-in default (MAX_FETCH=15, MAX_VERIFY_CLAIMS=25) hit Claude Pro rate limits at 97 agents — too many requests per minute within the subscription. Workflow subagents run under the Pro subscription, not a separate API key.
