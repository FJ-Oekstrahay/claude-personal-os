Manually override the session pressure level for **this session only**.

Usage: `/pressure <level>` where level is `normal`, `elevated`, or `high`.
`/pressure normal` clears the override and returns to automatic tracking.

Run this command now:

```bash
python3 -c "
import json, os, sys
from datetime import datetime, timezone

STATE_DIR = os.path.expanduser('~/.claude/hooks/state')
LEGACY = os.path.join(STATE_DIR, 'session-pressure.json')
level = '$ARGUMENTS'.strip().lower()

if level not in ('normal', 'elevated', 'high'):
    print('Usage: /pressure normal|elevated|high')
    sys.exit(1)

# Write THIS session's file. Claude Code exports the session id to every
# subprocess; without it we would be mutating the shared legacy file, which
# carries whichever session ticked last — that let an override leak into a
# concurrent peer, or vanish before the session that set it ever read it.
sid = os.environ.get('CLAUDE_CODE_SESSION_ID')
if not sid:
    print('CLAUDE_CODE_SESSION_ID not set — refusing to write a shared override.')
    print('Without a session id this would leak into whichever session ticked last.')
    sys.exit(1)

safe = ''.join(c for c in sid if c.isalnum() or c in '-_')
target = os.path.join(STATE_DIR, 'session-pressure-%s.json' % safe)

try:
    with open(target) as f:
        state = json.load(f)
except Exception:
    state = {}

state['session_id'] = sid
state['pressure'] = level
# 'normal' means: stop overriding, go back to automatic tracking.
state['manual_override'] = level != 'normal'
state['checkpoint_due'] = level in ('elevated', 'high')
state['last_updated'] = datetime.now(timezone.utc).isoformat()

os.makedirs(STATE_DIR, exist_ok=True)
blob = json.dumps(state, indent=2)
with open(target, 'w') as f:
    f.write(blob)
# Mirror to the legacy path for consumers that have not migrated yet.
with open(LEGACY, 'w') as f:
    f.write(blob)

if level == 'normal':
    print('Override cleared — back to automatic tracking.')
else:
    print('Pressure pinned to: %s (clear with /pressure normal)' % level)
# Print the target so a silent no-op is visible. This whole mechanism assumes
# CLAUDE_CODE_SESSION_ID equals the session_id Claude Code hands the PostToolUse
# hook. Verified true for a main interactive session; NOT verified for a tmux
# teammate or a subagent invoking /pressure, where session_id handling is known
# to differ by dispatch mode. If they ever diverge this writes a file no hook
# reads back — no error, just an override that does nothing. If an override
# appears not to take, compare this path against the session_id inside
# ~/.claude/hooks/state/session-pressure.json.
print('  wrote: %s' % target)
"
```

After running, all pressure-aware commands (batchc, mmguns, review-sequence) throttle accordingly
for the rest of the session, and the PostToolUse hook will not overwrite the setting while the
override is active. The override is scoped to this session — a peer running concurrently is
unaffected, and cannot clobber yours.
