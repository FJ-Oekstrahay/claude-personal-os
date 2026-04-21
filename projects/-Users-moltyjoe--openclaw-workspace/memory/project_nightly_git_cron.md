---
name: Nightly workspace git commit cron
description: Planned but unimplemented nightly auto-commit for workspace memory/playbook changes
type: project
---

Nightly workspace git commit + push is planned but not yet implemented.

**Why:** Memory and playbook edits happen throughout the day but aren't committed automatically — risk of losing changes.

**How to apply:** When this comes up, don't treat it as new/unknown. It's on the project board (Infrastructure > Up Next and In Progress). No technical blocker — just hasn't been built. Candidate implementation: launchd plist or CronCreate running `git add -A && git commit && git push` nightly from `~/.openclaw/workspace/`.
