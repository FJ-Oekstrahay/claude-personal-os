# Hooks

Claude Code hooks are shell scripts that run at specific points in the execution lifecycle. **PreToolUse** hooks run before a tool call and can block it (exit 2) or allow it (exit 0). **PostToolUse** hooks run after a tool call completes and cannot block execution. **Notification** hooks fire when Claude needs user attention (e.g., waiting for approval). Anthropic also added a **SubagentStop** hook (mid-2026) that fires per-subagent when a subagent session ends — not yet wired here, but worth noting if you're building per-agent telemetry.

| Hook file | Type | What it does | Portable? |
|---|---|---|---|
| `protect-sensitive-files.sh` | PreToolUse | Blocks writes to protected paths (openclaw.json, credentials/, secrets/, IDENTITY.md, launchd plists) | Partial (path list is system-specific; pattern is portable) |
| `discord-notify.sh` | PreToolUse + PostToolUse + Notification + Stop | Posts narrative text (pre-tool) and tool summaries (post-tool) to per-session log webhooks; posts to alerts and logs when approval is needed; posts turn-end notifications to the originating Discord channel when a turn completes. For Agent (subagent) calls, posts the subagent type, description, and the full prompt (capped at 1500 chars) so every dispatch is visible from Discord. For Skill calls, posts the skill name and args (if non-empty). Stop hook now also flushes trailing narrative text (after the last tool call) to the log webhook. Narrative truncation cap raised to 1700 chars. | Yes (requires `discord-webhook.conf`) |
| `discord-prompt-submit.py` | UserPromptSubmit | Detects incoming Discord messages, writes `state/<session_id>.chatid` for log routing, injects reminder to reply via Discord tool. Also detects `<command-name>` blocks (slash commands) and posts a one-liner to the log webhook on every prompt submission — no Discord tag required. | Yes (no config required) |
| `resource-pressure.py` | PostToolUse + SessionStart | Tracks context token fill pressure per session. Primary path reads token usage from the session JSONL and computes fill % against the 200k-token context window. Fallback counts tool calls. Writes `session-pressure.json` with fields: `pressure` (normal/elevated/high), `fill_pct`, `checkpoint_due`. Respects `manual_override` flag set by `/pressure` command. | Yes |
| `infra-health-check.sh` | SessionStart | Checks memsearch/Milvus health and index age. Always exits 0 — never blocks a session. Posts a Discord alert to the log channel if checks fail. | Partial (requires Discord bot token in `discord-webhook.conf`) |
| `discord-seed-chatid.sh` | SessionStart | Pre-seeds `state/<session_id>.chatid` from the `DISCORD_CHAT_ID` project env var at session start. Eliminates log routing failures on the first tool call of a session (before the first Discord message arrives). No-ops if `DISCORD_CHAT_ID` is unset or `.chatid` already exists. | Yes |
| `batchc-nudge.py` | UserPromptSubmit | Scores the incoming prompt for multi-step-work signals (length, imperative verbs, list structure, keywords) and prints a suggestion to run the `batchc` protocol when it looks like a batch. Never blocks. | Yes (protocol-agnostic; references `batchc`) |
| `wave-counter.py` | PostToolUse | Appends each tool call to a rolling 60-second log so `resource-pressure.py` can compute `wave_density` — the tool-call burst rate used as a throttle-risk signal during batch dispatch. | Yes |
| `audit-trail.py` | PostToolUse | Appends one JSONL record per tool call to a daily audit log (`state/audit-<date>.jsonl`) — a forensic trail of every tool the session invoked. Never blocks. | Yes |
| `batchc-stop-gate.py` | Stop | Enforces the batch protocol's completion rules. Scans the session transcript at stop time; if a substantial batch edited more than one file with no subsequent `/verify` or `/code-review`, or finished without a written handoff, it blocks the stop (exit 2) and injects the missing-step checklist to stderr. Fires at most once per session. | Yes (references `batchc` protocol) |

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

## resource-pressure.py

Tracks how full the context window is during a session and exposes a pressure level (`normal` / `elevated` / `high`) that rate-limit-aware commands can read.

**Primary path** — reads token usage from `~/.claude/projects/<encoded-path>/<session_id>.jsonl` and computes fill percentage against the 200,000-token context window. Sets `elevated` at ≥50% fill, `high` at ≥75%.

**Fallback** — if the JSONL isn't found or has no usage data, falls back to counting tool calls (Agent/Task count double). Sets `elevated` at ≥25 calls, `high` at ≥40.

State is written to `~/.claude/hooks/state/session-pressure.json`. The `/pressure` command sets `manual_override: true` to prevent this hook from overwriting a manual setting. The SessionStart invocation (with `--reset`) clears state and starts fresh.

## infra-health-check.sh

Runs at session start to verify that background infrastructure (memsearch, Milvus) is healthy and the search index is reasonably fresh. Always exits 0 — failure here should never block a session, only alert. Posts to the Discord log channel via bot API if a check fails.

## discord-seed-chatid.sh

