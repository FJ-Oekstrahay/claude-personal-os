---
name: Subagent delegation and context hygiene
description: How to delegate to Seymour / Explore / Architect to keep the main context window clean — what to pass, what to return, and when to break the rule
type: feedback
originSessionId: 3e02b599-6e27-4893-9470-7e504193c1fb
---
Keep the main thread decision-only. Push mechanical work to subagents. Don't let raw file contents, diffs, or log dumps accumulate in the main window.

**Why:** Context bloat is the real failure mode. Once the window fills with file reads and code blocks, reasoning quality degrades and compaction becomes mandatory. Subagents have isolated contexts — that's the point.

**How to apply:**

## Classify the work first

Every non-trivial task maps to a tier:

| Work type | Who does it | Why delegate |
|---|---|---|
| File searches, codebase exploration, recon | Explore agent | Fast + cheap |
| File reads + writes, shell commands, mechanical edits | Seymour (Haiku) | Saves tokens |
| **Document editing: redlining, rewrites, business plans, long-form text** | **Seymour (Haiku)** | **File contents must NOT fill main context** |
| Complex programming that would bloat main context | Cob (Sonnet) | Context isolation |
| Parallelizable implementation tasks | Cob (Sonnet, multiple) | Parallelism |
| Production config, live system, risky to reverse | Claudo inline | Need full control |
| Design critique, architectural second opinion | The Architect (Opus) | Quality review |
| Planning a complex implementation | Plan agent | Structured output |

**Seymour vs Cob:** Seymour saves tokens (Haiku vs Sonnet). Cob preserves context (same quality, isolated window). Use Seymour when the task is genuinely cheap. Use Cob when the task needs real reasoning but shouldn't fill the main window.

## What to pass to subagents

- Goal (1-2 sentences)
- Key constraints ("preserve async patterns", "don't touch IDENTITY.md")
- File paths to read, not file contents
- Decisions already made in the main thread
- Agent autonomy offer: they may spawn Seymour or copies of themselves

Do NOT pass: large file contents, raw diffs, long logs.

## What subagents return

Instruct: "Return only: success/fail, key changes in under 100 words, risks and next steps. No raw file contents, no full diffs, no logs."

If I need to see specific code to make a decision, I pull that slice inline — not the whole file, not the whole diff.

## Main thread rule

- Plan here: architecture, tradeoffs, validation criteria
- Issue instructions to subagents with distilled context
- Review distilled results, iterate
- Only pull exact content into main context when a decision genuinely requires it

**Never read document content inline** (business plans, redlines, essays, long markdown files) — even when the task seems "quick." These files are long and bloat fast. Delegate to Seymour: give it the file path, the edit instructions, and nothing more.

## When to break the rule

- Geoff explicitly asks to see the code/output
- A subtle bug requires reading exact content to diagnose
- The subagent result is ambiguous and I need to verify

Even then: pull the relevant slice, not the whole file.

## Do not confuse with model tiering

This is about context hygiene (what stays out of the main window), not about which model tier is cheapest. See `feedback_model_tiering.md` for the Haiku/Sonnet/Opus cost breakdown.
