the user said **"orchcheck"** (or invoked `/orchcheck`). He wants you to **PAUSE and decide how to structure a piece of work before executing** — inline, parallel dispatch, batchc, or Workflow. Do NOT start executing the underlying task. Produce a recommendation and wait for his go-ahead.

## Steps

1. **Restate** the task in one line and list its subtasks.
2. **Check independence:** Do subtasks share inputs/outputs? Any file-write conflicts? Any structured data passed phase→phase? Any loop-until-X or conditional-on-results control flow? Any parallel agents that write files?
3. **Apply the decision tree** (from global `CLAUDE.md` / `[[workflow-orchestration]]` playbook):
   - **One task** → inline, just do it.
   - **2–3 fixed independent tasks**, no file conflicts, no structured cross-phase data → **parallel dispatch** (multiple Agent calls in one message).
   - **Several tool-heavy tasks you'll pace yourself**, where the risk is rate-limit / context bloat in *this* session → **batchc**.
   - **Deterministic fan-out** — loops-until-X, conditionals on results, structured phase→phase data, per-item error isolation, or **parallel agents that WRITE files** (→ worktrees) → **Workflow** (`pipeline()`/`parallel()`).
3b. **Stay on Claude Max unless the user asked for cross-provider this turn** — it is opt-in, see global
   `CLAUDE.md`. If GLM/Kimi would genuinely help (volume constrained by rate limits, or a big-context
   sweep), say so in ONE line as an offer and carry on with the Max plan; do not wait for an answer.
   If he did opt in: architect = Opus, worker = `ccx glm`, sweep = `ccx kimi`, review = Sonnet — and
   note that provider is fixed per *process*, so cross-provider always costs a dispatcher hop through
   `~/.claude/bin/ccx`, never a `model:` param on a subagent.

3c. **Is there a queue?** If the work is a list of items that outlives one session, put it on a state
   bus rather than inventing a per-run script — a killed worker then resumes from disk. Pattern and
   the four required mechanics: [[disk_state_bus_for_resumable_workers]]. The reference implementation
   is `~/.claude/bin/feature-state.py` (contract: games `docs/STATE-BUS.md`), drained by
   `~/.claude/workflows/feature-build.js` — **pass `args.repo`**, since that script defaults to the
   games repo and would otherwise drain the wrong queue.

   **Recommending the queue drain does not authorize it.** `feature-build.js` is gated behind the
   `longrun` trigger (`~/.claude/CLAUDE.md` §"Long autonomous runs are OPT-IN too"). A "yes, that
   approach is right" at step 6 approves the *mechanism*, not the run — the user still has to say
   `longrun go`. Say so explicitly in your step-4 output when the queue drain is what you recommend.

4. **Output:**
   - Recommended mechanism + one-line why.
   - A concrete sketch: which agents/waves, what model each (per the routing table — orchestrator/synthesis = opus, cross-file reasoning = sonnet, mechanical edits = haiku, verifiers = sonnet), worktree yes/no.
   - If Workflow: whether a standalone `~/.claude/workflows/*.js` script is needed vs an inline `script`.
5. **Flag the silent-failure trap:** a plain "do A, B, C in parallel" prompt may get *sequenced* by the model — only Workflow `parallel()`/`pipeline()` or explicit one-message dispatch guarantees concurrency.
6. **Stop.** Let the user confirm the approach before you execute.

## Reference
`~/.openclaw/workspace/memory/playbooks/workflow-orchestration.md`
