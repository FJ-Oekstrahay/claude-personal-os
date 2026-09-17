# templates/

Skeletons meant to be copied and filled in for a specific project, rather than used as-is. None of
these are auto-installed or auto-loaded anywhere; each is on-demand, opt-in per project.

| File | What it does |
|---|---|
| `epistemic-policy-skill-template.md` | Skeleton for a domain-expert skill or persona whose wrong answers carry real cost: money, health, hardware, legal exposure. Structures the core rule as: look up fixed facts before reasoning from memory, distinguish FACT / EMPIRICAL GUIDANCE / PREFERENCE-JUDGMENT claim types, never guess a domain's destructive fixed facts (voltage limits, statutory thresholds, dosing), and surface uncertainty instead of inferring past it. |
| `orchestrated-prompt-template.md` | Skeleton for a prompt that specifies a task's spec in plain English alongside an optional Workflow script to run it, with a warning up front that a `.md` file isn't itself executable via `Workflow({scriptPath})`, so the script has to be extracted to a real `.js` file or passed inline before it can run. |

## `hooks/`: hook templates

Three hook skeletons, each meant to be copied into a project's own `.claude/hooks/`, filled in, and
registered in that project's `.claude/settings.json`.

| File | Event | What it does |
|---|---|---|
| `inject-file-at-sessionstart.sh` | SessionStart | Unconditionally injects a file's contents into every new session, e.g. a project's curated memory file, so the model doesn't have to remember to go read a `CLAUDE.md` pointer. Fails open: a missing file degrades to a stderr warning rather than blocking the session. |
| `reinject-core-at-prompt.sh` | UserPromptSubmit | Re-injects a small, fixed snippet on every turn so mid-session context compaction can't silently drop it. Meant to stay short: a re-injection hook, not a place to dump a whole playbook. Fails open. |
| `stop-tripwire.py` | Stop | Compares two files' line counts against a SessionStart snapshot; if one grew and its paired record-keeping file didn't, writes a flag file for the next SessionStart to surface. Can't block retroactively at Stop, so it turns a silent miss into a visible one next session. Fails open, and is written to be idempotent against a Stop event firing more than once per turn. |

## Notes

- Every hook template documents, in its own header comment, that it fails open by design. A
  template for a *blocking* hook would need to fail closed instead, and each header says so
  explicitly rather than leaving that as an implicit assumption.
- `epistemic-policy-skill-template.md` was extracted from a working skill, not written from
  scratch; its guidance comments call out which parts to keep close to the original phrasing rather
  than soften.
