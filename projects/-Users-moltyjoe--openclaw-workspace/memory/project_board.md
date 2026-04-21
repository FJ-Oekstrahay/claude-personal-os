---
name: project_board
description: Location, purpose, and current snapshot of the project board — all active/blocked/someday work across OpenClaw, dev projects, and family projects
type: project
---

The project board lives at `~/.openclaw/workspace/projects/project-board/BOARD.md`. Live HTML: https://project-board-22t.pages.dev

**Why:** Persistent cross-session status view. Updated on session-handoff and when project status changes. Always update `_Last updated:` date at top.

**How to apply:** READ THE BOARD AT SESSION START. When work completes or changes status, update the board. When `/session-handoff` runs, update as part of that flow.

---

## Current state snapshot (as of 2026-03-30)

### Infrastructure
- **Browser Automation Hardening** — Playwright smoke + functional tests passed. Pending: resolve `.mcp.json` vs `~/.claude.json` config conflict, add anti-bot flag, run bot detection test, Geoff seeds cookies, failure mode tests, end-to-end via MoltyJoe.
- **Nightly workspace git commit cron** — NOT YET IMPLEMENTED. Auto-commit memory/playbook changes nightly. No technical blocker.
- **Handoff auto-archive** — NOT YET IMPLEMENTED. Move HANDOFF-*.md >3 days old to `handoffs/archive/`.
- **Token migration** — 6/6 secrets as SecretRefs. Blocked on openclaw supporting SecretRef for `embedding.apiKey` (lancedb plugin). openclaw.json still gitignored.
- **Lumpy improvement** — Root cause: Brave Search returns snippets only. Fix requires WebFetch/Playwright + Sonnet upgrade + strict citation rules.
- **Jarvis Talk Mode** — Config deployed. Pending: Geoff installs TestFlight app, connects to localhost:18789, sets wake word.
- **Discord channel permission matrix** — Pending: channel list from Geoff.

### Development & Sales Automation
- **TalonForge / Sales Automation** — Query triage architecture complete. `summaries/l3harris-latest.md` live. Next: evaluate query quality against expectations.
- **Prior Auth Voice Agent** — Phase 0 plan written. Next: Geoff gets Pablo's NPI + UHC prior auth number, runs Phase 0 recon call.
- **Traveloceros** — Phase 1 working. Phase 2 partially broken: hotels 400 error (`children_age[]` param), USA region search broken, budget UI needs rethink.

### Career Strategy
- **Strategy deep-dive** — Two Opus analyses done (Gary + Claudo). Next: Geoff reads both, answers 6 questions in BRAINSTORM doc, identifies first pilot prospect.
- **GitHub Showcase** — Up next: open-source agent governance framework + memory system.

### Family
- **Ethan Dashboard** — Live at https://fj-oekstrahay.github.io/ethan-dashboard/. Complete.

### Recently Resolved
- **LanceDB fixed (2026-03-27)** — stub `package.json` created at `/opt/homebrew/lib/node_modules/openclaw/dist/package.json`. Pre-installed runtime at `~/.openclaw/plugin-runtimes/memory-lancedb/lancedb/`. **Caveat: stub is wiped by `npm update -g openclaw` — must recreate after updates.**
- **Gateway switched to node@22** — node@22 22.22.2, wrapper at `gateway-wrapper.sh`.
- **openclaw.json.example committed** — sanitized template, 7 `YOUR_*` placeholders.
