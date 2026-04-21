---
name: BBQUERY in-session capability
description: Concept for JARFACE to query blackbox analyst mid-conversation using natural language tags
type: project
originSessionId: 797cc8e9-0aae-4ee4-84ca-3fcf9598f994
---
During a Cob overreach session (2026-04-18), a BBQUERY system was sketched out. The concept is valuable:

JARFACE emits `[BBQUERY: <natural language question>]` on its own line mid-response. The CLI intercepts this tag, converts it to a structured analyst query, sends it to the bb_analyst subprocess, and injects the analyst's text response before the next turn. JARFACE can then answer the pilot with actual numbers from the log.

Example emissions:
- `[BBQUERY: show motors and gyro from t=24.5 to t=27.5]`
- `[BBQUERY: full resolution around t=24.9]`
- `[BBQUERY: show worst crash event]`
- `[BBQUERY: event 0 with 2s pre and 4s post]`

The heuristic parser (`_bbquery_to_json`) converts these to structured dict queries. The `_query_analyst` function communicates with the analyst subprocess via JSON stdin/stdout.

**Why it matters:** Currently JARFACE gets a pre-analyzed summary injected at session start. If a pilot asks "what was happening at t=24?" JARFACE can't answer without this system. BBQUERY makes blackbox analysis interactive rather than a one-shot pre-session injection.

**Status:** Concept only — code was in Cob's overreach (since discarded). Needs spec review before implementing. Not a blocker for v1 but a strong v1.5 capability improvement.

**Why:** Closes the gap between "JARFACE has BB summary" and "JARFACE can dig into specific moments on demand" — which is what real debugging requires.

**How to apply:** Before implementing, run Gadfly (is this better than just running BBE yourself?) and Architect (how does BBQUERY interact with the existing analyst subprocess lifecycle?).
