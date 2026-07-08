#!/usr/bin/env python3
"""TEMPLATE — Stop hook: compliance tripwire.

Compares two files' line counts against a SessionStart snapshot. If FILE_A
grew but FILE_B did NOT, that's a proxy for "substantive work happened but
the paired record-keeping file was skipped." We can't block retroactively at
Stop, so we write a flag file that the next SessionStart is expected to
surface — turning a silent miss into a visible one next session.

Copy into a project's .claude/hooks/, fill in the two file paths (relative
to the project root) and the message. Derived from
health/.claude/hooks/reasoning_log_tripwire.py. On-demand only — not
auto-installed anywhere.

Hook lessons baked in (see distillation/checklist.md section D):
- Fail-open BY DESIGN: exit 0 always. A tripwire that blocks the Stop event
  itself would be far more disruptive than a missed compliance flag — this
  is a deliberate choice, not a shortcut. (A hook whose JOB is to block
  must fail CLOSED instead: exit 2 if input can't be parsed.)
- Stop hooks can fire MULTIPLE times per turn — this script is idempotent:
  re-running it with the same snapshot/state produces the same flag file
  contents, so a double-fire doesn't corrupt state or double-append.
- Uses __file__-relative paths to find PROJ, not a hardcoded absolute path
  — so the template is portable across projects without editing a path
  buried in logic.
"""
import json
import os
import sys

# --- fill in for your project ---
FILE_A_REL = "__RELATIVE_PATH_TO_FILE_A__"   # e.g. docs/discussion-log.md
FILE_B_REL = "__RELATIVE_PATH_TO_FILE_B__"   # e.g. docs/reasoning-log.md
TRIPWIRE_MSG_TEMPLATE = (
    "TRIPWIRE: last session appended to {a} but NOT to {b}. "
    "Confirm this was expected, or write the missing entry."
)
# ---------------------------------

PROJ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
STATE = os.path.join(PROJ, ".claude", "hooks", "state")
SNAP_FILE = os.path.join(STATE, "session-snapshot.json")
FLAG_FILE = os.path.join(STATE, "last-compliance-flag.txt")


def linecount(rel):
    p = os.path.join(PROJ, rel)
    try:
        with open(p, "r", encoding="utf-8") as f:
            return sum(1 for _ in f)
    except Exception:
        return 0


def main():
    try:
        sys.stdin.read()
    except Exception:
        pass

    try:
        snap = json.load(open(SNAP_FILE))
    except Exception:
        sys.exit(0)  # no snapshot -> nothing to compare; stay silent

    a_now = linecount(FILE_A_REL)
    b_now = linecount(FILE_B_REL)
    a_grew = a_now > snap.get("a", 0)
    b_grew = b_now > snap.get("b", 0)

    if a_grew and not b_grew:
        msg = TRIPWIRE_MSG_TEMPLATE.format(a=FILE_A_REL, b=FILE_B_REL)
        try:
            os.makedirs(STATE, exist_ok=True)
            with open(FLAG_FILE, "w", encoding="utf-8") as f:
                f.write(msg)
        except Exception:
            pass
        sys.stderr.write(msg + "\n")

    sys.exit(0)


if __name__ == "__main__":
    main()

# Registration example (project .claude/settings.json):
# {
#   "hooks": {
#     "Stop": [
#       { "hooks": [{ "type": "command", "command": "python3 .claude/hooks/stop-tripwire.py" }] }
#     ]
#   }
# }
#
# The paired SessionStart hook that WRITES session-snapshot.json (with keys
# "a" and "b" set to current linecount(FILE_A_REL)/linecount(FILE_B_REL)) is
# project-specific and not templated here — write it alongside this hook.
