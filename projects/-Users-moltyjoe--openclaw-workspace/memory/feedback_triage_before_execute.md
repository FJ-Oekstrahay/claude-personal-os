---
name: Triage before executing
description: Before writing code or executing a non-trivial task, ask Geoff if he wants to triage and delegate to Seymour (and potentially The Architect)
type: feedback
originSessionId: 3e02b599-6e27-4893-9470-7e504193c1fb
---
Before executing any non-trivial work (writing code, implementing features, making changes), consider whether to triage to Seymour, Cob, or The Architect — but apply judgment, not a blanket rule.

**Why:** Two priorities in order: (a) don't break things — careful execution matters most; (b) don't burn rate limit or fill context faster than needed.

**How to apply:**
- **Seymour (Haiku)**: mechanical tasks — file reads, simple writes, recon, scripts with no real risk. Saves tokens.
- **Cob (Sonnet)**: complex implementation that would bloat the main window, or parallelizable tasks. Same capability as Claudo — use when quality matters but context does too.
- **Claudo inline**: production config, live system, anything where a mistake is costly to reverse.
- **The Architect (Opus)**: design review, architectural decisions — not routine implementation.
- Ask Geoff one sentence max before triaging, don't over-explain.
