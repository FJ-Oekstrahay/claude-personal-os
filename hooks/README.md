# Hooks

Claude Code hooks are shell scripts that run at specific points in the execution lifecycle. **PreToolUse** hooks run before a tool call and can block it (exit 2) or allow it (exit 0). **PostToolUse** hooks run after a tool call completes and cannot block execution. **Notification** hooks fire when Claude needs user attention (e.g., waiting for approval).

| Hook file | Type | What it does | Portable? |
|---|---|---|---|
| `protect-sensitive-files.sh` | PreToolUse | Blocks writes to protected paths (openclaw.json, credentials/, secrets/, IDENTITY.md, launchd plists) | Partial (path list is system-specific; pattern is portable) |
| `discord-notify.sh` | PreToolUse + PostToolUse + Notification + Stop | Posts narrative text (pre-tool) and tool summaries (post-tool) to per-session log webhooks; posts to alerts and logs when approval is needed; posts turn-end notifications to the originating Discord channel when a turn completes. For Agent (subagent) calls, posts the subagent type, description, and the full prompt (capped at 1500 chars) so every dispatch is visible from Discord. For Skill calls, posts the skill name and args (if non-empty). Stop hook now also flushes trailing narrative text (after the last tool call) to the log webhook. Narrative truncation cap raised to 1700 chars. | Yes (requires `discord-webhook.conf`) |
| `discord-prompt-submit.py` | UserPromptSubmit | Detects incoming Discord messages, writes `state/<session_id>.chatid` for log routing, injects reminder to reply via Discord tool. Also detects `<command-name>` blocks (slash commands) and posts a one-liner to the log webhook on every prompt submission — no Discord tag required. | Yes (no config required) |
| `resource-pressure.py` | PostToolUse + SessionStart | Tracks context token fill pressure per session. Primary path reads token usage from the session JSONL and computes fill % against the 200k-token context window. Fallback counts tool calls. Writes `session-pressure.json` with fields: `pressure` (normal/elevated/high), `fill_pct`, `checkpoint_due`. Respects `manual_override` flag set by `/pressure` command. | Yes |
| `infra-health-check.sh` | SessionStart | Checks memsearch/Milvus health and index age. Always exits 0 — never blocks a session. Posts a Discord alert to the log channel if checks fail. | Partial (requires Discord bot token in `discord-webhook.conf`) |
| `discord-seed-chatid.sh` | SessionStart | Pre-seeds `state/<session_id>.chatid` from the `DISCORD_CHAT_ID` project env var at session start. Eliminates log routing failures on the first tool call of a session (before the first Discord message arrives). No-ops if `DISCORD_CHAT_ID` is unset or `.chatid` already exists. | Yes |

**`discord-stop-check.py`** is a helper script called by `discord-notify.sh` for the Stop event — not a hook itself. Handles two jobs: (1) flush assistant text produced after the last tool call (text-extractor only fires on tool events, so final-turn text is otherwise missed); (2) safety-net post if no Discord reply tool was used during the turn. Reads `DISCORD_BOT_TOKEN` from `discord-webhook.conf`.

**`discord-text-extract.py`** is a helper script called by `discord-notify.sh` — not a hook itself. It reads new assistant text blocks from the session JSONL and posts them as blockquotes before each tool summary. It accepts three arguments: `session_id`, `transcript_path`, `logs_webhook_url`. State is tracked in `state/<session_id>.txt` (last-read line number) and `state/<session_id>.chatid` (active Discord source channel for log routing). Note: `.chatid` is now written by BOTH `discord-prompt-submit.py` (on UserPromptSubmit, eliminating routing lag) and `discord-text-extract.py` (as a fallback on each tool call).

---

## protect-sensitive-files.sh

Blocks writes to a hardcoded list of sensitive paths: `openclaw.json`, `credentials/`, `secrets/`, any `IDENTITY.md` under `agents/`, and LaunchAgents plists. The matcher covers **Write, Edit, and Bash** — a `Write|Edit`-only matcher misses file writes that happen through shell commands (`cp`, `tee`, `>>`). The block reason is written to stderr (Claude only receives stderr when exit 2 fires). The hook **fails closed**: if python3 is unavailable or the JSON payload can't be parsed, it exits 2 and blocks. A broken hook that blocks everything is visible; a broken hook that silently allows everything is not.

## discord-notify.sh

Keeps you informed during long-running sessions without watching the terminal. Handles two hook types:

