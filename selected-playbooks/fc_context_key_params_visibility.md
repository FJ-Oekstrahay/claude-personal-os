---
name: fc_context KEY_PARAMS visibility rule
description: _compress_fc_context only passes KEY_PARAMS values inline — any param not listed is invisible to the model
type: reference
---

## Rule

`cli/tool_output.py:_compress_fc_context` compresses FC config by section:
- Header lines (FC name, BF version) pass through
- For each `[section]`: outputs param count + only the params that appear in `KEY_PARAMS`
- Everything else becomes a count: `[profile_0] 12 params [p_roll=48, ...]`

**If a param is not in `KEY_PARAMS`, the model sees its section count but not its value.**

## What this means in practice

- Model says "I don't have that value" or asks the pilot to run `get <param>` → first check if it's in KEY_PARAMS
- A test fails because the model ignores an injected fc_context value → check if that param is in KEY_PARAMS
- When adding a new feature that depends on a param being visible to JARFACE → add it to KEY_PARAMS

## How to fix

In `cli/tool_output.py`, find the `KEY_PARAMS` set and add the missing param name (exact BF CLI name).

## What was missing (found 2026-04-16)

These were stripped and caused 4 eval failures:
- Yaw PIDs: `d_yaw`, `i_yaw`, `f_yaw`
- Rates: `roll_rate`, `pitch_rate`, `yaw_rate`, `yaw_expo`
- Filters: `dterm_lpf2_static_hz`, `gyro_lpf2_static_hz`
- Notch: `dyn_notch_q`, `dyn_notch_min_hz`, `dyn_notch_max_hz`, `dyn_notch_count`

## Quick check

```
cd /path/to/droneteleo
.venv/bin/python -c "
import sys; sys.path.insert(0, 'cli')
from tool_output import _compress_fc_context
# paste a sample fc_context and verify the param you care about appears
print(_compress_fc_context(ctx))
"
```