Solves an edge case in per-channel log routing: if a session is opened from a Discord channel (with `DISCORD_CHAT_ID` set in the project env), but the first thing Claude does is a tool call before any Discord message arrives, the `.chatid` file doesn't exist yet and routing falls back to the default `LOGS_WEBHOOK_URL`. This hook writes the file at session start so the first tool call routes correctly. Guards: only writes if `DISCORD_CHAT_ID` is set, only writes if the file doesn't already exist (the `UserPromptSubmit` hook owns runtime updates).

---

## Protocol enforcement and telemetry

These hooks exist because a protocol written into a command file is a request, not a guarantee — the model can forget it under context pressure. Moving the enforcement into hooks makes the constraint hold regardless of what the model remembers.

## batchc-stop-gate.py

A `Stop` hook that gates session completion on the batch protocol's own rules. When a turn ends, it scans the session transcript for the work that was done. If a substantial batch edited **more than one file** with no subsequent `/verify` or `/code-review` call (the independent generator→critic gate), or finished without a written handoff, it exits 2 to block the stop and writes the missing-step checklist to stderr so the model sees exactly what's outstanding. A one-shot marker ensures it fires at most once per session, so it nudges rather than traps. This is the enforcement backstop for the rule that the agent which wrote the code does not get to be the one that declares it correct.

## wave-counter.py + resource-pressure.py

Together these turn batch dispatch into a closed loop. `resource-pressure.py` reads token usage from the session JSONL and computes context fill against the 200k window (`normal` / `elevated` / `high`); `wave-counter.py` logs every tool call to a rolling 60-second window from which `wave_density` (burst rate) is derived. The batch protocol reads both before each wave: it shrinks wave size as the context fills and pauses dispatch when the burst rate signals an impending rate-limit throttle — adapting before the limit is hit, not after.

## batchc-nudge.py

A `UserPromptSubmit` hook that scores the incoming prompt for multi-step-work signals — length, imperative verbs, list structure, batch keywords — and suggests running the batch protocol when the prompt looks like one. It only prints a suggestion; it never blocks or rewrites the prompt.

## audit-trail.py

A `PostToolUse` hook that appends one JSONL record per tool call to a daily audit log. Cheap, non-blocking, and independent of the Discord stream — a durable forensic trail of what every session actually did.

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

---

## Discord outbound routing policy (2026-07-03)

### Two destinations, never both

Every session-activity post goes to exactly one of two Discord destinations, and
**nothing posts verbatim to both**:

| Destination | What lands here | Producer |
|---|---|---|
| **Discussion channel** (the source channel the user talks in) | the reply-tool message; final answers; questions for the user; the `@you done` ping; Job 1/Job 2 safety-net text **only when Claude did not use the reply tool** | reply tool itself + `discord-stop-check.py` |
| **Log channel** (per-project firehose, mapped in `discord-routing.json` / `discord-log-channels.json`) | tool play-by-play summary lines; narrative-text firehose; post-reply trailing narrative | `discord-notify.sh` + `discord-text-extract.py` |

The reply-tool message **is** the discussion-channel post. `discord-stop-check.py`
does not re-post it. Trailing narrative that appears *after* the reply tool call
is routed to the **log** channel (it is not the reply body), so the discussion
channel never receives a duplicate.

### Three cross-cutting guarantees (all in `discord_outbound.py`)

1. **Dedup guard** — identical `(session, channel, content)` posted within
   `DISCORD_DEDUP_WINDOW` seconds (default 20) is suppressed. Time-windowed so
   legitimately-identical posts in different turns still fire. The done-ping and
   the turn-done post dedup on a turn-scoped key so a genuine next-turn ping is
   never swallowed. This is the safety net that makes the "same message 4×" bug
   structurally impossible regardless of how many times Stop fires.
2. **Coalescing** — log-channel lines are buffered per `(session, channel)` and
   flushed as one POST when the buffer is >2s old, >1600 chars, or force-flushed
   at Stop. Cuts POST volume (Discord webhook budget ≈ 5 posts / 2s → 429s).
   Disable with `DISCORD_COALESCE=0`.
3. **Outbound audit** — every POST attempt writes one JSON line to
   `state/outbound-audit.log`: `{ts, session, event, channel, target, status
   (sent|dedup|dropped|buffered), http, hash, text[:60]}`. Rotated past 5 MB.
   This is the forensic trail for any future "why did/didn't X post" question.

### Never-block invariant

All of the above runs in processes the shell hook already backgrounded. The hook
itself always exits 0 immediately; nothing here adds latency to a tool call.

### Test / debug env vars

- `DISCORD_HOOK_STATE_DIR` — override the state dir (used by the offline harness).
- `DISCORD_DRYRUN=1` — write intended POSTs to `$DISCORD_DRYRUN_FILE` instead of curling.
- `DISCORD_COALESCE=0` — post each log line immediately (no buffering).
- `DISCORD_DEDUP_WINDOW=<secs>` — dedup window (default 20).
