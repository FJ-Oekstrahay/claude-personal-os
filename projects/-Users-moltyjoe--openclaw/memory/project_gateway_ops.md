---
name: Gateway operational procedures
description: How to start, stop, restart, and check the OpenClaw gateway
type: project
---

Gateway is managed by openclaw CLI, not launchctl directly.

**Normal commands:**
- Restart: `openclaw gateway restart`
- Status: `openclaw gateway status` (also shows config issues)
- Check if running: `lsof -i :18789`
- Start via launchd (if not bootstrapped): `launchctl load ~/Library/LaunchAgents/ai.openclaw.gateway.plist`

**Do not use `launchctl unload/kickstart`** — the modern launchd domain API (`kickstart`, `bootout`, `bootstrap`) doesn't work reliably for this service. `launchctl load` is what Geoff uses.

**Resolved (2026-03-18):** `openclaw gateway install --force` was run — token removed from plist, plist regenerated at v2026.3.11. ThrottleInterval reset to 1 by reinstall (was bumped to 15, needs re-applying when stable).

**openclaw.json corruption (2026-03-18):** Line 14-15 had a literal newline inside the `browser.executablePath` string, splitting `/Applications/Brave Browser.app/Contents/MacOS/Brave Browser` across two lines. Caused JSON5 parse failure on gateway start. Fix: join the two lines. Likely caused Lumpy web search failures even after Brave API key update.

**Why:** Gateway not running = all agents down, Brave path corruption = CDP/browser tools broken.
**How to apply:** Always use `openclaw gateway restart` not launchctl. Check `openclaw gateway status` for config warnings before assuming the gateway is healthy.
