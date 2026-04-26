Parse $ARGUMENTS as one or more Discord channel bindings and wire them into the thread router.

Two accepted formats:
- Single: `name channel_id`
- Batch: `name: id, name: id, name: id, ...`

For each (name, channel_id) pair:

**Step 1 — Add to thread router config**

Read `~/.openclaw/workspace/projects/discord-thread-router/thread-router-config.json`. If `channel_id` is not already in `watchChannels`, add it. Also add a `sessionBases` entry mapping `channel_id` to `~/.openclaw/workspace/projects/<name>/threads`. Write the file back.

```bash
python3 -c "
import json, os
path = '/Users/moltyjoe/.openclaw/workspace/projects/discord-thread-router/thread-router-config.json'
with open(path) as f:
    cfg = json.load(f)
changed = False
if '<channel_id>' not in cfg['watchChannels']:
    cfg['watchChannels'].append('<channel_id>')
    changed = True
cfg.setdefault('sessionBases', {})
if '<channel_id>' not in cfg['sessionBases']:
    cfg['sessionBases']['<channel_id>'] = os.path.expanduser('~/.openclaw/workspace/projects/<name>/threads')
    changed = True
if changed:
    with open(path, 'w') as f:
        json.dump(cfg, f, indent=2)
        f.write('\n')
    print('added')
else:
    print('already present')
"
```

**Step 2 — Restart the router**

Restarting is safe — existing thread sessions run their own Discord plugin connection and are unaffected. The router only needs to be running for new thread provisioning.

Kill any running router process (the router runs as `bun thread-router.ts` in the `dist` tmux session, window 0 or named `router`):

```bash
# Kill the router window if it exists
tmux kill-window -t dist:router 2>/dev/null || true
```

Then restart:
```bash
cd ~/.openclaw/workspace/projects/discord-thread-router && ./start.sh
```

**After all pairs are processed**, report a table: name | channel_id | status (added/already present). Then tell the user: go to that Discord channel and create a new thread — the router will auto-provision a Claude Code session within a few seconds.

Note: the thread router provisions a new Claude session per thread automatically. No need to manually create state dirs or access.json — the router handles that.
