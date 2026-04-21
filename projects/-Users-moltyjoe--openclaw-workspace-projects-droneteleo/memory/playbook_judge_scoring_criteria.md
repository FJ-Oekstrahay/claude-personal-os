---
name: Judge scoring criteria wording
description: How to phrase judge rubric criteria to avoid ambiguous "don't fabricate X" instructions being read as "don't mention X at all"
type: feedback
originSessionId: c0884e37-2b6e-42e8-b9df-8527a068ad7c
---
Phrasing like "does not fabricate X values that differ from context" is ambiguous — the judge may read it as a prohibition on mentioning X at all, rather than a constraint on accuracy.

**Why:** The judge interprets negatively-framed criteria conservatively. "Don't fabricate X" reads as "avoid X entirely," which causes false negatives when the answer correctly states X from context.

**How to apply:** Rewrite ambiguous criteria in the positive form:

- Instead of: "does not fabricate X values that differ from context"
- Write: "only states X values present in context, exactly as given"

This makes it clear the agent *should* mention X — as long as it matches the provided context. Apply this pattern to any rubric criterion that combines a factual value with a prohibition on invention.
