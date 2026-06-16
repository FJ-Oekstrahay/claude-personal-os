#!/usr/bin/env python3
"""
Tracks per-session context token fill pressure for rate-limit-aware commands.

Primary method: reads context token usage from the session JSONL file and computes
fill percentage against the 200,000-token Sonnet 4.6 context window.

Fallback: if JSONL not found or no usage data, falls back to tool-call counting.

Modes:
  python3 resource-pressure.py          — PostToolUse: reads JSON from stdin, updates state
  python3 resource-pressure.py --reset  — SessionStart: resets state for new session

State file: ~/.claude/hooks/state/session-pressure.json

Schema:
  session_id              — matches current Claude Code session
  tool_calls              — running total (fallback path; Agent/Task count double)
  cumulative_tool_calls   — running total of ALL PostToolUse calls (both paths); used by stop gate
  fill_pct                — float 0–1, context window fill from token usage (primary path)
  jsonl_path              — cached path to session JSONL, or null
  pressure                — "normal" | "elevated" | "high"
  checkpoint_due          — true when fill_pct >= 0.65 (or tool_calls >= 40 in fallback)
  last_updated            — ISO timestamp
"""

import glob
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone

STATE_DIR = os.path.expanduser("~/.claude/hooks/state")
STATE_FILE = os.path.join(STATE_DIR, "session-pressure.json")
WAVE_LOG = os.path.join(STATE_DIR, "wave-log.jsonl")
PROJECTS_DIR = os.path.expanduser("~/.claude/projects")

CONTEXT_WINDOW = 200_000

# Agent/Task spawns amplify tool usage significantly (fallback path)
HEAVY_TOOLS = {"Agent", "Task"}


def pressure_level_from_fill(fill_pct: float) -> str:
    if fill_pct < 0.50:
        return "normal"
    if fill_pct < 0.75:
        return "elevated"
    return "high"


def pressure_level_from_calls(tool_calls: int) -> str:
    if tool_calls < 30:
        return "normal"
    if tool_calls < 60:
        return "elevated"
    return "high"


def load_state() -> dict:
    try:
        with open(STATE_FILE) as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def save_state(state: dict):
    os.makedirs(STATE_DIR, exist_ok=True)
    state["last_updated"] = datetime.now(timezone.utc).isoformat()
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)


def find_jsonl(session_id: str) -> str | None:
    """Search for the session JSONL file under ~/.claude/projects."""
    try:
        result = subprocess.run(
            ["find", PROJECTS_DIR, "-name", f"{session_id}.jsonl", "-maxdepth", "2"],
            capture_output=True, text=True, timeout=5
        )
        lines = result.stdout.strip().splitlines()
        if lines:
            return lines[0]
    except Exception:
        pass
    return None


def read_wave_density() -> int:
    """Count tool calls in wave-log.jsonl within the last 60 seconds."""
    cutoff = time.time() - 60
    count = 0
    try:
        with open(WAVE_LOG) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    entry = json.loads(line)
                    if entry.get("ts", 0) >= cutoff:
                        count += 1
                except Exception:
                    pass
    except FileNotFoundError:
        pass
    except Exception:
        pass
    return count


def read_fill_pct(jsonl_path: str) -> float | None:
    """Scan JSONL for last assistant message with usage data; return fill fraction."""
    try:
        last_usage = None
        with open(jsonl_path) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    entry = json.loads(line)
                except json.JSONDecodeError:
                    continue
                msg = entry.get("message", {})
                usage = msg.get("usage")
                if usage:
                    last_usage = usage
        if last_usage is None:
            return None
        total = (
            last_usage.get("input_tokens", 0)
            + last_usage.get("cache_read_input_tokens", 0)
            + last_usage.get("cache_creation_input_tokens", 0)
        )
        return total / CONTEXT_WINDOW
    except Exception:
        return None


def reset_mode():
    data = {}
    try:
        raw = sys.stdin.read().strip()
        if raw:
            data = json.loads(raw)
    except Exception:
        pass

    session_id = data.get("session_id", "unknown")
    state = {
        "session_id": session_id,
        "tool_calls": 0,
        "cumulative_tool_calls": 0,
        "fill_pct": 0.0,
        "jsonl_path": None,
        "pressure": "normal",
        "checkpoint_due": False,
        "manual_override": False,
    }
    save_state(state)


def post_tool_mode():
    try:
        data = json.loads(sys.stdin.read())
    except Exception:
        sys.exit(0)

    session_id = data.get("session_id", "unknown")
    tool_name = data.get("tool_name", "")

    state = load_state()

    # New session detected — reset rather than accumulate across sessions
    if state.get("session_id") != session_id:
        state = {
            "session_id": session_id,
            "tool_calls": 0,
            "cumulative_tool_calls": 0,
            "fill_pct": 0.0,
            "jsonl_path": None,
            "checkpoint_due": False,
        }

    # --- Always increment cumulative counter on every PostToolUse call ---
    state["cumulative_tool_calls"] = state.get("cumulative_tool_calls", 0) + 1

    # --- Always update: tool_calls, fill_pct, jsonl_path ---
    jsonl_path = state.get("jsonl_path")
    if not jsonl_path:
        jsonl_path = find_jsonl(session_id)
        state["jsonl_path"] = jsonl_path

    fill_pct = None
    if jsonl_path:
        fill_pct = read_fill_pct(jsonl_path)

    if fill_pct is not None:
        state["fill_pct"] = fill_pct
    else:
        increment = 2 if tool_name in HEAVY_TOOLS else 1
        state["tool_calls"] = state.get("tool_calls", 0) + increment

    # --- Wave density: read from objective log (wave-counter.py writes it) ---
    wave_density = read_wave_density()
    state["wave_density"] = wave_density

    # --- Respect manual_override: skip pressure/checkpoint_due if set ---
    if not state.get("manual_override"):
        if fill_pct is not None:
            state["pressure"] = pressure_level_from_fill(fill_pct)
            state["checkpoint_due"] = fill_pct >= 0.65
        else:
            state["pressure"] = pressure_level_from_calls(wave_density)
            state["checkpoint_due"] = wave_density >= 40

    save_state(state)


if __name__ == "__main__":
    if "--reset" in sys.argv:
        reset_mode()
    else:
        post_tool_mode()
