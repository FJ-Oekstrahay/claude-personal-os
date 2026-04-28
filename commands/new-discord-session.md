Bind a Claude Code project directory to a Discord channel.

Parse $ARGUMENTS as: `name channel_id [cwd]`

- `name` — short label used for the state dir (`discord-<name>`)
- `channel_id` — Discord channel ID to bind
- `cwd` — project directory to bind (defaults to current working directory)

---

**Step 1 — Create the state dir and access.json**

Check if `~/.claude/channels/discord-<name>/` exists. If not, create it and write `access.json`:

```json
{
  "dmPolicy": "allowlist",
  "allowFrom": ["<YOUR_USER_ID>"],
  "groups": {
    "<channel_id>": {
      "requireMention": false,
      "allowFrom": []
    }
  },
  "pending": {}
}
```

If the dir already exists, verify `<channel_id>` is present in `groups`. Add it if missing.

**Step 2 — Write project settings.json**

Create or update `<cwd>/.claude/settings.json` to set `DISCORD_STATE_DIR`:

```json
{
  "env": {
    "DISCORD_STATE_DIR": "~/.claude/channels/discord-<name>"
  }
}
```

If `settings.json` already exists, merge the `env` key — do not overwrite other settings.

**Step 3 — Report**

Print a table: name | channel_id | state_dir | project_dir | status (created/already present).

Tell the user: the binding is active for new sessions. Open a Claude Code session from `<cwd>` and messages in channel `<channel_id>` will route to it. No restart needed.

---

**How it works** (for reference):

The Discord plugin reads `DISCORD_STATE_DIR` at session start. The `access.json` inside that dir controls which channels and users the plugin accepts messages from. Each project gets its own state dir so channel routing is isolated per session. Bot token is shared globally from `~/.claude/channels/discord/.env`.
