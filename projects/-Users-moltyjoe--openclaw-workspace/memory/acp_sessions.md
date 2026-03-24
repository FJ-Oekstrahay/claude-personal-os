---
name: ACP Sessions (Discord → Claude Code)
description: How acpx plugin enables MoltyJoe to spawn Claude Code sessions from Discord threads, and how to control model
type: project
---

The `acpx` plugin was enabled 2026-03-19. It allows MoltyJoe (Sonnet orchestrator) to spawn full Claude Code instances bound to Discord threads.

**Claude Code ↔ Geoff Discord channel:** `#claudo-main`, channel ID `1484980384860078286`. This is where Geoff and Claude Code sessions communicate directly — distinct from MoltyJoe's agent channel (1482080556089868451).

**Flow:** Geoff tells MoltyJoe → MoltyJoe drafts prompt → confirms with Geoff → spawns ACP session → Claude Code runs in thread.

**Model control:** Not in plugin config. Set per-session via `acpx claude set model <id>` or `--model <id>` flag at spawn time. Model IDs: `claude-opus-4-6`, `claude-sonnet-4-6`, `claude-haiku-4-5-20251001`.

**Plugin config** (`openclaw.json` → `plugins.entries.acpx.config`):
- `permissionMode: "approve-all"` — all ops auto-approved (no interactive prompts in Discord)
- `nonInteractivePermissions: "deny"` — skips gracefully rather than hard-erroring
- `timeoutSeconds: 300` — 5 min per turn, prevents runaway billing
- `cwd: "/Users/moltyjoe/.openclaw/workspace"` — sessions start here

**Why:** MoltyJoe is the approval layer — it drafts and confirms prompts before spawning, compensating for `approve-all` running headless.

**Gateway restart command:** `launchctl kickstart -k gui/$(id -u)/ai.openclaw.gateway` — always user domain, never `system/`.
