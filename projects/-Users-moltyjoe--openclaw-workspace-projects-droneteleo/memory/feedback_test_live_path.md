---
name: Test live apply path
description: Scripted bench tests must include a non-dry-run live apply test; dry-run only is insufficient
type: feedback
originSessionId: 5df9e0ff-849f-479d-9e93-3f120e911f31
---
Never declare JARFACE "ready for interactive testing" based solely on dry-run scripted tests
and eval harness results. Both skip the FC apply path entirely.

**Why:** `run_jarface_test.py` hardcodes `--dry-run`, so `BetaflightCLI(port).open()` for
writing, `_apply_commands`, and `_verify_changes` are never called. Eval harness uses
FAKE_FC_CONTEXT — no FC at all. JARFACE failed its first live test because the apply path
had never been exercised.

**How to apply:** Before declaring an agent session ready for interactive testing:
1. A live (non-dry-run) scripted test must pass — applies at least one command and verifies it
2. The verify output ("All values verified.") must appear in the transcript
3. Session transcript log must exist in `logs/` for review

See `prompts-and-questions/17-fix-testing-gaps.md` for the implementation.
