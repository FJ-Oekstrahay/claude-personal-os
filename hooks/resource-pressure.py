#!/usr/bin/env python3
"""
Tracks per-session context token fill pressure for rate-limit-aware commands.

Primary method: reads context token usage from the session JSONL file and computes
fill percentage against the *model's actual* context window.

Fallback: if JSONL not found or no usage data, falls back to tool-call counting.

Modes:
  python3 resource-pressure.py          — PostToolUse: reads JSON from stdin, updates state
  python3 resource-pressure.py --reset  — SessionStart: resets state for new session

State files:
  ~/.claude/hooks/state/session-pressure.json               — legacy shared path (mirror)
  ~/.claude/hooks/state/session-pressure-<session_id>.json  — per-session, authoritative

  The legacy path is still written on every update so existing consumers
  (batchc-stop-gate.py, /pressure, /memory-health) keep working unchanged. With
  multiple concurrent sessions on one machine, the legacy file reflects whichever
  session made the most recent tool call — read the per-session file when you can.

Schema:
  session_id              — matches current Claude Code session
  tool_calls              — running total (fallback path; Agent/Task count double)
  cumulative_tool_calls   — running total of ALL PostToolUse calls (both paths); used by stop gate
  fill_pct                — float 0–1, context window fill from token usage (primary path)
  context_tokens          — absolute prompt tokens on the last request
  context_window          — denominator used for fill_pct (model-resolved, self-healing)
  model                   — model id from the last assistant message with usage
  jsonl_path              — cached path to session JSONL, or null
  pressure                — "normal" | "elevated" | "high"
  fill_stale              — true when this tick had no usage record, so fill_pct/
                            context_tokens/context_window are carried over, not fresh
  checkpoint_due          — true when fill_pct >= 0.65 (or wave_density >= 40 in fallback)
  last_updated            — ISO timestamp
"""

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

# Context window tiers. A wrong denominator is the difference between "5% full"
# and "26% full", so this is resolved from the model rather than hardcoded.
# Verified 2026-08-13 against claude 2.1.231. Note the `[1m]` suffix is a model
# *selector* string inside the binary, NOT something that appears in transcripts —
# 0 of ~103k usage records carry any bracket suffix, so match on the bare id.
# The 1M tier is right for those bare ids regardless: observed maxima on this
# machine are opus-4-8 1,278,010 / opus-5 1,033,543 / sonnet-5 824,436.
# Haiku-class stays at 200k.
DEFAULT_WINDOW = 200_000
LARGE_WINDOW = 1_000_000
# Deliberately no 500k rung: an unrecognized model that has already blown past
# 200k is almost certainly a 1M-context model, and an intermediate tier makes the
# reading oscillate as the transcript grows (480k reads 0.96 "high", then 520k
# promotes and reads 0.52 "elevated"). Jumping straight to 1M keeps it monotone.
WINDOW_TIERS = (200_000, 1_000_000, 2_000_000)

# Substring match against the model id from the session JSONL. This is the
# binary's own 1M list (every id it carries a "<id>[1m]" selector for), not a
# guess: an earlier version listed only three of them, which left claude-opus-4-6
# — already observed at 235,302 tokens on this machine — scored against a 200k
# denominator, i.e. exactly the pinned-high bug this resolver exists to fix.
# Keep this in sync after a version bump by grepping the binary for '[1m]' —
# but treat that as a floor, not the whole list: a model whose window is 1M by
# default has no '[1m]' selector to find (see Mythos below).
LARGE_CONTEXT_MODELS = (
    "opus-4-6",
    "opus-4-7",
    "opus-4-8",
    "opus-5",
    "sonnet-4-5-20250929",
    "sonnet-4-6",
    "sonnet-5",
    "fable-5",
    # Mythos has NO "[1m]" selector in the binary, so grepping for that alone
    # drops it — which is how it went missing in an earlier revision. It belongs
    # here anyway: `claude-mythos-5` is a real id (also `us.anthropic.` and
    # `anthropic.` prefixed), and Anthropic's bundled docs state Mythos offers
    # "the same capabilities, pricing, and API behavior" as Fable. No [1m]
    # variant exists because 1M is its default, not because it is a 200k model.
    # Matches `claude-mythos-5` and `claude-mythos-preview` alike.
    "mythos",
)

# Agent/Task spawns amplify tool usage significantly (fallback path)
HEAVY_TOOLS = {"Agent", "Task"}

# How much of the tail of the JSONL to scan before falling back to a full read.
TAIL_BYTES = 2_000_000


