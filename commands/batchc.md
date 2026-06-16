Smartbatch execution protocol. Read the full prompt before touching anything, then:

0. **Check resource pressure** (before classifying anything)
   - Run: `python3 -c "import json; d=json.load(open(os.path.expanduser('~/.claude/hooks/state/session-pressure.json'))); print(d['pressure'], d['tool_calls'], d['checkpoint_due'])" 2>/dev/null` — or simply `cat ~/.claude/hooks/state/session-pressure.json`.
   - If the file is missing or unreadable, treat as `normal`.
   - **elevated** (50–74% context): cap wave size at 2; enforce turn boundaries between all waves regardless of task weight.
   - **high** (75%+ context): cap wave size at 1; stop after each wave and ask the user before continuing.
   - If `checkpoint_due` is `true` and a `compact-checkpoint` has not been run this session: run `/compact-checkpoint` now, before dispatching any wave.
   - State the pressure level in your wave plan line: "Wave 1 [pressure: elevated]: ..."

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
   - Check `wave_density` from `~/.claude/hooks/state/session-pressure.json` before dispatching: if `wave_density` ≥ 30, treat rapid-fire urge as a confirmed throttle signal — pause, do not accelerate. If the field is missing, treat as 0 (normal).
   - Lightweight waves (inline answers, single fast lookups) do not require a pacing pause

1d. **Throttle-risk heuristic**
   - Read `wave_density` from the state file (tool calls in the last 60 seconds, written by `wave-counter.py`):
     - **wave_density < 30** — normal; no special constraint
     - **wave_density 30–59** — elevated burst; reduce wave to 1–2 tasks, enforce turn boundary
     - **wave_density ≥ 60** — HIGH; cap wave at 1 task, enforce turn boundary, do not skip this check
   - If state file is missing or unreadable, fall back to the subjective heuristics below as a conservative default:
     - Two or more consecutive tool-heavy waves, OR prior wave involved large context, OR rapid firing pattern

1e. **Hard stop condition**
   - If `wave_density` ≥ 60 for two consecutive waves, OR 3 or more consecutive tool-heavy waves have executed:
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

6. **Inline answers come last — but in the same turn as dispatch**
   - Write them after dispatching, so parallel work is already running while you type
   - **CRITICAL:** Inline answers MUST appear in the same assistant turn as the dispatch call — text before or after the tool call in a single message. Do NOT write them in a separate follow-up message after tool results return. A separate turn means the user waits for all parallel work to finish before seeing your answers — that defeats the purpose.
   - **Discord sessions:** When any message in the current conversation arrived via a `<channel source="plugin:discord:discord">` tag, inline answers must be sent via `mcp__plugin_discord_discord__reply` using the `chat_id` from that tag — in the same turn as dispatch. Text output alone is invisible to the Discord user. Use the `text` parameter (not `content`). If the inline answer is short, combine it with the dispatch context (e.g., "Working on X and Y in parallel — here's the answer to Z: ..."). This is required even if the post-batch checklist will also send a reply — don't make the user wait for parallel work to finish to see an answer you already have.
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

7b. **Subagent model routing — pick before dispatch**
   - Default to **Haiku** (`model: "haiku"`) when ALL of these are true:
     - Spec is fully enumerated: exact field, exact value, no inference needed
     - Changes are localized: single file or independent files, no cross-file reasoning
     - Failure is immediately visible in review (wrong field is obvious on inspection)
     - You'd hand this to a checklist executor with no judgment required
   - Default to **Sonnet** when ANY of these are true:
     - Spec is ambiguous or requires judgment to resolve
     - Cross-file consistency is required
     - Silent errors are dangerous (output looks plausible even if wrong)
     - Task involves governance text, playbooks, or output that feeds downstream reasoning
     - Structural traps exist (repeated field names, nested sections where context determines which instance to edit)
   - Never dispatch Cob at Sonnet for a task that is purely "apply this enumerated spec"
   - When in doubt: Sonnet. The cost of a silent Haiku error exceeds the cost of Sonnet overspend.
   - No routine spot-check required after Haiku dispatch on genuinely mechanical tasks — the catch layer is the user's review

