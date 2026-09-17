---
name: Spec presearch — codebase module check
description: Verify module existence before writing spec for new CLI features; catch duplicated implementations
type: feedback
---

Pattern: A spec was written proposing a new CLI module without discovering that the module already exists and is fully implemented.

**The incident:** Session motor-night (2026-04-21) wrote `specs/motor-test.md` proposing MSP motor telemetry framing in a new `cli/motor.py` module. Upon discovery, `cli/motor.py` already exists (977 lines), fully implements MSP framing + `MSP_MOTOR_TELEMETRY` (cmd 139) + jitter sampling + baseline I/O. Spec was REJECTED as redundant.

**Root cause:** No presearch phase before writing specs. Assumptions about what exists don't match reality.

**How to apply:**

Before writing any spec that proposes a new CLI module or significant new functionality:

1. List the `cli/` directory: `ls -la cli/*.py`
2. For each file that sounds related (bf_bridge, blackbox, motor, telemetry, osd), read its first 50 lines to understand scope
3. If proposing MSP framing work: check *both* `cli/blackbox.py` (flash operations) and `cli/motor.py` (telemetry) — MSP lives in multiple places depending on context
4. Run `grep -r "def <function_name>" cli/` to verify the function doesn't exist
5. Document your presearch findings in the spec's "Prior Art" section — what exists and why you're not extending it

**Why:** Codebase is large (thousands of lines across CLI modules). AI-generated specs assume an idealized module structure, not actual code state. Presearch before writing prevents wasted review cycles and rejected specs.

Consequence: This blocks Gadfly/CTO review until presearch shows the feature gap is real.