def resolve_window(model: str | None, observed_tokens: int, previous: int | None,
                   previous_model: str | None = None) -> int:
    """Pick the context-window denominator for fill_pct.

    Order: explicit env override -> model table -> previous value -> default.
    Then self-heal: if we have already observed more prompt tokens than the
    denominator, promote to the next tier. Without this, an unknown or
    mis-tiered model pins pressure at "high" forever and every pressure-aware
    command throttles to a wave size of 1.
    """
    env = os.environ.get("CLAUDE_CODE_MAX_CONTEXT_TOKENS")
    if env:
        try:
            val = int(env)
            if val > 0:
                return val
        except ValueError:
            pass

    # Guard the type, not just the truthiness: this is the one transcript-derived
    # value used outside a try/except, and a non-string model would raise on
    # .lower(), killing the hook on EVERY PostToolUse for the rest of the session.
    # That silently freezes cumulative_tool_calls, which is what batchc-stop-gate
    # keys the §11/§12 gates on — a total, invisible disarm.
    if not isinstance(model, str):
        model = None

    if model:
        # A known model decides its own tier outright. Do NOT fall back to the
        # previous value here: `previous` persists across a mid-session /model
        # switch, so opus (1M) -> haiku (200k) would keep the 1M denominator and
        # report a 90%-full Haiku session as 18% — the inverse of the bug this
        # resolver exists to fix, and the worse direction (it hides instead of
        # nagging, so the run blows past checkpoint_due into an auto-compact).
        m = model.lower()
        window = LARGE_WINDOW if any(tag in m for tag in LARGE_CONTEXT_MODELS) else DEFAULT_WINDOW
    else:
        window = previous or DEFAULT_WINDOW

    # Self-heal: never let the denominator sit below what we have actually seen.
    if observed_tokens > window:
        for tier in WINDOW_TIERS:
            if tier > observed_tokens:
                window = tier
                break
        else:
            window = observed_tokens

    # Make the healed value sticky for as long as the model is unchanged.
    # Without this, an unrecognized large-context model re-derives the tier from
    # whatever it has observed *this tick* and the reading oscillates as the
    # transcript grows (480k read 0.96 "high", then 520k read "elevated").
    # Resets on a model switch, which is what keeps a stale window from carrying
    # over into a smaller-context model.
    if previous and previous_model and previous_model == model:
        window = max(window, previous)
    return window


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


def session_state_path(session_id: str) -> str:
    safe = "".join(c for c in (session_id or "unknown") if c.isalnum() or c in "-_")
    return os.path.join(STATE_DIR, f"session-pressure-{safe}.json")


def load_state(session_id: str | None = None) -> dict:
    """Prefer the per-session file; fall back to the legacy shared file."""
    if session_id:
        try:
            with open(session_state_path(session_id)) as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            pass
    try:
        with open(STATE_FILE) as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def save_state(state: dict):
    os.makedirs(STATE_DIR, exist_ok=True)
    state["last_updated"] = datetime.now(timezone.utc).isoformat()
    blob = json.dumps(state, indent=2)

    def atomic_write(path):
        # Temp + rename, so a concurrent reader never catches a half-written
        # file. Two files are written here, which would otherwise double the
        # torn-read window compared to the single write this replaced.
        tmp = f"{path}.{os.getpid()}.tmp"
        try:
            with open(tmp, "w") as f:
                f.write(blob)
            os.replace(tmp, path)
        except Exception:
            try:
                os.unlink(tmp)
            except OSError:
                pass

    sid = state.get("session_id")
    if sid:
        atomic_write(session_state_path(sid))
    # Legacy mirror — keeps existing consumers working unchanged.
    atomic_write(STATE_FILE)


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


def _scan_usage(lines) -> tuple[int, str] | None:
    """Return (prompt_tokens, model) for the last entry carrying usage data."""
    last = None
    for line in lines:
        line = line.strip()
        if not line:
            continue
        try:
            entry = json.loads(line)
        except json.JSONDecodeError:
            continue
        msg = entry.get("message", {})
        usage = msg.get("usage")
        if not usage:
            continue
        total = (
            usage.get("input_tokens", 0)
            + usage.get("cache_read_input_tokens", 0)
            + usage.get("cache_creation_input_tokens", 0)
        )
        # API-error and interrupt records carry a usage block that sums to zero
        # (model reads "<synthetic>"). Accepting one resets fill_pct to 0.0,
        # wipes a genuine high reading back to "normal", clears checkpoint_due,
        # and drops context_window to the default. Measured: 6 such records
        # across 54 transcripts, 3 of which END on one. Skip them.
        if total <= 0:
            continue
        last = (total, msg.get("model"))
    return last


