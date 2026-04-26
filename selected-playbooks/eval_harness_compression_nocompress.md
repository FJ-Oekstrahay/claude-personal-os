---
name: Eval harness compression and no_compress field
description: _compress_fc_context strips non-k=v lines; adjrange label data lost; per-case override via no_compress YAML field
type: feedback
---

**Rule**: When test YAML fc_context contains adjrange label data or other non-key=value lines, add `no_compress: true` field to that test case. eval_harness.py checks for this field before applying context compression.

**Symptom**: adjrange label data in custom test fc_context gets dropped to "0 params" during eval. Regular test cases show full param count, custom test case shows minimal.

**Why**: `_compress_fc_context` in cli/tool_output.py was designed to strip noisy non-k=v lines for brevity, but adjrange section includes human-readable labels that carry semantic meaning ("Rate P1", etc). Compression loses them entirely.

**How to apply**: 
- Test YAML structure: add `no_compress: true` at the test case root level
- eval_harness.py checks `ctx.get('no_compress')` before compression
- Use when custom test context needs label data preserved for readability or for AGENT_SYSTEM validation
