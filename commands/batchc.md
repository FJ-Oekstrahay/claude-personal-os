Smartbatch execution protocol. Read the full prompt before touching anything, then:

0. **Check resource pressure** (before classifying anything)
   - **Read the per-session file, not the shared one.** Other Claude sessions on this machine write
     the legacy shared path too, so it often describes *someone else's* session:
     `cat ~/.claude/hooks/state/session-pressure-<session_id>.json` — fall back to
     `cat ~/.claude/hooks/state/session-pressure.json` only if the per-session file is absent, and
     when you do, check its `session_id` matches yours before trusting it.
   - If the file is missing or unreadable, treat as `normal`.
   - **elevated** (50–74% context): cap wave size at 2; enforce turn boundaries between all waves regardless of task weight.
   - **high** (75%+ context): cap wave size at 1; stop after each wave and ask the user before continuing.
   - If `checkpoint_due` is `true` and a `compact-checkpoint` has not been run this session: run `/compact-checkpoint` now, before dispatching any wave.
   - **Quote the absolute numbers, not just the level**, so a mis-tiered denominator is visible
     rather than silently throttling you: "Wave 1 [normal · 118k/1.0M · opus-5]: ...". `fill_pct` is
     `context_tokens / context_window`, and `context_window` is resolved from the model
     (1M for opus-5/sonnet-5/fable-5-class, 200k for haiku-class) with a self-healing promote.
     If `context_window` looks wrong for the model you are running, say so — do not just obey it.
   - **Check `fill_stale` before quoting those numbers.** When it is `true`, this tick had no usage
     record and `fill_pct` / `context_tokens` / `context_window` are carried over from an earlier
     one — `pressure` was recomputed from `wave_density` instead. Say so rather than quoting them as
     current: "Wave 1 [normal · 118k/1.0M · opus-5 — carried over, not fresh this turn]". Without
     this the state can read `fill_pct: 0.82` alongside `pressure: normal` and you would quote both.

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
   - Check `wave_density` from the §0 state file before dispatching: if `wave_density` ≥ 30, treat rapid-fire urge as a confirmed throttle signal — pause, do not accelerate. If the field is missing, treat as 0 (normal). Note `wave_density` is **machine-global** — it counts every session's tool calls in the last 60s from a shared log — so a busy peer can trip it. It only ever over-reports, so it fails safe; if you stop on it, say a peer may be the cause rather than blaming your own pacing.
   - Lightweight waves (inline answers, single fast lookups) do not require a pacing pause

1d. **Throttle-risk heuristic** — applies by default per CLAUDE.md's "Default-on safety posture" to ANY 2+ parallel `Agent`/`Workflow` dispatch, not only when this file is explicitly invoked as `/batchc`.
   - Read `wave_density` from the §0 state file (tool calls in the last 60 seconds across **all** sessions, written by `wave-counter.py`):
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