def read_usage(jsonl_path: str) -> tuple[int, str] | None:
    """Last assistant message with usage: (prompt_tokens, model).

    Scans only the tail of the file first — these transcripts routinely reach
    tens of MB during long runs and this hook fires on every single tool call.
    Falls back to a full scan if the tail carries no usage record.
    """
    try:
        size = os.path.getsize(jsonl_path)
        if size > TAIL_BYTES:
            with open(jsonl_path, "rb") as f:
                f.seek(size - TAIL_BYTES)
                chunk = f.read().decode("utf-8", errors="ignore")
            # First line is probably truncated mid-record — drop it.
            result = _scan_usage(chunk.splitlines()[1:])
            if result is not None:
                return result
        with open(jsonl_path, errors="ignore") as f:
            return _scan_usage(f)
    except Exception:
        return None


def sweep_stale_sessions(max_age_days: int = 30):
    """Drop per-session state files older than max_age_days.

    One file per session accumulates forever otherwise, in a state dir that
    already holds >11k files.

    30 days, not 7: mtime only advances on a tool call, so a peer session that
    is open but idle looks stale. Deleting its file makes its next tick take the
    "new session detected" branch and silently drop any manual_override it had.
    30 days makes that vanishingly unlikely while still bounding the directory.
    """
    cutoff = time.time() - (max_age_days * 86400)
    try:
        for name in os.listdir(STATE_DIR):
            if not (name.startswith("session-pressure-") and name.endswith(".json")):
                continue
            path = os.path.join(STATE_DIR, name)
            try:
                if os.path.getmtime(path) < cutoff:
                    os.remove(path)
            except OSError:
                pass
    except Exception:
        pass


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
        "context_tokens": 0,
        "context_window": DEFAULT_WINDOW,
        "model": None,
        "jsonl_path": None,
        "pressure": "normal",
        "checkpoint_due": False,
        "manual_override": False,
    }
    save_state(state)
    sweep_stale_sessions()


def post_tool_mode():
    try:
        data = json.loads(sys.stdin.read())
    except Exception:
        sys.exit(0)

    session_id = data.get("session_id", "unknown")
    tool_name = data.get("tool_name", "")

    state = load_state(session_id)

    # New session detected — reset rather than accumulate across sessions
    if state.get("session_id") != session_id:
        state = {
            "session_id": session_id,
            "tool_calls": 0,
            "cumulative_tool_calls": 0,
            "fill_pct": 0.0,
            "context_tokens": 0,
            "context_window": DEFAULT_WINDOW,
            "model": None,
            "jsonl_path": None,
            "checkpoint_due": False,
        }

    # manual_override lives in this session's own state file, written directly
    # by /pressure via CLAUDE_CODE_SESSION_ID. There is deliberately no
    # carry-across from the legacy shared file: an earlier version adopted the
    # override from there, which (a) let a peer's /pressure leak into this
    # session and (b) made the override unclearable, because the adopt was
    # gated on "not already overridden" so a second /pressure was never read.
    # load_state() has already loaded whatever /pressure wrote.

    # --- Always increment cumulative counter on every PostToolUse call ---
    state["cumulative_tool_calls"] = state.get("cumulative_tool_calls", 0) + 1

    # --- Always update: tool_calls, fill_pct, jsonl_path ---
    jsonl_path = state.get("jsonl_path")
    if not jsonl_path:
        jsonl_path = find_jsonl(session_id)
        state["jsonl_path"] = jsonl_path

    usage = None
    if jsonl_path:
        usage = read_usage(jsonl_path)

    fill_pct = None
    if usage is not None:
        context_tokens, model = usage
        window = resolve_window(model, context_tokens,
                                state.get("context_window"), state.get("model"))
        fill_pct = context_tokens / window
        state["context_tokens"] = context_tokens
        state["context_window"] = window
        state["model"] = model
        state["fill_pct"] = fill_pct
        state["fill_stale"] = False
    else:
        increment = 2 if tool_name in HEAVY_TOOLS else 1
        state["tool_calls"] = state.get("tool_calls", 0) + increment
        # No usage record this tick, so fill_pct/context_tokens/context_window
        # keep their previous values while `pressure` gets recomputed from
        # wave_density below. Without this flag the state can read
        # `fill_pct: 0.82` and `pressure: "normal"` simultaneously, and batchc §0
        # now quotes those absolute numbers straight to the user.
        state["fill_stale"] = True

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
