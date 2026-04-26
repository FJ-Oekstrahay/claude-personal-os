---
name: Python Global Flags in Async Functions
description: Global keyword required when modifying module-level flags inside nested async functions
type: reference
---

# Python Global Flags in Async Functions

## The gotcha
When you define module-level flags and modify them inside nested async functions (e.g., callbacks within FastAPI route handlers), Python treats them as local variables unless you explicitly declare them `global`.

```python
# Module level
_active_call = False

@app.post("/call")
async def start_call():
    _active_call = True  # ❌ Creates a LOCAL variable, doesn't modify module-level
    
# Later, _active_call is still False
```

## Solution
Use the `global` keyword in each function that modifies the flag:

```python
_active_call = False
_callback_pending = False

@app.post("/call")
async def start_call():
    global _active_call
    _active_call = True  # ✅ Correctly modifies module-level
    
@app.post("/callback")
async def handle_callback():
    global _callback_pending
    _callback_pending = True  # ✅ Correctly modifies module-level
```

## Why separate flags?
Don't combine state into one flag if the conditions are independent. In the prior auth bot:
- `_active_call`: True while a test call is in progress
- `_callback_pending`: True while waiting for an inbound callback (may happen during an active call)

They have different lifespans and can overlap, so they need separate tracking.

## Related
- Prior auth bot inbound callback: `/Users/moltyjoe/.openclaw/workspace/memory/playbooks/prior_auth_test_call.md`
