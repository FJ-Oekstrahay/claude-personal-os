#!/usr/bin/env python3
"""PostToolUse audit trail hook — appends one JSONL entry per tool call."""

import json
import os
import sys
import time
from datetime import datetime

try:
    payload = json.load(sys.stdin)
    tool_name = payload.get("tool_name", "unknown")
    tool_input = payload.get("tool_input", {})

    ts = time.time()
    date_str = datetime.utcfromtimestamp(ts).strftime("%Y%m%d")
    session_id = payload.get("session_id") or os.environ.get("CLAUDE_SESSION_ID", "unknown")

    summary = json.dumps(tool_input)[:120]

    entry = {
        "ts": ts,
        "session_id": session_id,
        "tool": tool_name,
        "summary": summary,
    }

    state_dir = os.path.expanduser("~/.claude/hooks/state")
    log_path = os.path.join(state_dir, f"audit-{date_str}.jsonl")

    with open(log_path, "a") as f:
        f.write(json.dumps(entry) + "\n")

except Exception:
    pass

sys.exit(0)
