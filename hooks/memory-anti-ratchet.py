#!/usr/bin/env python3
"""SessionStart hook — memory anti-ratchet (C7 generalization of health's differential
metadata). Domain-neutral belief-staleness computer for the auto-memory system.

Reads the claude-config auto-memory dir, parses `Belief metadata` blocks off their literal
`key:` lines, computes staleness/entrenchment, and emits a challenge notice on stdout so the
model never has to *remember* to re-examine a belief that gets re-injected every session.

Schema + rationale: specs/anti-ratchet-belief-metadata.md.

Fail-soft: this hook only *injects context*; it must never crash the session. On any read/parse
error it emits a LOUD degraded notice and exits 0 — a silent failure would re-create the exact
"you can't tell if the discipline ran" hole the mechanism exists to close.
"""
import os
import re
import sys
from datetime import date, datetime

# Claude Code's built-in auto-memory dir for THIS project (the same dir MEMORY.md loads from).
# Path is Claude Code's per-project slug of the cwd; hardcoded because this hook is project-scoped
# to claude-config. Out-of-repo and NOT version-controlled — see spec §2 "Data-source asymmetry".
MEMORY_DIR = os.path.expanduser(
    "~/.claude/projects/<project-slug>/memory"
)

# Parameterized triggers — health defaults (spec §1).
STALE_DAYS = 30
SELF_CHALLENGE_CAP = 2          # >= this many self-challenges w/o external -> escalate
SESSIONS_CARRIED_TRIGGER = 3    # >= this many sessions carried -> external review due

BLOCK_MARKER = "Belief metadata"


def _today():
    return date.today()


def _parse_date(s):
    # tolerate a trailing annotation, e.g. `Last challenged:` 2026-06-16 (self)
    m = re.search(r"\d{4}-\d{2}-\d{2}", s)
    if not m:
        raise ValueError(f"no YYYY-MM-DD in {s!r}")
    return datetime.strptime(m.group(), "%Y-%m-%d").date()


def _emit(lines):
    """Write the preamble, guaranteeing we never crash the session on an encoding
    error (the whole hook is fail-soft). Non-ASCII glyphs (═, ⚠) raise
    UnicodeEncodeError under an ASCII stdout locale (LANG=C); fall back to ASCII."""
    text = "\n".join(lines) + "\n"
    try:
        sys.stdout.write(text)
    except Exception:
        try:
            sys.stdout.write(text.encode("ascii", "replace").decode("ascii"))
        except Exception:
            pass


def _int(s):
    try:
        return int(re.search(r"-?\d+", s).group())
    except Exception:
        return None


def parse_belief(text, fname):
    """Return a dict for a memory file carrying a Belief metadata block, else None.
    Keyed off the literal `key:` lines we control (regex-parsed, format is load-bearing)."""
    if BLOCK_MARKER not in text:
        return None

    def grab(key):
        m = re.search(r"`" + re.escape(key) + r":`\s*([^\n]+)", text)
        return m.group(1).strip() if m else None

    d = {
        "file": fname,
        "belief": grab("Belief"),
        "last_challenged": grab("Last challenged"),
        "challenge_source": grab("Challenge source"),
        "self_since_external": grab("Self-challenges since last external"),
        "sessions_carried": grab("Sessions carried"),
        "external_review": grab("External review"),
    }
    # The marker string can appear in prose (e.g. a memo that *describes* the schema) without any
    # real `key:` lines. Only count it as an instrumented belief if at least one field parsed —
    # otherwise it's a phantom that would inflate the belief count.
    if not any(v for k, v in d.items() if k != "file"):
        return None
    return d


def evaluate(b):
    """Return list of action strings for one belief record."""
    actions = []
    # short, stable label: the belief text if present, else the filename
    label = (b["belief"] or b["file"]).strip()
    if len(label) > 80:
        label = label[:77] + "..."

    # explicit external-review due-flag already set in the record
    er = b["external_review"]
    if er and er.lower().startswith("due"):
        actions.append(f"{label}: External review DUE ({er}) — challenge this belief against "
                       f"reality before relying on it; a self-challenge will NOT clear it.")

    # event trigger: sessions carried (re-injection count — the core memory failure mode)
    sc = _int(b["sessions_carried"] or "")
    if sc is not None and sc >= SESSIONS_CARRIED_TRIGGER:
        actions.append(f"{label}: carried {sc} sessions (>= {SESSIONS_CARRIED_TRIGGER}) without "
                       f"an external challenge -> external review due.")

    # event trigger: self-challenge cap
    ss = _int(b["self_since_external"] or "")
    if ss is not None and ss >= SELF_CHALLENGE_CAP:
        actions.append(f"{label}: {ss} self-challenges with no external (>= {SELF_CHALLENGE_CAP}) "
                       f"-> escalate to external; re-reasoning can no longer advance "
                       f"'Last challenged'.")

    # calendar staleness
    lc = b["last_challenged"]
    if lc:
        try:
            days = (_today() - _parse_date(lc)).days
            if days > STALE_DAYS:
                actions.append(f"{label}: last challenged {days}d ago (> {STALE_DAYS}) -> run a "
                               f"self-challenge (strongest case the belief is now wrong/stale + "
                               f"cheapest way to check), then update the fields.")
        except Exception:
            actions.append(f"{label}: 'Last challenged' unparseable ('{lc}') -> fix to YYYY-MM-DD.")
    return actions


def main():
    # first-line defense: prefer UTF-8 stdout with replacement so the glyphs below
    # never raise; _emit() is the belt-and-suspenders fallback if this isn't honored.
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

    # consume stdin (hook payload) defensively; we don't require any field
    try:
        sys.stdin.read()
    except Exception:
        pass

    lines = ["═══ MEMORY ANTI-RATCHET (computed by hook — act on this, do not re-derive) ═══"]

    try:
        if not os.path.isdir(MEMORY_DIR):
            lines.append(f"⚠ DEGRADED: auto-memory dir not found ({MEMORY_DIR}) — belief-staleness "
                         f"NOT checked this session. Surface instrumented beliefs manually.")
            lines.append("═" * 72)
            _emit(lines)
            sys.exit(0)

        beliefs = []
        for fname in sorted(os.listdir(MEMORY_DIR)):
            if not fname.endswith(".md") or fname == "MEMORY.md":
                continue
            path = os.path.join(MEMORY_DIR, fname)
            try:
                with open(path, "r", encoding="utf-8") as f:
                    text = f.read()
            except Exception:
                continue
            b = parse_belief(text, fname)
            if b:
                beliefs.append(b)

        actions = []
        for b in beliefs:
            actions.extend(evaluate(b))

        if not beliefs:
            lines.append("  • no instrumented beliefs found (no 'Belief metadata' blocks). "
                         "Pilot inert — this is expected until a belief is instrumented.")
        elif actions:
            for a in actions:
                lines.append(f"  • {a}")
        else:
            lines.append(f"  • {len(beliefs)} belief(s) instrumented; none due for challenge.")
    except Exception as e:
        # loud degraded notice, never crash the session
        lines.append(f"⚠ DEGRADED: memory anti-ratchet hook errored ({e}) — surface instrumented "
                     f"beliefs manually this session.")

    lines.append("═" * 72)
    _emit(lines)
    sys.exit(0)


if __name__ == "__main__":
    main()