7c. **Tool/reasoning boundary — apply when writing subagent prompts**
   - The agent decides *which* tool to invoke and *when*. The tool owns *how* — implementation details, parameters, pacing, defaults.
   - If a subagent prompt requires you to supply low-level implementation details (wordlists, retry counts, exact encoding schemes, pacing intervals), that's a design smell. Those belong inside the tool, not in the agent's prompt.
   - Rule of thumb: if a parameter answers "what to do," the agent supplies it. If it answers "how to do it," the tool owns it.
   - When you spot this pattern, flag it: "This is a tool/reasoning boundary issue — the agent shouldn't need to know X, the tool should own that."

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
   - When prompting Cob subagents to commit, instruct them: "End the commit message with Co-Authored-By using your actual model name. If your model name is unavailable or reports as 'synthetic', write: Co-Authored-By: Claude (model unknown) <noreply@anthropic.com>"
   - Never fabricate a model name. "model unknown" is correct; a wrong model name is not.

10. **Use unambiguous past tense in summaries**
    - Write "committed", "shipped", "done", "applied"
    - Never use "complete" or "complete X"

11. **Define completion**
    - A task is "done" only when all dependencies are resolved and outputs are produced
    - Do not mark dependent tasks as done prematurely
    - **Independent verifier gate (generator→critic):** When a task touched more than one file, it is NOT done until a separate agent context has reviewed it. The agent that wrote the code does not verify its own work.
      - **Feature/behavior changes** → run `/verify` (behavioral, drives the app)
      - **Structural/spec changes** → run `/code-review` (diff-level analysis)
      - Run the verifier in a fresh agent context — never in the same Cob instance that did the writing.
      - Token tradeoff: this adds ~1 agent per multi-file task. That cost is load-bearing; absorb it.
      - Skip for single-file Haiku-routed mechanical edits (per §7b): the change is immediately visible on inspection and the gate adds no value there.
      - **This gate is hook-enforced.** `batchc-stop-gate.py` scans the session transcript at Stop time. If it finds >1 distinct file written/edited with no subsequent `/verify` or `/code-review` call, it blocks the stop and appends a verifier reminder to the §12 checklist message. The block fires at most once per session (one-shot marker).
    - **Threshold note for the user:** The ">1 file" line will underfire as tasks grow in scope. For anything touching live config or shipped code, consider tightening to ">0 files" — every change to production surfaces deserves a second context regardless of file count.

12. **Post-batch completion checklist**
After all work items are committed and done:
- Check whether auto-memory files or project MEMORY.md need updating based on what was learned this batch. Update them now, not later.
- Flag any playbook that should be created or updated from patterns discovered this batch — name it explicitly. If it can be written in under 5 minutes, write it. Do not let session learnings go unwritten while context is still fresh.
- Write any next-session prompts now while context is fresh, even if the session is not ending yet.
- **Handoff is automatic, not advisory.** If the batch involved substantial work or learnings and no handoff has been written yet, run `/session-handoff` NOW — pick a descriptive name yourself (format: `HANDOFF-<topic>-<YYYY-MM-DD>-<HHMM>.md`). Never tell the user a handoff is "recommended" or ask whether to run one — recommending is a protocol failure. The only reason to skip is that the work was genuinely minor.
- **Always** close every batch with one of these two explicit statements — no exceptions, no third option:
  - **"Context safe to clear — no handoff needed."** (minor work, nothing worth capturing)
  - **"Handoff written — context can now be cleared."** (handoff was run this batch — either earlier or via the automatic step above)
  Do not omit this even if the session feels small. The user cannot tell from Discord whether the terminal is done or just quiet.
- **Discord-bound sessions — REQUIRED BLOCKER:** If any message in this session arrived via Discord (i.e., a `<channel source="plugin:discord:discord" chat_id="...">` tag was present), you MUST send the closing statement via `mcp__plugin_discord_discord__reply` using the `chat_id` from the most recent inbound Discord message. Use the `text` parameter (not `content`). This step is NON-OPTIONAL — skipping it is a failure of the batch protocol. Do not rely on terminal output alone — the user is watching Discord, not the terminal. This is the FINAL action of the batch; nothing comes after it.

When $ARGUMENTS is empty, apply this protocol to the items in the current user message.
When $ARGUMENTS contains items, treat those as the work list.

Usage: type `/batchc` followed by your task list in the same message, or use it as a prefix — the items after `/batchc` become the work list.
