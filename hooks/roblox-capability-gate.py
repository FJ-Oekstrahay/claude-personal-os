#!/usr/bin/env python3
"""
Roblox capability gate — stop the model from (a) claiming something is impossible
and (b) hand-rolling a system, WITHOUT first checking the capability surface that
already exists.

Why this exists (Geoff, 2026-08-07): "you still either tell me you can't do
something when it turns out you can, or you think up a solution that is
reinventing the wheel when it turns out the standard way of doing things was
easily findable."

CLAUDE.md and MEMORY.md already say to check. That did not work — a reminder is
more of what already failed. This is an ENFORCEMENT layer: it reads the
transcript for actual evidence of a capability check and blocks when there is
none.

Two modes, wired as two separate hooks in ~/.claude/settings.json:

  pretool  — PreToolUse, matcher "Write". Fires when the model creates a NEW
             .lua/.luau file (a new system = the reinvention moment) with zero
             capability-check evidence this session. Truly preventive: it fires
             BEFORE the wheel gets rebuilt.

  stop     — Stop hook. Fires when the final assistant message contains an
             impossibility claim ("can't", "there is no API for", "we'd have to
             build our own") with zero capability-check evidence this session.
             Catches the case that lives in prose, not in a tool call.

STALENESS INTEGRATION (added 2026-08-08): when the gate fires, it also runs the
project's `tools/roblox_staleness_check.py` and appends any stale-doc warnings
to the block message. This delivers the staleness signal exactly when someone is
about to RELY on those surveys — not on a calendar. The staleness check is
advisory (it adds context to the existing block); it never causes a block on its
own. Fail-open: if the script is missing or errors, the gate works exactly as it
did before.

Exit codes:
  0 — allow.
  2 — block; STDERR is fed back to the model as the reason.

FAIL-OPEN on every error. For a Stop hook, "fail closed" means wedging the
session in an unstoppable loop; for this PreToolUse gate it means bricking every
Lua write on a parse bug. Both are worse than a missed check. This deliberately
inverts the global CLAUDE.md "fail closed" lesson, which was written for
PreToolUse *protection* hooks guarding a resource — the same reasoning
batchc-stop-gate.py documents at its top.

Loop/nag prevention (any one suffices):
  1. stop_hook_active=True (stop mode) → allow.
  2. per-session marker file → each mode fires AT MOST ONCE per session.
  3. capability-check evidence found in the transcript → allow.

Escape hatch for genuine negatives: some "no" answers are settled and recorded
(e.g. project-cannot-save-or-publish-from-mcp). Condition 3 normally handles
this, because settling one requires having looked. The block text explicitly
tells the model it may close the loop by citing the catalog entry or the memory
that settles it — so a true negative costs one extra turn, not a fight.
"""

import json
import os
import re
import subprocess
import sys

STATE_DIR = os.path.expanduser("~/.claude/hooks/state")

# --- What counts as "this session did a capability check" --------------------
# Deliberately GENEROUS. A false PASS costs one missed nudge; a false BLOCK
# trains Geoff to disable the hook. Any one of these disarms the gate.

# Tool calls that ARE a capability check by their nature.
EVIDENCE_TOOL_NAMES = (
    "mcp__Roblox_Studio__skill",       # the 6 bundled rbx-* skills
    "mcp__Roblox_Studio__http_get",    # rbx-docs-search recipe against create.roblox.com/docs
    "mcp__Roblox_Studio__search_asset",
    "WebSearch",
    "WebFetch",
    "ToolSearch",                      # loading a deferred MCP tool schema IS enumerating the API
)
# Files/strings whose appearance in a tool INPUT means the surface was consulted.
EVIDENCE_PATH_MARKERS = (
    "roblox-capabilities",             # docs/reference/ROBLOX-CAPABILITIES.md
    "llms.txt",
    "create.roblox.com",
    "developer.roblox.com",
    "/.claude/skills/",                # reading an installed skill
    "roblox-third-party-skills",       # the ecosystem survey doc
)
# A Skill/Agent dispatch aimed at capability discovery.
EVIDENCE_SKILL_NAMES = {"mmguns", "become-expert", "deep-research", "claude-code-guide"}

# --- Impossibility / reinvention language (stop mode) ------------------------
# Matched against the FINAL assistant message only. Kept to phrasings that make
# a capability CLAIM; bare "can't" in other senses ("I can't tell from here")
# is accepted collateral because the conjunction with "no evidence at all this
# session" plus one-shot-per-session keeps the false-positive cost to one turn.
IMPOSSIBILITY_PATTERNS = [
    r"\b(?:can'?t|cannot|unable to)\b[^.\n]{0,60}\b(?:do|make|set|read|write|get|access|drive|control|render|simulate|automate|measure|capture|publish|save|test)\b",
    r"\bthere(?:'s| is| are)?\s+no\b[^.\n]{0,40}\b(?:api|tool|way|method|service|hook|event|property|option|support)\b",
    r"\bno (?:api|tool|way|method|built-?in|native)\b[^.\n]{0,30}\bfor\b",
    r"\b(?:doesn'?t|does not|isn'?t|is not)\s+(?:exist|supported|available|possible|expose)",
    r"\bnot (?:possible|supported|exposed|available)\b",
    r"\bthe (?:engine|api|studio|platform) (?:doesn'?t|does not|lacks)\b",
]
REINVENTION_PATTERNS = [
    r"\b(?:build|write|implement|roll)(?:ing)? (?:our|my|a) own\b",
    r"\bfrom scratch\b",
    r"\bhand-?roll",
    r"\bcustom (?:implementation|system|solution|framework|module)\b",
    r"\bwe'?(?:d|ll) have to (?:build|write|implement)\b",
    r"\bi'?(?:d|ll) (?:just )?(?:build|write|implement) (?:a|my own|our own)\b",
]

