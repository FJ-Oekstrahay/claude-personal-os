Manually override the session pressure level in `~/.claude/hooks/state/session-pressure.json`.

Usage: `/pressure <level>` where level is `normal`, `elevated`, or `high`.

Run this command now:

```bash
python3 -c "
import json, os, sys
from datetime import datetime, timezone

STATE_FILE = os.path.expanduser('~/.claude/hooks/state/session-pressure.json')
level = '$ARGUMENTS'.strip().lower()

if level not in ('normal', 'elevated', 'high'):
    print('Usage: /pressure normal|elevated|high')
    sys.exit(1)

try:
    with open(STATE_FILE) as f:
        state = json.load(f)
except Exception:
    state = {}

state['pressure'] = level
state['manual_override'] = True
state['last_updated'] = datetime.now(timezone.utc).isoformat()
# checkpoint_due on elevated or high
state['checkpoint_due'] = level in ('elevated', 'high')

os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
with open(STATE_FILE, 'w') as f:
    json.dump(state, f, indent=2)

print(f'Pressure set to: {level}')
"
```

After running, all pressure-aware commands (batchc, mmguns, review-sequence) will throttle accordingly for the rest of the session. The PostToolUse hook will not overwrite the manual setting. Type `/pressure normal` to clear the override and return to automatic tracking.
