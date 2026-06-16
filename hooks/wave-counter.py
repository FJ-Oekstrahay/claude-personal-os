#!/usr/bin/env python3
"""
PostToolUse hook: appends tool call events to a rolling 60-second wave log.

Reads PostToolUse JSON from stdin, appends one line {"ts": <epoch_float>, "tool": "<name>"}
to ~/.claude/hooks/state/wave-log.jsonl. Pruning of the 60-second window happens on the
read side in resource-pressure.py:read_wave_density().

Append-only avoids last-writer-wins clobber under parallel subagent PostToolUse fires.
Fails open on any error (exit 0 silently).
"""

import json
import os
import sys
import time

WAVE_LOG = os.path.expanduser("~/.claude/hooks/state/wave-log.jsonl")


def main():
    try:
        raw = sys.stdin.read()
        data = json.loads(raw)
        tool_name = data.get("tool_name", "unknown")
    except Exception:
        sys.exit(0)

    now = time.time()
    entry = json.dumps({"ts": now, "tool": tool_name})

    try:
        os.makedirs(os.path.dirname(WAVE_LOG), exist_ok=True)
        with open(WAVE_LOG, "a") as f:
            f.write(entry + "\n")
    except Exception:
        pass

    sys.exit(0)


if __name__ == "__main__":
    main()
