---
name: Python venv requirement for YAML parsing
description: .venv/bin/python vs system python3; PyYAML block scalars fail silently with system Python
type: feedback
---

**Rule**: Run droneteleo eval harness with `.venv/bin/python`, not system `python3`. System Python has no PyYAML installed and silently breaks YAML block scalar parsing.

**Symptom**: `fc_context` loads as literal `'|'` string instead of multiline content. Tests appear to pass but context is corrupted.

**Why**: venv isolation ensures all dependencies (PyYAML, rich, pyyaml) are present. System Python on macOS may have stale or missing packages. Silence makes this particularly tricky to debug.

**How to apply**: When running eval_harness.py or any test that parses YAML, explicitly use `.venv/bin/python`. Add to droneteleo CLI wrapper if not already present.
