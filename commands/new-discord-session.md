Bind a Claude Code project directory to a Discord channel.

Parse $ARGUMENTS as: `name channel_id [cwd]`

- `name` — short label for this binding (used only in the report)
- `channel_id` — Discord channel ID to bind (any channel the bot has access to)
- `cwd` — project directory to bind (defaults to current working directory)

---

## Background — how the current system works

Channel IDs are specific to your Discord server setup. Any channel the bot has access to can be bound. A "new Discord session" means pointing a Claude Code session at one of those channels so Discord messages route to it.

There is **one shared Discord state dir**: `~/.claude/channels/discord/`. All Claude Code sessions use this dir — it holds the bot token (`.env`) and the access policy (`access.json`). There is no per-project state dir or thread-router. Channel routing happens via the `groups` object in `access.json`: each channel ID that appears there is a channel the bot listens to.

Prerequisite skills:
- `/discord:configure` — saves the bot token, checks token/access status
- `/discord:access` — approves pairings, edits allowlists, adds/removes groups, sets DM policy

---

**Step 1 — Add the channel to access.json**

Read `~/.claude/channels/discord/access.json`. Check if `channel_id` is already in `groups`. If not, add it:

```json
"<channel_id>": {
  "requireMention": false,
  "allowFrom": []
}
```

Write the updated file back (2-space indent, preserve all other keys). If the file doesn't exist, create it with defaults before adding the group.

Alternatively, run: `/discord:access group add <channel_id> --no-mention`

**Step 2 — Write project settings.json**

Create or update `<cwd>/.claude/settings.json` to set `DISCORD_STATE_DIR`:

```json
{
  "env": {
    "DISCORD_STATE_DIR": "~/.claude/channels/discord"
  }
}
```

If `settings.json` already exists, merge the `env` key — do not overwrite other settings. Note: this path is the same for every project; it points at the single shared state dir.

**Step 3 — Report**

Print a table: name | channel_id | state_dir | project_dir | status (group added / already present).

Tell the user: the binding is active for new sessions. Open a Claude Code session from `<cwd>` and messages in channel `<channel_id>` will route to it. No gateway restart needed — `access.json` is re-read on every inbound message.

---

**Finding your channel ID**

Enable Developer Mode in Discord (Settings → Advanced → Developer Mode), then right-click any channel → Copy Channel ID.
