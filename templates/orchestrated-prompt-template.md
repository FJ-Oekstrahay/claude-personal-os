# <TASK TITLE>

**Priority:** <urgent | important-not-urgent>
**Model (top-level):** <Opus | Sonnet> — *the model used when this prompt is pasted into Claude Code, or for the first `agent()` call if a script runs it*
**Effort:** <low | medium | high>
**Orchestration:** <plain prompt | parallel dispatch | Workflow script>  ← see decision tree in `playbooks/workflow-orchestration.md`
**Run order (if multiple prompts):** <N/A | "run after X">

---

## ⚠️ How to run this (read first)

> A `.md` file is **NOT** executable via `Workflow({scriptPath})` — that parses the file as JavaScript.
> The script below is for humans. To actually run it, pick one:
>
> 1. **Extract** the ```js block to `~/.claude/workflows/<name>.js`, then:
>    `Workflow({ scriptPath: "~/.claude/workflows/<name>.js", args: <json> })`
> 2. **Inline** — paste the script into the `script` param:
>    `Workflow({ script: "<the JS>", args: <json> })`
>
> If **Orchestration = plain prompt or parallel dispatch**, delete the script section — just keep the spec and run it interactively.

---

## Spec (plain English)

What done looks like, in prose. A human (or the top-level agent) should be able to read just this section and understand the goal, the inputs, the constraints, and the deliverables. Keep the script and the spec consistent — if you edit one, edit the other.

- **Inputs:** <files, data, args>
- **Deliverables:** <files written, report returned>
- **Constraints:** <don't touch X, must run tests, etc.>
- **Verification:** <how to confirm it worked — /verify, /code-review, test command>

---

## Workflow script (delete if not a script)

```js
export const meta = {
  // PURE LITERAL — no variables, calls, or interpolation in here.
  name: '<kebab-name>',
  description: '<one line, shown in the permission dialog>',
  phases: [
    { title: 'Discover' },
    { title: 'Work' },
    { title: 'Verify' },
  ],
}

// `args` is the value passed to Workflow({args}). Pass real JSON, not a stringified list.
// `budget` exposes the turn's token target (budget.total / .remaining()).
// Date.now()/Math.random()/new Date() THROW here — pass timestamps via args, vary randomness by index.

// ── Schemas: define once, reuse. Validation forces the agent to return this shape. ──
const ITEM_SCHEMA = {
  type: "object", required: ["items"],
  properties: {
    items: { type: "array", items: {
      type: "object", required: ["path", "reason"],
      properties: { path: { type: "string" }, reason: { type: "string" } },
    }},
  },
}
const RESULT_SCHEMA = {
  type: "object", required: ["file", "summary"],
  properties: { file: { type: "string" }, summary: { type: "string" } },
}

// ── Phase 1: discover the work-list (dynamic fan-out) ──
phase('Discover')
const found = await agent(
  "Find the things to work on. Return {items:[{path, reason}]}. Structured output only.",
  { label: "discover", phase: "Discover", model: "sonnet", schema: ITEM_SCHEMA }
)
if (!found || !found.items.length) return { error: "Nothing to do." }
log(`Found ${found.items.length} items`)

// ── Phase 2 + 3: process each item, then verify — pipelined (no barrier) ──
// Default to pipeline(). Use isolation:'worktree' because these agents WRITE files in parallel.
const results = await pipeline(
  found.items,

  // stage 1: do the work (mechanical edit → haiku; cross-file reasoning → sonnet)
  (item) => agent(
    `Apply the change to ${item.path}. Reason: ${item.reason}. ` +
    `Return only: file touched + one-line summary. No diffs, no code blocks.`,
    { label: `edit:${item.path}`, phase: "Work", model: "haiku", schema: RESULT_SCHEMA, isolation: "worktree" }
  ),

  // stage 2: verify each as soon as its edit lands (verifier in a FRESH context)
  (res, item) => res && agent(
    `Verify the change to ${item.path} is correct and complete. Report pass/fail + why.`,
    { label: `verify:${item.path}`, phase: "Verify", model: "sonnet" }
  ).then(v => ({ ...res, verdict: v }))
)

return {
  done: results.filter(Boolean),
  stats: { items: found.items.length, completed: results.filter(Boolean).length },
}
```

---

## Notes for future-me
- **Worktrees** only because stage-1 agents write files in parallel. If they were read-only, drop `isolation` (pure overhead). See worktree checklist in the playbook.
- **`parallel()` vs `pipeline()`**: this uses `pipeline()` so each item verifies the moment its edit lands. Switch to a `parallel()` barrier only if a later stage needs *all* prior results at once (dedup, total-count early-exit).
- **Model per agent**: set explicitly. Discover=sonnet (judgment), edit=haiku (mechanical), verify=sonnet (catch silent errors).
- Commit scoped to changed files after the run (standing order). Don't push unless asked.
