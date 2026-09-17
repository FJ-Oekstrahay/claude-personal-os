# hooks/

Claude Code hooks intercept lifecycle events (session start, tool calls, prompt submission, session
stop) and receive event data as JSON on stdin. They talk back to the harness two ways: stdout is
injected into the model's context, and the exit code decides whether the triggering action is
allowed (0) or blocked (2). The event/matcher wiring for the hooks below lives in
`../settings.example.json`. Three files here are not top-level hooks: `discord-text-extract.py` and `discord-stop-check.py`
are called directly by `discord-notify.sh`, and `discord_outbound.py` is the helper module all three
import.

| File | Event / matcher | What it does |
|---|---|---|
| `anthropic-key-tripwire.sh` | SessionStart | Warns on stdout (never blocks) if a bare `ANTHROPIC_API_KEY` is present in the session environment. A stale key can silently take auth precedence over a Claude subscription and start metered billing. |
| `audit-trail.py` | PostToolUse (`.*`) | Appends one JSONL line per tool call, with the tool name and the first 120 characters of its input, to a per-day log file. |
| `batchc-nudge.py` | UserPromptSubmit | Scores the submitted prompt on cheap string signals only (length, distinct imperative verbs, list depth) and prints one line suggesting the batchc protocol above a threshold. No LLM call, no blocking. |
| `batchc-stop-gate.py` | Stop | Blocks the stop (exit 2) when a substantial batch of work, measured by cumulative tool-call count or context tokens used, ends with no handoff file containing a "Lessons Captured" section, and separately when more than one file (or a live shared surface such as a hook or command) was edited with no independent review detected. See note below. |
| `discord-keyword-dispatch.py` | UserPromptSubmit | Detects a bare keyword (`batchc`, `orchcheck`, `longrun`, etc., including dictation-friendly variants) typed in a Discord message and injects context telling Claude to load and run the matching command file, so slash-commands work without typing `/`. |
| `discord-notify.sh` | PreToolUse (`.*`), PostToolUse (`.*`), Stop, SubagentStop, Notification | Posts activity to Discord webhooks: pre-tool narrative flush, post-tool play-by-play, and approval alerts. Routes tool play-by-play and narrative firehose to a per-project log channel, and reply/done-ping content to the discussion channel, never both. |
| `discord_outbound.py` | imported by the three hooks above | Shared helper: bounded-retry POST, a time-windowed dedup guard, a per-channel coalescing buffer flushed at Stop, and an append-only outbound audit log. Fails open by design so a lost Discord post never crashes a hook. |
| `discord-stop-check.py` | called by `discord-notify.sh` (Stop) | Posts assistant text produced after the last tool call, and acts as a safety net if the reply tool was never used this turn. Uses a per-session file lock and content-hash dedup to avoid re-posting on repeated Stop fires. |
| `discord-text-extract.py` | called by `discord-notify.sh` | Reads new assistant text out of the session transcript under a per-agent cursor and posts it to the log channel as a firehose. |
| `discord-webhook.conf.example` | n/a, configuration template | Template for the webhook URLs, bot token, per-channel log routing, and alert-mention user ID that the Discord hooks read from `discord-webhook.conf` (gitignored). |
| `handoff-timestamp-guard.sh` | PreToolUse (`Write\|Edit\|Bash`) | Blocks any Write/Edit/Bash that would put a handoff filename with a literal, typed-in date on disk. The sanctioned flow generates the timestamp from the shell, so it passes through untouched. |
| `memory-anti-ratchet.py` | SessionStart, project-scoped, see note below | Parses `Belief metadata` blocks out of a project's auto-memory files, computes staleness and self-challenge counts, and emits a challenge notice so a belief that gets re-injected every session doesn't go indefinitely unexamined. |
| `protect-sensitive-files.sh` | PreToolUse (`Write\|Edit\|Bash`) | Blocks writes matching protected path patterns (`/credentials/`, `/secrets/`, `.env`, etc.) and scans Write/Edit content and Bash command strings for embedded tokens (bot tokens, webhook URLs, API keys), with a carved-out exception for the designated `discord-webhook.conf` token store. |
| `resource-pressure.py` | SessionStart (`--reset`), PostToolUse (`.*`) | Tracks per-session context-fill percentage against the model's actual context window, resolved from the model id rather than a fixed guess, with a tool-call-counting fallback when no token-usage data is available. Read by `/pressure`, `/memory-health`, and `batchc-stop-gate.py`. |
| `wave-counter.py` | PostToolUse (`.*`) | Appends one `{ts, tool}` line to a rolling 60-second log, read by `resource-pressure.py` to compute tool-call density. Append-only so concurrent subagent tool calls can't clobber each other. |

## Notes

- **`memory-anti-ratchet.py` runs as a project-scoped `SessionStart` hook**, registered in a
  project's own `.claude/settings.json` rather than in the global one; it does not appear in
  `../settings.example.json`. The `MEMORY_DIR` path in this copy is a placeholder
  (`~/.claude/projects/<project-slug>/memory`); a real deployment points it at that project's actual
  auto-memory directory.
- **`batchc-stop-gate.py` fails open by design.** Its own docstring: "Fail-OPEN on any error or
  missing signal... failing closed on a parse bug would wedge EVERY session in an un-stoppable loop.
  So the safe failure here is to allow the stop. Loud-but-stoppable beats wedged." This deliberately
  inverts the fail-closed convention the PreToolUse protection hooks above use, because those hooks
  guard a resource (safe to block on doubt) while this one gates a stop (blocking on doubt wedges the
  session).
- **The Discord hooks require `discord-webhook.conf`.** Copy `discord-webhook.conf.example` to
  `discord-webhook.conf` (gitignored) and fill in webhook URLs and a bot token before
  `discord-notify.sh`, `discord-stop-check.py`, or `discord-text-extract.py` will do anything.
  `discord-keyword-dispatch.py` does not read the config; it only checks whether the prompt carries a
  Discord channel tag.
