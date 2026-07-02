the user said **"orchcheck"** (or invoked `/orchcheck`). He wants you to **PAUSE and decide how to structure a piece of work before executing** — inline, parallel dispatch, batchc, or Workflow. Do NOT start executing the underlying task. Produce a recommendation and wait for his go-ahead.

## Steps

1. **Restate** the task in one line and list its subtasks.
2. **Check independence:** Do subtasks share inputs/outputs? Any file-write conflicts? Any structured data passed phase→phase? Any loop-until-X or conditional-on-results control flow? Any parallel agents that write files?
3. **Apply the decision tree** (from global `CLAUDE.md` / `[[workflow-orchestration]]` playbook):
   - **One task** → inline, just do it.
   - **2–3 fixed independent tasks**, no file conflicts, no structured cross-phase data → **parallel dispatch** (multiple Agent calls in one message).
   - **Several tool-heavy tasks you'll pace yourself**, where the risk is rate-limit / context bloat in *this* session → **batchc**.
   - **Deterministic fan-out** — loops-until-X, conditionals on results, structured phase→phase data, per-item error isolation, or **parallel agents that WRITE files** (→ worktrees) → **Workflow** (`pipeline()`/`parallel()`).
4. **Output:**
   - Recommended mechanism + one-line why.
   - A concrete sketch: which agents/waves, what model each (per the routing table — orchestrator/synthesis = opus, cross-file reasoning = sonnet, mechanical edits = haiku, verifiers = sonnet), worktree yes/no.
   - If Workflow: whether a standalone `~/.claude/workflows/*.js` script is needed vs an inline `script`.
5. **Flag the silent-failure trap:** a plain "do A, B, C in parallel" prompt may get *sequenced* by the model — only Workflow `parallel()`/`pipeline()` or explicit one-message dispatch guarantees concurrency.
6. **Stop.** Let the user confirm the approach before you execute.

## Reference
`~/.openclaw/workspace/memory/playbooks/workflow-orchestration.md`
