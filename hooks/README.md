# Hooks

Claude Code hooks are shell scripts that run at specific points in the execution lifecycle. **PreToolUse** hooks run before a tool call and can block it (exit 2) or allow it (exit 0). **PostToolUse** hooks run after a tool call completes and cannot block execution. **Notification** hooks fire when Claude needs user attention (e.g., waiting for approval).

| Hook file | Type | What it does | Portable? |
|---|---|---|---|
| `protect-sensitive-files.sh` | PreToolUse | Blocks writes to protected paths (openclaw.json, credentials/, secrets/, IDENTITY.md, launchd plists) | Partial (path list is system-specific; pattern is portable) |
| `discord-notify.sh` | PostToolUse + Notification | Posts tool mutation summaries to a #logs webhook; posts approval-needed alerts to an #alerts webhook | Yes (requires `discord-webhook.conf`) |
| `discord-webhook.conf.example` | Config template | Copy to `discord-webhook.conf` (gitignored) and fill in your webhook URLs | Yes |

---

## protect-sensitive-files.sh

The critical design detail here is that the tool matcher covers **Bash in addition to Write and Edit**. A `Write|Edit`-only matcher misses file writes that happen through shell commands (`cp`, `tee`, `>>`). Since protected files can be overwritten via any of these paths, all three must be covered.

The hook also **fails closed**: if python3 is unavailable or the JSON payload can't be parsed, it exits 2 and blocks the operation. A broken hook that blocks everything is visible; a broken hook that silently protects nothing is invisible and dangerous.

## discord-notify.sh

Both sends are **backgrounded** — the hook forks `curl` and exits immediately. This keeps hook latency under 1ms and has zero impact on Claude's response time. The hook safely no-ops if `discord-webhook.conf` is missing, so it won't break the session on a machine without Discord configured.

To set up: copy `discord-webhook.conf.example` to `~/.claude/hooks/discord-webhook.conf`, fill in two Discord webhook URLs (one for logs, one for alerts). Create webhooks via Discord: Server Settings → Integrations → Webhooks → New Webhook.

---

## Hook lessons

Exit codes, matcher scope, and fail-closed design are documented in detail in [`LESSONS.md`](../LESSONS.md).
