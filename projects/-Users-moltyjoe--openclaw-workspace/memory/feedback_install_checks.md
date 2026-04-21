---
name: Check before suggesting installs
description: Always verify a tool is absent before suggesting installation, and check for conflicts
type: feedback
---

Before telling Geoff to install or upgrade anything:

1. **Check if it's already installed** — run `which <tool>` or `<tool> --version`. Don't assume something needs installing without checking.
2. **Briefly consider conflicts** — think about whether installing/upgrading would break something else in the live system (OpenClaw gateway, launchd services, running agents). This doesn't require deep research — just a quick mental check.

**Why:** Geoff has already installed many tools across projects (ngrok, brew packages, etc.). Redundant install suggestions waste time and could cause unintended upgrades.

**How to apply:** Before any `brew install`, `pip install` (for system tools), `npm install -g`, etc. in a suggestion — verify absence first. Flag known risks if they exist.

**Known installed tools (verified):**
- ngrok 3.37.2 (`/opt/homebrew/bin/ngrok`) — installed for Traveloceros, works for any project
