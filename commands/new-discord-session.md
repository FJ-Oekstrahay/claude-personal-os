Bind a Claude Code project directory to a Discord channel with full hook support.

Parse $ARGUMENTS as: `name channel_id channel_name log_channel_id log_channel_name log_webhook_url [cwd]`

- `name` — short slug (lowercase, no spaces) used in state dir name and webhook variable names. E.g. `myproject`
- `channel_id` — Discord channel ID for the conversation channel
- `channel_name` — Human-readable label for the conversation channel (matches actual Discord channel name). E.g. `my-project`
- `log_channel_id` — Discord channel ID for the log/activity channel
- `log_channel_name` — Human-readable label for the log channel (matches actual Discord channel name). E.g. `log-my-project`
- `log_webhook_url` — Webhook URL for the log channel (get from Discord: channel Settings → Integrations → Webhooks)
- `cwd` — project directory to bind (defaults to current working directory)

---

## What this does

Sets up a new Discord ↔ Claude Code binding. After running this, open a Claude Code session from `<cwd>` and messages in `channel_id` will route to it. Activity (tool calls, narrative text) will post to the log channel via webhook.

**The webhook is for the log channel only.** Conversation replies use the Discord bot API (token already configured globally).

---

## Step 1 — Derive variable name

The webhook conf variable name follows the pattern: `LOG_<NAME_UPPER>_WEBHOOK_URL`

Example: name=`myproject` → var=`LOG_MYPROJECT_WEBHOOK_URL`

---

## Step 2 — Add conversation channel to shared access.json

Read `~/.claude/channels/discord/access.json`. If `channel_id` is not already in `groups`, add:

```json
"<channel_id>": {
  "requireMention": false,
  "allowFrom": []
}
```

Write the updated file back (2-space indent, preserve all other keys).

---

## Step 3 — Create per-project state dir, copy bot token, write access.json

Create `~/.claude/channels/discord-<name>/` if it doesn't exist.

**Copy the bot token** — the Discord plugin reads its token from `<DISCORD_STATE_DIR>/.env` at startup. Per-project state dirs do NOT inherit this automatically:

```bash
cp ~/.claude/channels/discord/.env ~/.claude/channels/discord-<name>/.env
chmod 600 ~/.claude/channels/discord-<name>/.env
```

If this file is missing, the plugin starts silently with no MCP tools registered — `mcp__plugin_discord_discord__reply` will be unavailable and any Discord send attempt fails with "MCP failed."

Write `~/.claude/channels/discord-<name>/access.json` scoped to exactly this channel:

```json
{
  "dmPolicy": "allowlist",
  "allowFrom": [],
  "groups": {
    "<channel_id>": {
      "requireMention": false,
      "allowFrom": []
    }
  },
  "pending": {}
}
```

If the file already exists, check it has the right channel and update if needed.

---

## Step 4 — Update discord-channels.json

Read `~/.claude/hooks/discord-channels.json`. Add both channels using the provided names:

```json
"<channel_id>": "<channel_name>",
"<log_channel_id>": "<log_channel_name>"
```

If either ID is already present, leave it unchanged. Write back with 2-space indent.

---

## Step 5 — Update discord-routing.json

Read `~/.claude/hooks/discord-routing.json`. Add the routing entry:

```json
"<channel_id>": "LOG_<NAME_UPPER>_WEBHOOK_URL"
```

If `channel_id` is already present, update the value. Write back with 2-space indent.

---

## Step 6 — Update discord-log-channels.json

Read `~/.claude/hooks/discord-log-channels.json`. Add the mapping:

```json
"<channel_id>": "<log_channel_id>"
```

If `channel_id` is already present, update it. Write back with 2-space indent.

---

## Step 7 — Add webhook to discord-webhook.conf

Read `~/.claude/hooks/discord-webhook.conf`. Check if `LOG_<NAME_UPPER>_WEBHOOK_URL` is already present. If not, append:

```
LOG_<NAME_UPPER>_WEBHOOK_URL="<log_webhook_url>"
```

If it's present with a different URL, update it in-place.

---

## Step 8 — Write project settings.json

Create or update `<cwd>/.claude/settings.json`. Set:

```json
{
  "env": {
    "DISCORD_STATE_DIR": "~/.claude/channels/discord-<name>",
    "DISCORD_CHAT_ID": "<channel_id>"
  }
}
```

If `settings.json` already exists, merge into the `env` key — do not overwrite other settings.

---

## Step 9 — Update Known channel IDs table in this skill file

Read `~/.claude/commands/new-discord-session.md`. Find the "Known channel IDs" table at the bottom. Add two rows if not already present:

```
| <channel_name> | <channel_id> |
| <log_channel_name> | <log_channel_id> |
```

Write the file back. This keeps the reference table current so future debug sessions don't need to cross-reference JSON files. The table is the human-readable snapshot; `~/.claude/hooks/discord-channels.json` is the runtime source of truth.

---

## Step 10 — Report

Print a summary table:

| Field | Value |
|---|---|
| Name (slug) | `<name>` |
| Conversation channel | `<channel_id>` (`<channel_name>`) |
| Log channel | `<log_channel_id>` (`<log_channel_name>`) |
| Webhook var | `LOG_<NAME_UPPER>_WEBHOOK_URL` |
| State dir | `~/.claude/channels/discord-<name>/` |
| Project dir | `<cwd>` |
| Known channel IDs table | updated |
| Status | what was created vs already present |

Tell the user: open a Claude Code session from `<cwd>` and messages in `<channel_id>` will route to it. No gateway restart needed — `access.json` is re-read on every inbound message.

---

## Files touched summary

| File | What changes |
|---|---|
| `~/.claude/channels/discord/access.json` | `channel_id` added to groups |
| `~/.claude/channels/discord-<name>/.env` | bot token copied from discord/.env |
| `~/.claude/channels/discord-<name>/access.json` | created (scoped access) |
| `~/.claude/hooks/discord-channels.json` | two label entries added |
| `~/.claude/hooks/discord-routing.json` | channel → webhook var mapping |
| `~/.claude/hooks/discord-log-channels.json` | channel → log channel mapping |
| `~/.claude/hooks/discord-webhook.conf` | webhook URL variable added |
| `<cwd>/.claude/settings.json` | DISCORD_STATE_DIR + DISCORD_CHAT_ID set |
| `~/.claude/commands/new-discord-session.md` | Known channel IDs table updated |

---

## Known channel IDs

This table is updated automatically by Step 9 each time `/new-discord-session` runs. Runtime source of truth: `~/.claude/hooks/discord-channels.json`.

| Channel | ID |
|---|---|
| moltyjoe | <channel-id> |
| bob | <channel-id> |
| gerbilcheeks | <channel-id> |
| lumpy | <channel-id> |
| moltyjoe-sec | <channel-id> |
| bridgernelson | <channel-id> |
| moltyjoe-public | <channel-id> |
| moltyjoe-casual | <channel-id> |
| git-public-repo | <channel-id> |
| log-git-public-repo | <channel-id> |
| log | <channel-id> |
| droneteleo | <channel-id> |
| log-droneteleo | <channel-id> |
| prior-auth-bot | <channel-id> |
| publishing | <channel-id> |
| openclaw-config | <channel-id> |
| claude-config | <channel-id> |
| sales_automation | <channel-id> |
| log-sales-automation | <channel-id> |
| l3harris | <channel-id> |
| log-l3harris | <channel-id> |
| saic | <channel-id> |
| log-saic | <channel-id> |
| textron | <channel-id> |
| log-textron | <channel-id> |
| bambu | <channel-id> |
| log-bambu | <channel-id> |