# --- Is this session Roblox-shaped? -----------------------------------------
ROBLOX_SIGNALS = ("mcp__roblox_studio__", ".lua", ".luau", "default.project.json", "rojo")

CHECKLIST = """\
[roblox-capability-gate] STOP — you are about to {verb}, and this session shows \
ZERO evidence that you checked what already exists. This is the exact failure \
Geoff called out: claiming you can't, or rebuilding a wheel, when the standard \
way was one lookup away.

Do these BEFORE continuing. Not all of them every time — enough of them that \
your answer is grounded in a lookup, not a recollection:

1. `docs/reference/ROBLOX-CAPABILITIES.md` — 27 `mcp__Roblox_Studio__*` tools \
flagged used/never-used, the 6 bundled `rbx-*` skills, `search_asset` scope + \
`verifiedCreatorsOnly`, and the collected traps. READ IT.
2. `docs/reference/ROBLOX-THIRD-PARTY-SKILLS.md` — the surveyed third-party \
Claude Code skill ecosystem. Check whether someone already packaged this.
3. `mcp__Roblox_Studio__skill` — the 6 bundled skills are the enum, not a \
sample: rbx-device-simulator-lua, rbx-docs-search, rbx-scene-analysis, \
rbx-perf-profiling, rbx-unit-test, rbx-create-skill.
4. TWO greps, not one (memory: feedback-grep-before-claiming-the-engine-lacks-it):
   - grep `src/` — "do WE already have it?"
   - `rbx-docs-search` / Roblox llms.txt — "does ROBLOX already have it?"
5. Official Roblox kits (memory: project-roblox-ships-official-game-kits) — \
Weapons, NPC, Battle-Royale. They implement much of what this project hand-built.
6. The deferred-tool list itself. Several of the 27 MCP tools have NEVER been \
called here. `ToolSearch` loads a schema in one call — enumerate the API before \
concluding it lacks something (memory: feedback-fix-the-environment-dont-report-it, \
"four rejected guesses is not a proof of impossibility").

If the answer is a GENUINE, ALREADY-SETTLED no — say so and CITE it: the \
ROBLOX-CAPABILITIES.md entry or the project memory that settles it (e.g. \
project-cannot-save-or-publish-from-mcp). A cited negative closes this cleanly. \
An uncited one does not.

MAINTENANCE (do not skip): if this check turns up a capability that is NOT in \
`docs/reference/ROBLOX-CAPABILITIES.md`, append it in THIS session, tagged \
[measured] / [cited] / [unverified]. That file decays into a stale pointer \
otherwise, and then this gate is pointing at nothing.

This gate fires at most ONCE per session per mode. It will not block you again.\
"""


def _mark_path(session_id, mode):
    if not session_id:
        return None
    return os.path.join(STATE_DIR, f"{session_id}.roblox-capgate-{mode}")


def _already_fired(session_id, mode):
    p = _mark_path(session_id, mode)
    return bool(p and os.path.exists(p))


def _mark_fired(session_id, mode):
    p = _mark_path(session_id, mode)
    if not p:
        return
    try:
        os.makedirs(STATE_DIR, exist_ok=True)
        with open(p, "w") as f:
            f.write("1")
    except Exception:
        pass


def _iter_transcript(transcript_path):
    if not transcript_path or not os.path.exists(transcript_path):
        return
    try:
        with open(transcript_path) as f:
            for line in f:
                try:
                    yield json.loads(line)
                except Exception:
                    continue
    except Exception:
        return