**PostToolUse** — After each tool call, the hook reads the session JSONL transcript (`~/.claude/projects/<encoded-path>/<session_id>.jsonl`) to find any Claude narrative text blocks written since the last check. Those are posted as `> quoted` lines to the LOGS webhook. Then a one-line tool call summary is posted (format varies by tool: Write, Edit, Bash, Read, mcp:\*, Agent, Task, etc.). State is tracked in `state/<session_id>.txt` as the last-read line number so each run only processes new content.

**Subagent call telemetry:** For `Agent` tool calls, the summary includes the `subagent_type`, the description, and the prompt text (capped at ~1500 chars with `…` truncation). Format:
```
**Agent** → `<subagent_type>` — <description>
```<prompt body>```
```
This makes every subagent dispatch — Cob, Gadfly, CTO, Seymour, etc. — visible from Discord without watching the terminal.

**Notification** — When Claude needs terminal input (approval requests, etc.), posts to both the ALERTS and LOGS webhooks so the alert is audible on mobile while the LOGS channel retains context. Note: `ALERTS_WEBHOOK_URL` is optional — the @mention to the per-session log webhook fires regardless.

**Stop** — When a Claude Code turn ends, if a Discord message arrived during the turn but no reply was sent via the Discord plugin, the hook posts the assistant's last text to the originating Discord channel using the bot API (requires `DISCORD_BOT_TOKEN` in conf). If the last text contains a question (ends with `?` or contains question phrases), the post includes an @mention. All stop-hook posts are prefixed with `[turn done]` to distinguish them from live replies.

Both sends are **backgrounded** (`curl` is forked and the hook exits immediately), keeping hook latency under 1ms. The hook safely no-ops if `discord-webhook.conf` is missing, so it won't break sessions on machines without Discord configured.

**Per-channel log routing** — When a session originates from a Discord channel listed in `discord-routing.json`, log messages are sent to that channel's dedicated log webhook instead of the default LOGS webhook. The active channel is detected from the session transcript by `discord-text-extract.py` and persisted in `state/<session_id>.chatid`. Channels not in the routing map fall back to `LOGS_WEBHOOK_URL`.

---

## Config

**`discord-webhook.conf`** (gitignored — copy from `discord-webhook.conf.example`):
- `LOGS_WEBHOOK_URL` — default webhook for tool call summaries and narrative text
- `ALERTS_WEBHOOK_URL` — webhook for approval/notification alerts
- `LOG_CLAUDE_CONFIG_WEBHOOK_URL`, `LOG_DRONETELEO_WEBHOOK_URL`, `LOG_PUBLISHING_WEBHOOK_URL`, `LOG_GIT_PUBLIC_REPO_WEBHOOK_URL` — per-channel log webhooks (optional; fall back to `LOGS_WEBHOOK_URL` if unset)
- `DISCORD_BOT_TOKEN` — Discord bot token; required for the Stop hook to post turn-end notifications to the originating Discord channel
- `DISCORD_ALERT_USER_ID` — Discord user ID to @mention in alert messages (optional)

**`discord-routing.json`** — maps source Discord channel IDs to log webhook variable names (defined in `discord-webhook.conf`). Channels absent from this map fall back to `LOGS_WEBHOOK_URL`. Extend this file to add new channel→log mappings.

**`discord-channels.json`** — maps Discord channel IDs to agent names. Used by `discord-notify.sh` to label which agent a notification comes from when the hook fires inside an agent-spawned session.

**`state/<session_id>.txt`** — one file per session, contains the last-read JSONL line number. Created automatically; safe to delete (resets to line 0, may re-post old content once).

To create webhooks: Discord Server Settings → Integrations → Webhooks → New Webhook. Set the target channel, copy the URL, paste into `discord-webhook.conf`.

---

## Gotchas

- **Exit codes**: exit 2 blocks (PreToolUse only), exit 0 allows, exit 1 is non-blocking. Only exit 2 stops the tool call.
- **Stderr vs stdout**: Claude only sees stderr when a hook exits 2. Block reasons must go to stderr.
- **Matcher scope**: A matcher of `Write|Edit` misses Bash-based writes. Always include `Bash` when protecting file paths.
- **Fail closed**: if a hook can't parse its input, exit 2. Don't silently exit 0.
- **`tool_input`**: the correct key in the PreToolUse JSON payload (not `input`).

Full lessons from hook development are in [`../CLAUDE.md`](../CLAUDE.md) under "Lessons Learned → Claude Code hooks".
