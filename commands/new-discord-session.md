Parse $ARGUMENTS as one or more Discord channel bindings and set up a project directory for each.

Two accepted formats:
- Single: `name channel_id`
- Batch: `name: id, name: id, name: id, ...`

For each (name, channel_id) pair, execute the following via Bash:

**Step 1 — Create dirs**
```
mkdir -p ~/.openclaw/workspace/projects/<name>/.claude
mkdir -p ~/.claude/channels/discord-<name>
```

**Step 2 — Merge DISCORD_STATE_DIR into settings.json**

If `~/.openclaw/workspace/projects/<name>/.claude/settings.json` exists, read it and set `env.DISCORD_STATE_DIR` without touching other keys. If it doesn't exist, create it fresh. Use this Python snippet:

```bash
python3 -c "
import json, os, sys
path = os.path.expanduser('~/.openclaw/workspace/projects/<name>/.claude/settings.json')
d = {}
if os.path.exists(path):
    with open(path) as f:
        d = json.load(f)
d.setdefault('env', {})['DISCORD_STATE_DIR'] = '/Users/moltyjoe/.claude/channels/discord-<name>'
with open(path, 'w') as f:
    json.dump(d, f, indent=2)
    f.write('\n')
"
```

**Step 3 — Copy bot token**

Copy the token file so the plugin can authenticate:
```bash
cp ~/.claude/channels/discord/.env ~/.claude/channels/discord-<name>/.env
chmod 600 ~/.claude/channels/discord-<name>/.env
```

**Step 4 — Write access.json**

Write `~/.claude/channels/discord-<name>/access.json`. If file already exists, overwrite it (channel binding is the authoritative config for this dir):

```json
{
  "dmPolicy": "allowlist",
  "allowFrom": ["1015620939611910254"],
  "groups": {
    "<channel_id>": {
      "requireMention": false,
      "allowFrom": []
    }
  },
  "pending": {}
}
```

**After all pairs are processed**, report a table: name | project path | state dir | created or updated.

Note: the Discord plugin reads DISCORD_STATE_DIR at startup. The binding takes effect when the project is opened in a new Claude Code session, not in the current one.
