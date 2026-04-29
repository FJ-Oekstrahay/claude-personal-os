# Hooks

Claude Code hooks are shell scripts that run at specific points in the execution lifecycle. **PreToolUse** hooks run before a tool call and can block it (exit 2) or allow it (exit 0). **PostToolUse** hooks run after a tool call completes and cannot block execution. **Notification** hooks fire when Claude needs user attention (e.g., waiting for approval).

| Hook file | Type | What it does | Portable? |
|---|---|---|---|
| `protect-sensitive-files.sh` | PreToolUse | Blocks writes to protected paths (openclaw.json, credentials/, secrets/, IDENTITY.md, launchd plists) | Partial (path list is system-specific; pattern is portable) |
| `discord-notify.sh` | PostToolUse + Notification | Posts Claude's narrative text and tool call summaries to a #logs webhook after each tool use; posts to #alerts and #logs when approval is needed | Yes (requires `discord-webhook.conf`) |

---

## protect-sensitive-files.sh

Blocks writes to a hardcoded list of sensitive paths: `openclaw.json`, `credentials/`, `secrets/`, any `IDENTITY.md` under `agents/`, and LaunchAgents plists. The matcher covers **Write, Edit, and Bash** — a `Write|Edit`-only matcher misses file writes that happen through shell commands (`cp`, `tee`, `>>`). The block reason is written to stderr (Claude only receives stderr when exit 2 fires). The hook **fails closed**: if python3 is unavailable or the JSON payload can't be parsed, it exits 2 and blocks. A broken hook that blocks everything is visible; a broken hook that silently allows everything is not.

## discord-notify.sh

Keeps you informed during long-running sessions without watching the terminal. Handles two hook types:

**PostToolUse** — After each tool call, the hook reads the session JSONL transcript (`~/.claude/projects/<encoded-path>/<session_id>.jsonl`) to find any Claude narrative text blocks written since the last check. Those are posted as `> quoted` lines to the LOGS webhook. Then a one-line tool call summary is posted (format varies by tool: Write, Edit, Bash, Read, mcp:\*, Agent, Task, etc.). State is tracked in `state/<session_id>.txt` as the last-read line number so each run only processes new content.

**Notification** — When Claude needs terminal input (approval requests, etc.), posts to both the ALERTS and LOGS webhooks so the alert is audible on mobile while the LOGS channel retains context.

Both sends are **backgrounded** (`curl` is forked and the hook exits immediately), keeping hook latency under 1ms. The hook safely no-ops if `discord-webhook.conf` is missing, so it won't break sessions on machines without Discord configured.

---

## Config

**`discord-webhook.conf`** (gitignored — copy from `discord-webhook.conf.example`):
- `LOGS_WEBHOOK_URL` — webhook for tool call summaries and narrative text
- `ALERTS_WEBHOOK_URL` — webhook for approval/notification alerts

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
