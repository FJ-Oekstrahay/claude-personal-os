---
name: dt Agent FC Detection Pattern
description: FC lookup requires explicit None argument; hardcoded defaults silently fail on multi-FC systems
type: playbook
---

# FC Detection in dt agent

## The Issue
When calling `find_fc()` in `cli/fc.py`, the function signature is:
```python
def find_fc(serial_port=None, model=None)
```

If you call `find_fc()` or `find_fc(model=None)` expecting it to scan hardware inventory, **it will fail silently and return the wrong FC** because:
- The function has internal defaults that hardcode specific models (e.g., QAV → seeker3)
- These defaults are only meant for test isolation
- Production code must explicitly pass `None` to trigger hardware scanning

## The Fix
Always call: `find_fc(None)` or `find_fc(serial_port=None)` when you need real hardware detection.

Correct usage:
```python
fc = find_fc(None)  # Scans hardware inventory
```

Incorrect usage:
```python
fc = find_fc()      # Uses internal test defaults (wrong!)
fc = find_fc(model=None)  # Same as above (wrong!)
```

## Why This Matters
The dt agent runs against real FCs. If FC detection uses hardcoded defaults instead of hardware scanning, the agent will:
- Write config to the wrong FC model
- Produce eval results against stale test fixtures, not actual hardware
- Give silent false negatives (test passes but doesn't measure anything)

**Always read the call site and hardware inventory before running eval.** Don't trust that a passing test actually ran against the right hardware.

## Related
- `cli/fc.py` — find_fc() implementation
- `playbook_hardware_accuracy_rule` — always verify hardware before naming models
