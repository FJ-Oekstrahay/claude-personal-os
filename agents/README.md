# agents/

Subagent definitions: each file is a markdown prompt with YAML frontmatter (`name`, `description`,
`model`, and for some, `color`/`memory`) that Claude Code loads when dispatching work to that
subagent type. The frontmatter's `description` is also what the top-level session reads to decide
when to reach for a given agent.

| Name | File | Model | Role |
|---|---|---|---|
| The Architect | `architect.md` | opus | Harsh structural reviewer for code, plans, and architecture. Reads everything before commenting; reports bugs, edge cases, and design trade-offs by severity. Report-only, no fixes, no code. |
| Claudio | `claudio.md` | sonnet | General-purpose catch-all for writing, analysis, planning, or research that doesn't fit Cob (implementation) or Seymour (mechanical work). |
| Cob | `cob.md` | sonnet | Full-capability implementation delegate. Used for context isolation or parallelizing work that requires real reasoning; it runs the same model as the main session, so it's not a cheaper option. |
| CTO | `cto.md` | sonnet | Pragmatic reviewer for build sequencing, architectural coherence, and what to defer. Runs after Gadfly when product direction is involved. |
| Gadfly | `gadfly.md` | sonnet | Hostile product skeptic. Argues from the user's point of view, finding pain, wrong assumptions, and what would make a user quit. Runs before CTO. |
| Safety Officer | `safety-officer.md` | opus | Hardware-safety and user-facing-risk reviewer for drone/flight-controller work. First question on every review is unexpected prop spin; ends with a Ship / Ship with mitigations / Do not ship recommendation. |
| Seymour | `seymour.md` | haiku | General-purpose cheap/mechanical task executor: file operations, shell commands, research extraction, simple writing. Reports back and stops if it hits something requiring judgment. |

## Sequencing rule: Gadfly before CTO

`../commands/review-sequence.md` sets an explicit order when both product-skeptic and
build-sequencing review apply to the same work: Gadfly runs first, CTO second. The file's own
reasoning: "If CTO runs first, it produces a polished, internally coherent plan. Gadfly responding
inside that frame is already anchored and outgunned — it argues at the margins instead of
questioning the premise." Running Gadfly on the raw idea first gives unbiased product pushback,
which CTO then incorporates. The one exception is when CTO's output is needed to scope what Gadfly
should evaluate. In that case CTO runs first, but Gadfly is bumped to Opus for the follow-up to
match the model tier.
