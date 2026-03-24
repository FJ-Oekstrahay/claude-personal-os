---
name: Claude Code bootstrap completed
description: Bootstrap of Claude Code global config for the OpenClaw project — what was set up
type: project
---

Bootstrap completed 2026-03-16. Set up Claude Code global config for Geoff's OpenClaw environment.

**Why:** Clean slate — no CLAUDE.md, settings, hooks, skills, or MCP servers existed before this session.

**What was created:**
- `~/.claude/CLAUDE.md` — global env context, agent roster, known gotchas
- `~/.claude/settings.json` — permissions (allow: git/ps/lsof/which/node/npm/top; deny: rm -rf/sudo/launchctl load/unload) + PreToolUse hook for sensitive file protection + macOS Notification hook
- `~/.claude/hooks/protect-sensitive-files.sh` — blocks writes to openclaw.json, credentials/, secrets/, auth-profiles, .env, LaunchAgents plists, agent IDENTITY.md files
- `~/.claude/skills/`: openclaw-status, debug-agent, deploy-task, session-handoff, critic, compact-checkpoint
- `~/.openclaw/CLAUDE.md` — project-level context, token migration TODO
- `~/.openclaw/workspace/CLAUDE.md` — workspace context pointing to AGENTS.md + GOVERNANCE.md
- `~/.openclaw/.gitignore` — excludes openclaw.json, credentials, secrets, workspace subdirs (each has own repo), browser, sessions, runtime state
- `~/.openclaw/` git repo initialized, initial commit (21 files: .gitignore, CLAUDE.md, agent IDENTITY.md files, bin scripts, completions, imsg-send skill)
- `sequential-thinking` MCP server added to local config

**How to apply:** Reference when continuing openclaw work — config is in place, don't recreate it.

**One deviation from plan:** `identity/device.json` was added to gitignore (contains a private key) — it was NOT committed despite the plan listing it as safe.
