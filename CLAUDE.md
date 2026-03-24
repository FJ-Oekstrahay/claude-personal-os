# Claude Code — Geoff's Environment

## Who I'm working with
Geoff Hoekstra (geoff.k.hoekstra@gmail.com). Hardware and firmware background. Fluent code reader — skip the "here's what I did" summaries. Do explain architectural choices, trade-offs, and side effects on the live system.

Communication: casual, direct. Call him Geoff. No emoji, no fluff.

## Workflow
Default to **plan mode** (Shift+Tab twice) for anything non-trivial. Geoff prefers understanding the plan before execution.

## The Two Systems
**Claude Code** = workshop (interactive dev, debugging, scripting — Geoff at the terminal).
**OpenClaw** = factory floor (autonomous agents, scheduled tasks, background ops).

Build and maintain OpenClaw with Claude Code. Don't use Claude Code to replace OpenClaw tasks. When a request would be better as an OpenClaw task, say so.

## Live System Warning
OpenClaw is running right now. The gateway (`openclaw-gateway`, port 18789) and agents are active. Never modify running configs without confirmation and a rollback plan.

Protected files — propose changes, don't write directly:
- `~/.openclaw/openclaw.json` (contains live tokens)
- `~/.openclaw/credentials/` (pairing JSONs)
- `~/.openclaw/secrets/` (bluebubbles.pass, imessage-bridge.env)
- `~/.openclaw/agents/*/agent/IDENTITY.md` (live agent prompts — production config)
- `~/Library/LaunchAgents/com.bluebubbles.server.plist` (BlueBubbles service)

Gateway is managed by launchd. Check status with: `launchctl list ai.openclaw.gateway`

## Key paths
- Claude Code reference: `~/.openclaw/CLAUDE-CODE-REFERENCE.md` — reference for slash commands, skills, session management, permissions. Update it whenever new patterns are established.
- OpenClaw root: `~/.openclaw/`
- Main workspace: `~/.openclaw/workspace/`
- Agent identities: `~/.openclaw/agents/{id}/agent/IDENTITY.md`
- Agent sessions: `~/.openclaw/agents/{id}/sessions/`
- gog CLI: `/opt/homebrew/bin/gog --account geoff.k.hoekstra@gmail.com`
- iMessage CLI: `~/.openclaw/bin/imsg`
- Governance: `~/.openclaw/workspace/GOVERNANCE.md`
- Project board: `~/.openclaw/workspace/projects/project-board/BOARD.md` — tracks all active/blocked/someday work across OpenClaw infra, dev projects, and family projects. Read it for context at session start. Update it when project status changes or on `/session-handoff`.

## OpenClaw Agent Roster
| ID | Name | Model | Role |
|---|---|---|---|
| moltyjoe | MoltyJoe | Sonnet 4.6 | Orchestrator — delegates only, no shell execution |
| bob | Bob | Haiku 4.5 | Developer — files + shell |
| gerbilcheeks | Gerbilcheeks | GPT-4.1-mini | Ops/research |
| bridgernelson | BridgerNelson | GPT-4.1-mini | Bridge tasks |
| moltyjoe-sec | MoltyJoe-Sec | GPT-4.1 | Security review |
| lumpy | Lumpy | Haiku 4.5 | Web search only |
| moltyjoe-casual | MoltyJoe-Casual | Sonnet 4.5 | Casual interface |
| moltyjoe-public | MoltyJoe-Public | Sonnet 4.5 | Public-facing, restricted |

## Session start
Run `/openclaw-status` at the beginning of each session to check gateway and agent state.

## Agent IDENTITY.md files
Committed to git but are **production config**. Changes take effect on agent restart. Treat them like live service config, not documentation. Do not edit them without a plan.

## ACP Sessions (Discord → Claude Code)
The `acpx` plugin (enabled 2026-03-19) lets MoltyJoe spawn Claude Code sessions from Discord threads. Key facts:
- Model is set per-session: `acpx claude set model claude-opus-4-6` (not in plugin config)
- Plugin config in `openclaw.json` → `plugins.entries.acpx.config`: `permissionMode: "approve-all"`, `nonInteractivePermissions: "deny"`, `timeoutSeconds: 300`, `cwd: ~/.openclaw/workspace`
- MoltyJoe should draft + confirm prompt with Geoff before spawning — that's the approval layer
- Gateway restart after plugin changes: `launchctl kickstart -k gui/$(id -u)/ai.openclaw.gateway` (user domain only, never `system/`)

## Known Gotchas
- BlueBubbles: use actual `chat.guid` from `chat.db`, not constructed GUIDs
- Auth: each agent needs its own `auth-profiles.json` — isolated sessions need separate credential files
- `maxfiles` was raised to 65536 to prevent gateway crashes
- Slack disabled (WebSocket pong timeouts — migrated to Discord)
- GPT-4.1-mini has hallucinated tool results in the past
- launchd plists need explicit env vars (`GOG_ACCOUNT`, `ANTHROPIC_API_KEY`)
- `group:runtime` deny-list can conflict with agent tool access
- `group:fs` deny on MoltyJoe-Public is intentional — don't add it back

## Lessons Learned

### Claude Code hooks
- PreToolUse hook exit codes: **exit 2 blocks**, exit 0 allows, anything else is non-blocking. exit 1 does NOT block.
- Block reason must go to **stderr** (`echo >&2`), not stdout. Claude only sees stderr when a hook blocks.
- Hook matcher covers tool *names* (`Write`, `Edit`, `Bash`). A matcher of `Write|Edit` misses all Bash-based writes (`cp`, `tee`, `>>`). Always include `Bash` if protecting file paths.
- Fail closed: if a hook can't parse its input (missing python3, bad JSON), exit 2, don't exit 0.
- `tool_input` is the correct key in the PreToolUse JSON payload (not `input`).

### Permissions
- `Bash(git *)` auto-approves destructive git ops (`push --force`, `reset --hard`, `clean`). Use explicit safe subcommands instead.
- Always add deny rules for `kill`, `pkill`, `killall` when a live process must be protected.

### Files before staging
- Read files before staging in git, even if they look safe. `identity/device.json` appeared to be a non-secret device ID but contained a plaintext private key.

### Skills that reference files/directories
- If a skill writes to a directory, either pre-create it or add `mkdir -p` to the skill. Directories don't create themselves.
- If a skill needs data from a secrets-containing file (e.g., openclaw.json), specify the exact `jq` path to extract — don't instruct reading the whole file. Tokens end up in context.

## Backlog
- [ ] Create `openclaw.json.example` sanitized template and commit it — no version history on master config until token migration
- [ ] Clarify `session-handoff` intent: `workspace/HANDOFF.md` is inside a gitignored dir — decide if it should live elsewhere or if that's fine
- [ ] `critic` skill: add explicit instruction not to offer to apply fixes
- [ ] `settings.json` `"model": "sonnet"` floats — pin to specific version if that matters
- [ ] `deploy-task` skill: reference `workspace/rewiring/old/DEPLOY_TASK.md` alongside GOVERNANCE.md
- [ ] Add `PostToolUse` audit hook — no execution trail currently
- [ ] Explore `.claude/commands/` project-level slash commands
- [ ] Token migration: move inline tokens out of openclaw.json into `secrets/tokens.env` (dedicated session)
- [ ] Resolve Gerbilcheeks model: CLAUDE.md says GPT-4.1-mini, bootstrap originally said switched to Haiku — verify current openclaw.json
