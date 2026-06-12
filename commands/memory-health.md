Check the health of each memory tier and report a compact status table.

Run this command now:

```bash
python3 - << 'PYEOF'
import os, json, glob, subprocess
from datetime import datetime, timezone

now = datetime.now(timezone.utc)

def age_str(path):
    try:
        mtime = os.path.getmtime(path)
        secs = now.timestamp() - mtime
        if secs < 3600:
            return f"{int(secs//60)}m ago"
        if secs < 86400:
            return f"{int(secs//3600)}h ago"
        return f"{int(secs//86400)}d ago"
    except Exception:
        return "unknown"

def newest_in_dir(d, pattern="*.md"):
    files = glob.glob(os.path.join(d, pattern))
    if not files:
        return None
    return max(files, key=os.path.getmtime)

rows = []
fixes = []

# --- Tier 1: auto-memory (MEMORY.md + agent-memory dir) ---
mem_index = os.path.expanduser("~/.claude/projects/-Users-moltyjoe--openclaw-workspace-projects-claude-config/memory/MEMORY.md")
mem_dir = os.path.dirname(mem_index)
if os.path.exists(mem_index):
    newest = newest_in_dir(mem_dir)
    age = age_str(newest) if newest else "no files"
    rows.append(("auto-memory", "OK", f"index exists, newest file {age}"))
else:
    rows.append(("auto-memory", "BROKEN", "MEMORY.md not found"))
    fixes.append("auto-memory: check ~/.claude/projects/.../memory/ path")

# --- Tier 2: memsearch ---
memsearch_dirs = [
    os.path.expanduser("~/.memsearch/memory"),
    os.path.expanduser("~/.openclaw/.memsearch/memory"),
]
found_dir = next((d for d in memsearch_dirs if os.path.isdir(d)), None)
if found_dir:
    newest = newest_in_dir(found_dir)
    if newest:
        age_secs = now.timestamp() - os.path.getmtime(newest)
        age = age_str(newest)
        status = "STALE" if age_secs > 7 * 86400 else "OK"
        rows.append(("memsearch", status, f"dir={os.path.basename(found_dir)}, newest {age}"))
        if status == "STALE":
            fixes.append("memsearch: newest indexed file is >7d old — check indexer cron")
    else:
        rows.append(("memsearch", "BROKEN", f"dir exists but no .md files"))
        fixes.append("memsearch: run indexer manually to populate memory dir")
else:
    rows.append(("memsearch", "BROKEN", "no memory dir found"))
    fixes.append("memsearch: install/configure memsearch plugin and run indexer")

# --- Tier 3: session-pressure state file ---
pressure_file = os.path.expanduser("~/.claude/hooks/state/session-pressure.json")
if os.path.exists(pressure_file):
    age_secs = now.timestamp() - os.path.getmtime(pressure_file)
    age = age_str(pressure_file)
    try:
        with open(pressure_file) as f:
            state = json.load(f)
        level = state.get("pressure", "?")
        fill = state.get("fill_pct")
        detail = f"pressure={level}"
        if fill is not None:
            detail += f", fill={fill:.0%}"
        detail += f", updated {age}"
        status = "STALE" if age_secs > 3600 else "OK"
        rows.append(("session-pressure", status, detail))
        if status == "STALE":
            fixes.append("session-pressure: state file >1h old — PostToolUse hook may not be registered")
    except Exception as e:
        rows.append(("session-pressure", "BROKEN", f"parse error: {e}"))
        fixes.append("session-pressure: corrupt state file — delete and let hook recreate")
else:
    rows.append(("session-pressure", "BROKEN", "state file missing — hook never ran"))
    fixes.append("session-pressure: resource-pressure.py not registered in settings.json PostToolUse")

# --- Tier 4: hook-errors.log ---
errors_log = os.path.expanduser("~/.claude/hooks/state/hook-errors.log")
if os.path.exists(errors_log):
    cutoff = now.timestamp() - 7 * 86400
    recent = []
    try:
        with open(errors_log) as f:
            for line in f:
                line = line.rstrip()
                if not line:
                    continue
                recent.append(line)
        # count errors in last 7 days (lines with ISO timestamps)
        week_lines = []
        for line in recent:
            # lines start with [2026-... ] timestamp
            try:
                ts_part = line[1:line.index("]")]
                ts = datetime.fromisoformat(ts_part.replace("Z", "+00:00"))
                if ts.timestamp() > cutoff:
                    week_lines.append(line)
            except Exception:
                pass
        count = len(week_lines)
        last3 = week_lines[-3:] if week_lines else []
        status = "STALE" if count == 0 else ("OK" if count < 10 else "STALE")
        detail = f"{count} errors in last 7d"
        rows.append(("hook-errors", status, detail))
        if last3:
            print(f"\nhook-errors.log — last {len(last3)} recent entries:")
            for l in last3:
                print(f"  {l[:120]}")
        if count >= 10:
            fixes.append(f"hook-errors: {count} errors in 7d — check ~/.claude/hooks/state/hook-errors.log")
    except Exception as e:
        rows.append(("hook-errors", "BROKEN", f"read error: {e}"))
        fixes.append("hook-errors: cannot read log file")
else:
    rows.append(("hook-errors", "OK", "no errors logged (file absent)"))

# --- Print table ---
col_w = [20, 8, 60]
header = f"{'Tier':<{col_w[0]}} {'Status':<{col_w[1]}} {'Detail'}"
sep = "-" * (col_w[0] + col_w[1] + col_w[2] + 2)
print(f"\n{header}")
print(sep)
for tier, status, detail in rows:
    marker = "" if status == "OK" else ("! " if status == "STALE" else "X ")
    print(f"{marker+tier:<{col_w[0]}} {status:<{col_w[1]}} {detail}")

if fixes:
    print(f"\nSuggested fixes:")
    for f in fixes:
        print(f"  - {f}")
else:
    print("\nAll tiers OK.")
PYEOF
```