def scan_transcript(transcript_path):
    """Return (has_capability_evidence, is_roblox_session, last_assistant_text).

    Only ASSISTANT tool_use blocks and assistant text are inspected. Tool
    RESULTS arrive as type=="user" with a LIST content and can echo any string
    on disk — including this very file — so matching them would let `grep`ping
    the hook disarm the hook. That exact false-PASS bug is documented in
    batchc-stop-gate.py; do not reintroduce it here.
    """
    evidence = False
    roblox = False
    last_text = ""

    for e in _iter_transcript(transcript_path):
        if e.get("type") != "assistant":
            continue
        content = e.get("message", {}).get("content", [])
        if not isinstance(content, list):
            continue
        texts = []
        for b in content:
            if not isinstance(b, dict):
                continue
            btype = b.get("type")

            if btype == "text":
                texts.append(str(b.get("text", "") or ""))
                continue

            if btype != "tool_use":
                continue

            name = str(b.get("name", "") or "")
            inp = b.get("input", {}) or {}
            try:
                blob = json.dumps(inp).lower()
            except Exception:
                blob = str(inp).lower()

            if name.lower().startswith("mcp__roblox_studio__"):
                roblox = True
            if any(s in blob for s in ROBLOX_SIGNALS):
                roblox = True

            if name in EVIDENCE_TOOL_NAMES:
                evidence = True
            if any(m in blob for m in EVIDENCE_PATH_MARKERS):
                evidence = True
            if name == "Skill":
                sk = str(inp.get("skill", "") or "").strip().lower().rpartition(":")[2]
                if sk in EVIDENCE_SKILL_NAMES or sk.startswith("rbx-"):
                    evidence = True
            if name in ("Agent", "Task"):
                st = str(inp.get("subagent_type", "") or "").strip().lower()
                if st in ("claude-code-guide", "explore"):
                    evidence = True

        if texts:
            last_text = "\n".join(texts)

    return evidence, roblox, last_text


def _cwd_is_roblox(cwd):
    try:
        return os.path.exists(os.path.join(cwd or "", "default.project.json"))
    except Exception:
        return False


def _staleness_warning(cwd):
    """Run the project's Roblox staleness check, return its output if anything is stale.

    Advisory only — appends context to the existing block message, never causes
    a block on its own. Fail-open: missing script or any error returns "".
    """
    try:
        script = os.path.join(cwd or "", "tools", "roblox_staleness_check.py")
        if not os.path.exists(script):
            return ""
        out = subprocess.run(
            ["python3", script, "--quiet"],
            capture_output=True, text=True, timeout=10,
            cwd=cwd or None,
        )
        return out.stdout.strip()
    except Exception:
        return ""


def _block(session_id, mode, verb, cwd=""):
    _mark_fired(session_id, mode)
    msg = CHECKLIST.format(verb=verb)
    stale = _staleness_warning(cwd)
    if stale:
        msg += "\n\n" + stale
    sys.stderr.write(msg + "\n")
    sys.exit(2)


def run_pretool(data):
    """Block the creation of a NEW .lua/.luau file when nothing was checked."""
    if str(data.get("tool_name", "")) != "Write":
        sys.exit(0)

    inp = data.get("tool_input", {}) or {}
    fp = str(inp.get("file_path", "") or "")
    if not fp.lower().endswith((".lua", ".luau")):
        sys.exit(0)
    # Only NEW files. Overwriting a file that exists is editing, not inventing.
    if os.path.exists(os.path.expanduser(fp)):
        sys.exit(0)

    session_id = data.get("session_id", "") or ""
    if _already_fired(session_id, "pretool"):
        sys.exit(0)

    evidence, roblox, _txt = scan_transcript(data.get("transcript_path", ""))
    if evidence:
        sys.exit(0)

    # Roblox-scope guard. Without this, ANY session on this machine writing a new
    # .lua file — a Neovim config, an unrelated repo — eats a block telling it to
    # read docs/reference/ROBLOX-CAPABILITIES.md, a file that doesn't exist there.
    # A false block in an unrelated project is the fastest route to this hook
    # being deleted. run_stop has always had this guard; run_pretool shipped
    # without it (caught in review before it ever fired).
    if not roblox and not _cwd_is_roblox(data.get("cwd", "")):
        sys.exit(0)

    _block(session_id, "pretool",
           "create a NEW Luau system file (`%s`)" % os.path.basename(fp),
           cwd=data.get("cwd", ""))


def run_stop(data):
    """Block the stop when the last message claims impossibility with no lookup."""
    if data.get("stop_hook_active"):
        sys.exit(0)

    session_id = data.get("session_id", "") or ""
    if _already_fired(session_id, "stop"):
        sys.exit(0)

    evidence, roblox, last_text = scan_transcript(data.get("transcript_path", ""))
    if evidence:
        sys.exit(0)

    if not roblox and not _cwd_is_roblox(data.get("cwd", "")):
        sys.exit(0)

    if not last_text:
        sys.exit(0)
    low = last_text.lower()

    hit_imp = any(re.search(p, low) for p in IMPOSSIBILITY_PATTERNS)
    hit_rei = any(re.search(p, low) for p in REINVENTION_PATTERNS)
    if not (hit_imp or hit_rei):
        sys.exit(0)

    verb = ("declare something IMPOSSIBLE" if hit_imp
            else "propose building something from scratch")
    _block(session_id, "stop", verb, cwd=data.get("cwd", ""))


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "stop"
    try:
        data = json.loads(sys.stdin.read())
    except Exception:
        sys.exit(0)  # fail-open: never wedge a session, never brick a write

    try:
        if mode == "pretool":
            run_pretool(data)
        else:
            run_stop(data)
    except SystemExit:
        raise
    except Exception:
        sys.exit(0)  # fail-open on any unexpected error
    sys.exit(0)


if __name__ == "__main__":
    main()
