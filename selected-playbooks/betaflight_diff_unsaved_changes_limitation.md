---
name: BetaFlight diff limitation with unsaved changes
description: Diff doesn't work for detecting RAM-only changes because FC reboots on disconnect, losing RAM state
type: playbook
---

## Problem
When comparing BetaFlight configurations before and after a session, a `diff` command may fail to detect changes that were applied but never explicitly `save`'d to EEPROM.

This is a common workflow:
1. Connect to FC
2. Apply PID changes, feature flags, serial settings
3. Motor test to verify behavior
4. Disconnect
5. Later: re-connect and run `diff` expecting to see the changes
6. Result: `diff` shows "No changes" even though we know changes were applied

## Why
BetaFlight stores configuration in two places:
- **RAM** — working copy, fast read/write, lost on power cycle or reboot
- **EEPROM** — persistent, requires explicit `save` to update

When the CLI connection closes:
1. The `exit` command is sent
2. FC performs a hardware reboot (DTR toggle resets the board)
3. FC boots with EEPROM contents (the last saved state)
4. Any changes that were in RAM are **discarded**

The `diff` command compares the current EEPROM state against the last known good backup. If those changes were never saved to EEPROM, there's nothing to diff against.

## How to apply

### When applying config changes
1. **Always `save` before disconnecting** if you want those changes to persist
   ```
   > set pid_roll = 35
   > save
   ```
2. **Motor testing** can be done without saving (safer — if the quad flips, reboot clears bad settings)
3. If you're testing non-destructive settings (display, serial rates), you can skip save; understanding this is temporary

### When comparing configs
1. **`diff` is for saved state only** — it checks EEPROM vs. backup, not RAM vs. backup
2. **Don't use `diff` to verify temporary changes** — the changes are gone after disconnect/reboot
3. Use **before/after dumps** if you need to verify transient RAM state:
   ```
   > feature
   > get [setting name]
   ```
   Then screenshot or log before/after, compare manually.

### Workflow recommendation
```
[Connect] → [Make changes] → [Motor test on RAM] → [Reboot to verify safe defaults]
           ↓
      [Reboot with props off, verify nothing bad stuck]
           ↓
      [If good, reconnect] → [Reapply changes] → [SAVE] → [Disconnect]
           ↓
      [Later: diff all] — now changes are permanent
```

## Related
- `betaflight_cli_motor_testing.md` — motor test workflow (changes don't need to be saved)
- `betaflight_serial_reconnect_timeout.md` — why the reboot happens on disconnect
