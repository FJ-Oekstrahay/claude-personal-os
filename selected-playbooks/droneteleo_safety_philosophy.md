---
name: Droneteleo safety philosophy — guidance not gatekeeping
description: JARFACE should warn on unsafe param values, not block; Betaflight owns motor safety natively; don't add extra approval barriers
type: playbook
---

## Philosophy
JARFACE is a configuration companion, not a safety gate. Betaflight already implements its own safety systems:
- Motor enable toggle (prevents accidental arm)
- "I accept the risk" click-through dialogs on dangerous operations
- Multiple safety screens before firmware flashing
- Failsafe arming/disarming logic
- Motor protocol validation (PWM, DSHOT, BiDir, etc.)

Adding confirmations to JARFACE for PID range warnings creates a false sense of security and adds friction without additional safety value.

## Rule
**Don't block on configuration warnings; warn and proceed.**

Blocking confirmations are appropriate for:
- Failsafe/arming changes (in-flight behavior, no way to undo mid-air)
- Motor protocol changes (affects motor binding, hard to recover)
- Firmware operations (irreversible until next flash)

Blocking confirmations are **not** appropriate for:
- PID value ranges (conservative estimates, users often go outside them safely)
- Sensor calibration flags (can be re-run immediately if wrong)
- Display/serial rate settings (no motor impact)

**Why:** A user who has watched multiple YouTube videos on PID tuning and deliberately sets values outside stock ranges doesn't need a gatekeeping confirmation from an AI. The confirmation is annoying, not protective. If the values are bad, the motor test (props-off) will reveal it in seconds.

## How to apply

### For warnings that should be informational only
```python
# Bad: blocking confirmation
if pid_value > stock_max:
    confirm = input("PID out of range. Apply anyway? (y/n): ")
    if confirm != 'y':
        return

# Good: yellow warning panel, proceed
if pid_value > stock_max:
    warn_panel = Panel(f"⚠️  PID roll {pid_value} exceeds stock max {stock_max}",
                       style="yellow")
    display.print(warn_panel)
    # Apply the value anyway
    apply_pid(pid_value)
```

### For confirmations that stay
Failsafe, motor protocol, and firmware changes should still confirm (separate secondary gates):
```python
if is_failsafe_change(old, new) or is_motor_protocol_change(old, new):
    warn_panel = Panel("⚠️  This affects in-flight behavior", style="red")
    display.print(warn_panel)
    confirm = input("Confirm? (y/n): ")
    if confirm != 'y':
        return
```

## Related
- `betaflight_cli_motor_testing.md` — how to verify changes safely with props-off motor test
- `reference_fpv_betaflight.md` — PID tuning reference values by frame
