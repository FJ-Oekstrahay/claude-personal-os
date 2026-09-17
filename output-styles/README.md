# output-styles/

Output styles: markdown files with frontmatter (`name`, `description`, `keep-coding-instructions`)
that Claude Code loads when the user runs `/output-style <name>`, replacing part of the model's
default behavior for the rest of the session.

| File | What it does |
|---|---|
| `engineering-rigor.md` | Senior-engineer default for real-infrastructure directories. Requires a one-line THROWAWAY/EXTENSION declaration before any code file is created or modified, sourcing every hardcoded constant from the config that owns it (or citing `file:line`), checking for reusable tooling before writing something new, handling the failure modes actually reachable with real data, stopping to present options before non-trivial extensions, and verifying claims with real command output rather than "should work." |
| `quick-explore.md` | The deliberate escape hatch from `engineering-rigor`, for a genuine one-off question. Everything written is treated as THROWAWAY and confined to a `scratch/` directory, with no options gate or plan-mode ceremony. A correctness floor (print assumptions, sanity-check magnitude) and a safety floor (no writes outside `scratch/`, no editing hooks or live config) still apply. |

## Notes

- `engineering-rigor.md` names `quick-explore` explicitly as its own escape hatch, and
  `quick-explore.md` names switching back to `engineering-rigor` as its own escape hatch for when a
  one-off turns out to need real, reusable code. They're designed as a pair, not two unrelated
  styles.
- The THROWAWAY/EXTENSION distinction that `engineering-rigor.md` codifies is otherwise documented
  in a project's own `CLAUDE.md`; the output style mirrors it so the same discipline applies by
  default in any directory, not only where it's spelled out locally.
