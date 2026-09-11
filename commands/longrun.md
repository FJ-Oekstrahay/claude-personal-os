# /longrun — drain the feature queue with model-routed workers

the user said `longrun` (or its dictation alias `runqueue` / "run queue"). This is the **only** trigger
that starts an autonomous queue-draining run. Everything about the system:
`docs/MODEL-COORDINATION.md` in the project (games has it today).

## Modes — read the argument text

**This table is canonical.** `~/.claude/CLAUDE.md` and `docs/MODEL-COORDINATION.md` point here and
must not restate it; if you change a mode, change it only here.

| Argument | What you do |
|---|---|
| *(none)* | **Plan only.** Report the queue, propose items, name tiers and cost. **Execute nothing.** |
| `go` | Drain on **Max only** (Opus/Sonnet/Haiku). No metered spend. |
| `go cross` | Drain with `crossProvider: true` — GLM (flat) + Kimi (metered, flag the spend). |
| `go unattended` | Drain on **Max only** with **no approval gates**. Auto-queues from `data/backlog.json` under the §2U filter. Appends every decision to a run ledger. **Never asks a question**; on any self-abort condition it writes the report and stops. |
| `status` | Just `~/.claude/bin/feature-state.py status` + `list`. Nothing else. |
| `add ...` | Add items to the queue only; do not run the orchestrator. |

Anything you don't recognize → treat as bare `longrun` (plan only). Never guess your way into `go`.

`unattended` and `cross` are **mutually exclusive**. If the argument text contains both, run
Max-only and log the refusal — nobody authorises metered spend at 3am.

`go unattended` is normally launched by `~/.claude/bin/longrun-unattended.sh`, which supplies the
supervisor, the run stamp, and the restart-on-wedge watchdog. Typing it directly in a session works,
but that session has no watchdog: a hung MCP call stalls until a human notices.

## Step 0 — the first-run gate

**When may this section be deleted?** Only when `docs/MODEL-COORDINATION.md` §"What is NOT done" no
longer carries the "`feature-build.js` has never been run against real items" bullet. That bullet is
the tracking artifact: a clean validation run removes it *in the same commit* that removes this
section. Never delete this section on an agent's say-so that "it ran fine" — check the bullet.

**`feature-build.js` has never been executed against real items.** Four bugs were found by review,
zero by execution (`docs/MODEL-COORDINATION.md`, "What is NOT done"). So the **first** `longrun go`
is an E2E validation, not production work. On that first run:

- Cap it: `{ rounds: 1, maxPerRound: 1 }`, **one** item, Max-only. Do not honour `cross` on the first
  run — say why. (The default `maxPerRound` is 4; without this override the first run takes 4 items.)
- Follow `claude-config-mba/prompts/feature-build-e2e-validation.md` if it is present. (That prompt
  covers the cross-provider/ccx path for a later B2 run; the first run is Max-only.)
- Watch for the two silent failure modes specifically: a worker that does the work *itself* instead
  of routing (voids the whole point), and a `ccx` session that dies without reporting.
- Report what actually happened, including "it silently no-opped" if that's the truth.

Say plainly in the reply that this run *is* the validation.

**Under `unattended` the cap is not lifted — it auto-advances.** Round 1 is still
`{ rounds: 1, maxPerRound: 1 }`, Max-only. The run proceeds to normal batches **only if** that round
produces an item whose land result is `landed` with a sha on `main`; otherwise it self-aborts and
writes the report. An unattended run **may recommend** clearing the tracking bullet in its report but
**must never remove it, or this section, itself** — that stays an attended human act, per the
paragraph above.

## Step 1 — locate the state bus

```bash
FEATURE_STATE_REPO=$(pwd) python3 ~/.claude/bin/feature-state.py status
FEATURE_STATE_REPO=$(pwd) python3 ~/.claude/bin/feature-state.py list
```

If `FEATURE_LIST.json` doesn't exist in the CWD project, stop: this project has no queue.
Say so, and offer to `init` one — `python3 ~/.claude/bin/feature-state.py init`.

## Step 2 — if the queue is empty, REFUSE to run

Do not dispatch an orchestrator at an empty queue. Instead:

1. Propose 2–5 concrete items drawn from the current conversation, open `prompts/*.md`, or the
   latest handoff's "Pending" section.
2. For each: `id`, `title`, `epic`, `tier` (architect/worker/sweep/review), `--files` (enumerated),
   `--criteria` (checkable — it either holds or it doesn't).
3. Show the exact `feature-state.py add` commands. **Attended modes (bare / `go` / `go cross`):** get
   one go-ahead, then add them.
4. Only after the queue is non-empty does `go` mean anything.

An item without an enumerated file list or a checkable criterion is not queue work. Say so and
either fix it or drop it — do not queue a vague item and hope the worker figures it out.

### §2U — `unattended`: do not ask, filter and log

Under `unattended` there is no go-ahead. Apply the eligibility filter in the project's
`prompts/longrun-unattended.md` §2, add the passing items, and append one `queue_add` event per item
to the ledger recording the invented `files[]`, the invented `criteria`, and a one-sentence
rationale for each. Refusals and deferrals get `refuse`/`defer` events with the same detail.

The filter is the whole safety story, so the refuse list is not advisory: **never queue anything
that references `~/.claude` or any path outside the repo** — an unattended run must not edit its own
governance, its own orchestrator, or the hooks that gate its writes. A criterion that does not
actually verify the feature ("it compiles") is a fake pass; defer the item instead of inventing one.

## Step 3 — show the plan before executing (both `go` forms)

One compact table: item → tier → model it will actually route to → files. Then the totals: item
count, rounds, and — for `cross` — the metered-spend line (Kimi output is $15/M; GLM is flat).
Under the Max-5x rule, metered spend gets flagged every time, not once.

Under `unattended`, write that same table to the run ledger instead of to chat, then proceed. There
is nobody reading chat.

## Step 4 — run it

```
Workflow({
  scriptPath: '~/.claude/workflows/feature-build.js',
  args: { rounds: <n>, tiers: [...] }            // add crossProvider: true only for `go cross`
})
```

`crossProvider: true` appears **only** when the argument text literally contained `cross`. Never
add it because it seems faster or because the queue is large.

## Step 5 — report

Final queue state (`status` + `list`), what each worker committed, what failed and why. If any item
came back `blocked`, name the blocker and what would unblock it. Commit the queue file and any
worker output per the standing commit rule; push (games repo pushes by standing order).

## What `longrun` is NOT

- Not `orchcheck` — that recommends a mechanism and stops.
- Not `batchc` — that paces tool-heavy work inside this session.
- Not implied by "knock all these out" / "run it overnight". Only the literal word starts a run.
  **`go unattended` does not change this** — it removes the *approval gates inside* a run, never the
  trigger itself. "I'm going to bed, keep going" still requires the user to have typed `longrun`.