1f. **Autonomy budget — `/batchc auto [N]`**
   - Default (`/batchc` with no `auto`): unchanged — gate at every wave boundary as 1c/1e describe.
   - With `auto`: **self-continue** across wave boundaries without asking, up to **N waves**
     (default 6), as long as *all* of these hold at the start of each wave:
     - `pressure` is `normal` **and** `checkpoint_due` is false. `checkpoint_due` is not itself a
       stop: take §0's remedy — run `/compact-checkpoint`, then continue on the budget. It becomes a
       stop only if it is still true afterwards.
     - `wave_density` < 30
     - no task in the previous wave failed twice (1 retry per 3a is fine)
     - no queued item touches a **live shared surface** (the §11 path list) or a
       hardware-safety surface — those always stop for the user, regardless of `auto`
   - **What `auto` changes in 1c and 1e — stated explicitly, because "self-continue" is otherwise
     a no-op.** In Claude Code, ending your turn *is* handing control to the user, so 1c's "turn
     boundary" and "ask the user" are the same act. Under `auto`:
     - 1c's turn boundary is satisfied by **waiting for the previous wave's tool results** before
       dispatching the next one — a results boundary, not an end-of-turn. You still never fire two
       tool-heavy waves without seeing the first one's output.
     - 1e's "3 or more consecutive tool-heavy waves" limit is **raised to N** for the duration of
       the budget. Without this, `auto` maxes out at 3 on Cob waves (§1b/§7a make every Cob task
       tool-heavy) and the documented default of 6 could never be reached. Every *other* 1e
       condition — `wave_density` ≥ 60 twice running — still hard-stops and outranks the budget.
   - The moment any condition breaks: stop, state what completed and what remains, ask. `auto` buys
     you consecutive waves; it never buys you past a real signal.
   - Emit one line per wave so the run is followable — on Discord sessions use
     `mcp__plugin_discord_discord__edit_message` on a single progress message rather than a new
     `reply` per wave (edits don't push-notify; the §12 closing reply does).
   - Budget the whole run before starting: state the wave count and the rough token/rate-limit share
     you expect to spend, per the Max-5x rule. `auto 6` on tool-heavy Cob waves is not a small run.

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
    - **Independent verifier gate (generator→critic):** A task is NOT done until a separate agent context has reviewed it. The agent that wrote the code does not verify its own work. **Writing a handoff does not satisfy this** — a handoff records that work happened; it is not evidence anyone reviewed it.
      - **Trigger — risk, not just file count.** The gate applies when *either* holds:
        1. the task touched **more than one file**, or
        2. the task touched a **live shared surface** — anything under `~/.claude/hooks/`, `~/.claude/commands/`, `~/.claude/agents/`, `~/.claude/skills/`, `~/.claude/output-styles/`, `~/.openclaw/bin/`, `~/Library/LaunchAgents/`, or `settings.json` / `settings.local.json`. One edit there changes behavior for **every session on this machine**, so file count is irrelevant.
      - **The requirement is the intent, not a specific command.** Two mechanisms satisfy it:
        1. **Dispatch a reviewer subagent via the Agent tool** — this is the one *you* can always do, and it is the default.
           - **Default reviewer: `cto` or `gadfly` (both Sonnet).** Proportionate cost for an ordinary change.
           - **Escalate to `The Architect` (Opus)** only when the change is genuinely hard — subtle control flow, concurrency, a security or data-loss surface, or anywhere being wrong is expensive. Opus draws on the weekly cap; spend it deliberately, not by default.
           - **`Safety Officer` (Opus)** for flight-controller or hardware-safety surfaces, regardless of size.
           - Any other `subagent_type` (`general-purpose`, `cob`, `seymour`) counts only if you put the literal marker `[verifier-gate]` in the Agent prompt — that stops a routine search agent from disarming the gate by accident.
        2. **Ask the user to run `/verify` (behavioral, drives the app) or `/code-review` (diff-level analysis).** Both are real built-in commands compiled into the CC binary — they are NOT files under `~/.claude/commands`, so a filesystem sweep will wrongly conclude they don't exist. Both are registered `userInvocable` + `disableModelInvocation` (verified in binary v2.1.218), so **the harness structurally refuses to let you call them.** Asking the user to type one is the correct move, not a failure to report.
      - **Never** tell the user you are "blocked", that "`/code-review` isn't available in this session", or that "`/verify` doesn't exist anywhere on disk." All three are false; mechanism 1 is always open to you. The "only when the user has explicitly opted into multi-agent orchestration" restriction belongs to the **Workflow** tool — do not generalize it to the Agent tool, which needs no opt-in.
      - Run the verifier in a fresh agent context — never in the same Cob instance that did the writing.
      - **The review must come AFTER the last code edit it covers.** A reviewer dispatched early in the batch does not cover files edited later, and the hook enforces this: any Write/Edit resets the detection, so only a verifier dispatched after the final substantive edit counts. If you fix something the reviewer flagged, that fix is itself unreviewed — re-run the reviewer or say plainly that the fix went in unreviewed. (Writing the HANDOFF file does not count as a code edit and does not reset the gate.)
      - Token tradeoff: this adds ~1 agent per multi-file task. That cost is load-bearing; absorb it.
        Note it is ~1 agent **per run, not per wave**: because the review must come after the last
        edit it covers, one verifier dispatched at the end of an `auto` run covers every file that
        run touched. Longer autonomous runs make this gate *cheaper* per unit of work, not dearer —
        so it is not a reason to shorten a run, and it is never a thing to trade away for tokens.
      - Skip for single-file Haiku-routed mechanical edits (per §7b) **that are not on a live shared surface**: the change is immediately visible on inspection and the gate adds no value there. A one-line edit to a live hook is not covered by that exemption.
      - **This gate is hook-enforced.** `batchc-stop-gate.py` scans the session transcript at Stop time. If the trigger above is met (>1 distinct file written/edited, **or** any edit to a live shared surface) with no independent review detected, it blocks the stop — appending a verifier reminder to the §12 checklist message, or, if the handoff is already written, emitting the verifier reminder alone. The block fires at most once per session (one-shot marker). Detection covers: an `Agent`/`Task` call matching mechanism 1 above, a `Skill` call whose name is exactly `verify` or `code-review`, and a the user-typed `/verify` or `/code-review` in the transcript. It deliberately has **no Bash branch** — the old substring match on `"/verify"` was satisfied by the *file path* `scripts/verify_claims.py`, so every financial re-anchor silently disarmed the gate.
    - **Threshold note — RESOLVED 2026-07-24.** The old ">1 file" line underfired on exactly the changes that mattered most. Rather than a blanket ">0 files" (which would nag on every ordinary single-file edit until the gate got ignored), the trigger is now risk-based: >1 file **or** any live shared surface, enumerated above. the user's call; the path list is deliberately narrow and is the thing to extend if it turns out to underfire again.

12. **Post-batch completion checklist**
After all work items are committed and done:
- Check whether auto-memory files or project MEMORY.md need updating based on what was learned this batch. Update them now, not later.
- **A REJECT verdict from §11's verifier gate is itself a trigger**: write (or confirm Auto Memory already wrote) a `feedback`-type memory entry documenting why the reviewer rejected it, before closing the batch. This replaces the old `/capture-pair` nudge — that command is retired (it duplicated Auto Memory's `feedback` type and was never used; see `distillation/checklist.md`'s history in claude-config). Auto Memory writes `feedback`/`project`/`reference`/`user` entries automatically with no separate command; the point of this line is to make sure a rejection specifically doesn't get fixed and forgotten without one.
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

**Strip the mode arguments first.** If $ARGUMENTS begins with `auto`, consume it — and an integer
immediately after it, if present — as the §1f autonomy budget. What remains is the work list.
`/batchc auto 4 fix X` means "budget 4 waves, work list = [fix X]", never a work item called
"auto 4". If nothing remains after stripping, fall back to the items in the current user message.

Usage: type `/batchc` followed by your task list in the same message, or use it as a prefix — the items after `/batchc` become the work list.
Add `auto` (optionally `auto N`) as the first argument to grant the §1f autonomy budget: `/batchc auto 4 <task list>`.

Token levers for long runs — verified against `claude` 2.1.231, not folklore:
`~/.openclaw/workspace/memory/playbooks/long-run-token-levers.md`. Read it before changing any
model / thinking / context env var. The short version: **never set `CLAUDE_CODE_SUBAGENT_MODEL`** —
it silently overrides every explicit `model:` you pass to the Agent tool, including the §11
reviewers and `Safety Officer`.
