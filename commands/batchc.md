Smartbatch execution protocol. Read the full prompt before touching anything, then:

1. **Classify every item** into one of four buckets:
   - **Inline answer** — can be answered from existing context, no tools needed
   - **Parallel dispatch** — independent subagent or tool work, no dependencies
   - **Sequential** — depends on the output of another item (name the dependency explicitly)
   - **Cob subagent (code)** — any task that:
     - modifies files, OR
     - depends on repository state, OR
     - spans multiple files or requires consistency across files

1a. **Merge trivial items**
   - If multiple items target the same file or resource and can be done together, merge into a single subagent task
   - Do not spawn separate subagents for tightly coupled edits

1b. **Wave sizing — tool-heavy tasks**
   - A wave should contain no more than **3 concurrent tool-heavy tasks**
   - Wave size should adapt based on task size and follow-up likelihood — use fewer than 3 when tasks are large, context-heavy, or likely to trigger follow-up work; drop to 1–2 when risk is high
   - **Reduce to 1–2 tasks** when: prior wave was tool-heavy, context/tool usage was large, follow-up work is likely, or throttle risk is HIGH (see 1d)
   - **Cob subagent = tool-heavy**: a single Cob subagent may internally trigger many tool calls. Count any Cob task as tool-heavy for wave sizing — do not undercount by treating it as one lightweight item (see also 7a)
   - If you are about to dispatch more than 3 tool-heavy tasks in one wave, stop and re-read rule 1a — most batches that hit 3+ have merge candidates
   - Queue remaining work into later waves; do not pre-initialize all future work at once

1c. **Wave gating and pacing**
   - Do not start the next wave until the current wave has produced useful results
   - For tool-heavy waves: enforce a turn boundary before dispatching the next wave — do not fire the next wave in the same turn as receiving results
   - Urgency to immediately fire the next wave is a throttle-risk signal; treat it as a forced pause, not a reason to accelerate
   - Lightweight waves (inline answers, single fast lookups) do not require a pacing pause

1d. **Throttle-risk heuristic**
   - Declare **HIGH throttle risk** if any of the following apply:
     - Two or more consecutive waves were tool-heavy
     - Prior wave involved large context or many tool calls
     - Multiple waves dispatched in quick succession (pattern of rapid firing)
   - Under HIGH throttle risk: cap wave at 1–2 tasks; enforce turn boundary between waves; do not skip this check

1e. **Hard stop condition**
   - If 3 or more consecutive tool-heavy waves have executed, OR throttle risk has been HIGH for 2+ consecutive waves:
     - Stop. State what was completed and what remains.
     - Ask the user whether to continue before dispatching another wave.
   - Do not continue autonomously past this checkpoint.

2. **Map dependencies** — classify each as:
   - **HARD**: must wait for another task's output
   - **SOFT**: can proceed with a placeholder, assumption, or best-effort plan
   - List all "C waits for A" chains before starting; do not block unrelated work on soft dependencies

2a. **Check for file/resource conflicts**
   - Before marking two items as parallel, verify they touch different files, schemas, and docs
   - If two items would write to the same file (or one reads a file the other modifies), they are **sequential**, not parallel
   - Flag explicitly: "B waits for A — both touch `agent.py`."

3. **Dispatch current wave first**
   - Fire all tasks in the current wave in a single message before writing any inline answers
   - Do not dispatch future waves speculatively

3a. **Parallel execution rules**
   - Dispatch all parallel items in one message
   - Do not wait for results unless a dependent task requires them
   - If a task fails, retry once; if it fails again, mark it failed and continue
   - Never block unrelated work on a failed task

4. **State the plan explicitly**
   - One line: "Wave 1: [A, B] in parallel. [C] waits for A (wave 2). Answering [D–G] inline."

5. **Sequential execution constraint**
   - Sequential execution is only allowed when a dependency or resource conflict is explicitly identified

6. **Inline answers come last**
   - Write them after dispatching, so parallel work is already running while you type
   - Only answer inline items that have no unresolved dependencies
   - If an inline item depends on parallel work, defer it and state the dependency

7. **Never dump code inline**
   - All file edits and code changes go to a Cob subagent
   - Report only: what changed, which file, one-line summary
   - Never paste diffs or code blocks into main context
   - When writing a Cob prompt, instruct the agent to return only a brief summary (file, what changed, one line) — not file content, diffs, or long outputs. Long Cob results pollute context the same way inline code does.

   Also, never read large files inline via the Read tool in main context. Route file discovery to Explore subagents and implementation reads to Cob subagents. When requesting results from subagents, ask for summaries — not full file contents — unless the exact text is needed for planning decisions that can't be delegated.

7a. **Subagent amplification**
   - A single Cob subagent may internally trigger many tool calls (reads, edits, shell commands)
   - Treat any Cob task as **tool-heavy** when assessing wave size and throttle risk — even if it appears as one item
   - Do not undercount exposure by treating Cob tasks as lightweight

8. **Context discipline**
   - Send only the incremental context needed for the next wave — no full-prompt recaps
   - Prefer concise summaries over restating unchanged context
   - Reuse stable prompt structure across waves; avoid small wording changes that bust cache
   - If a task requires a lot of context, consider whether it can be split or merged first

9. **Commit code changes**
   - Commit only when a task (or logical group of tasks) is fully complete
   - Do not commit partial dependency chains
   - Stage only the specific changed files
   - Use a conventional commit message ending with:
     Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>

10. **Use unambiguous past tense in summaries**
    - Write "committed", "shipped", "done", "applied"
    - Never use "complete" or "complete X"

11. **Define completion**
    - A task is "done" only when all dependencies are resolved and outputs are produced
    - Do not mark dependent tasks as done prematurely

12. **Post-batch completion checklist**
After all work items are committed and done:
- Check whether auto-memory files or project MEMORY.md need updating based on what was learned this batch. Update them now, not later.
- Flag any playbook that should be created or updated from patterns discovered this batch — name it explicitly. If it can be written in under 5 minutes, write it. Do not let session learnings go unwritten while context is still fresh.
- Write any next-session prompts now while context is fresh, even if the session is not ending yet.
- **Always** close every batch with one of these explicit statements — no exceptions:
  - **"Context safe to clear — no handoff needed."** (minor work, nothing worth capturing)
  - **"Full /session-handoff recommended before clearing context."** (substantial work or learnings)
  Do not omit this even if the session feels small. The user cannot tell from Discord whether the terminal is done or just quiet.

When $ARGUMENTS is empty, apply this protocol to the items in the current user message.
When $ARGUMENTS contains items, treat those as the work list.

Usage: type `/batchc` followed by your task list in the same message, or use it as a prefix — the items after `/batchc` become the work list.
