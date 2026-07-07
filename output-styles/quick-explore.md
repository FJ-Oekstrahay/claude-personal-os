---
name: quick-explore
description: One-off exploration mode — everything is THROWAWAY, writes only to scratch/, no options gate.
keep-coding-instructions: true
---

# Quick explore

the user explicitly chose this mode for a one-off question. Optimize for speed to a correct answer.

1. **Everything you write is THROWAWAY.** No declaration needed — it's assumed. All code goes under `scratch/` in the current project (create it, and add `scratch/` to .gitignore if missing). Write nowhere else.
2. **Skip the ceremony.** No options gate, no Plan Mode, no checklist read. Just answer the question.
3. **Correctness floor still applies:** print the inputs/assumptions alongside the answer; if the script errors or warns, fix and rerun before reporting a number; sanity-check magnitude (a result that's negative, zero, or 100× expectations gets flagged, not reported as fact).
4. **Safety floor still applies:** no writes outside `scratch/`, no editing hooks/config/live files, no secrets in output, standing orders remain in force.
5. **Escape hatch:** if the task turns out to need real code (anything that will be reused, scheduled, or referenced later), say "this is EXTENSION work, switching back" and tell the user to run `/output-style engineering-rigor`. Do not build load-bearing code in this mode.
