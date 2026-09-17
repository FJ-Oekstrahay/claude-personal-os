# skills/

Skills: each subdirectory holds a `SKILL.md` that Claude Code auto-loads when its trigger
conditions match the conversation, or that the user invokes directly by name. Unlike a command, a
skill's instructions can be pulled in automatically without the user typing anything.

| Skill | File | What it does |
|---|---|---|
| `compact-checkpoint` | `compact-checkpoint/SKILL.md` | Writes a session-summary checkpoint file before running `/compact`, so context compaction doesn't lose the current task state. |
| `convert-doc` | `convert-doc/SKILL.md` | Converts markdown or in-context text to a shareable file. Picks HTML, PDF, or DOCX from request signals (never asks), using pandoc and, for PDF, headless Chrome rather than a LaTeX toolchain. |
| `critic` | `critic/SKILL.md` | Harsh persistent reviewer. Tears apart whatever is pasted after `/critic` (plan, code, config, or architecture decision), tagging each issue BLOCKER/MAJOR/MINOR and ending with a SHIP/REWORK/SCRAP verdict. Report-only. |
| `cto` | `cto/SKILL.md` | Spawns the `cto` subagent with the content under review (and any Gadfly findings already in context) passed in, then saves the review to a dated file and flags if it recommends an Opus re-run. |
| `deep-research` | `deep-research/SKILL.md` | Fan-out research harness invoked via the capped `~/.claude/workflows/deep-research.js` Workflow script: searches, fetches sources, adversarially verifies claims by majority vote, and synthesizes a cited report at roughly 28 agents total (1 scope + ~6 search + 5 fetch + 15 verify + 1 synth with the script's current caps) instead of the uncapped version's much larger fan-out. |
| `gadfly` | `gadfly/SKILL.md` | Spawns the `gadfly` subagent with the content under review passed in, saves the review to a dated file, and reminds that Gadfly runs before CTO when both apply. |
| `snapshot` | `snapshot/SKILL.md` | Writes a short handoff-style snapshot file (what we're doing, current state, key paths, next step) from the conversation so far, with no further summarization or agent spawning. |
| `visualize` | `visualize/SKILL.md` | Turns a data or chart request into a rendered visualization (matplotlib PNG for static charts, a self-contained HTML file with a CDN library for interactive ones), delivered as an attachment or file path. |

## Notes

- `critic`, `cto`, and `gadfly` correspond to the reviewer roles described in
  `../commands/review-sequence.md` and `../agents/README.md`; the skill is the invocation
  mechanism, the agent file is the reviewer's actual instructions.
- `deep-research`'s agent-count math (search/fetch/verify counts and how each changes as the caps
  are edited) lives in the skill file itself and in `../workflows/README.md`.
