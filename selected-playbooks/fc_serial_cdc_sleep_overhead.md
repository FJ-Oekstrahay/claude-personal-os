---
name: FC Serial CDC Sleep Overhead
description: Unconditional 0.5s sleep after serial close adds latency to every apply cycle; gate on send_exit only
type: playbook
---

# Serial Port CDC Reset Sleep in fc.py

## The Issue
After closing a serial connection to a flight controller, the code had an unconditional 0.5-second sleep:

```python
# Old: always sleeps, even when not needed
serial_port.close()
time.sleep(0.5)  # Wait for CDC reset on STM32
```

This sleep is necessary **only when the microcontroller is rebooting due to DTR toggle** (which happens on a clean exit via `send_exit=True`). But it was applied unconditionally, adding 0.5s latency to:
- Every config apply cycle
- Every dry-run simulation
- Every eval test case

For a 15-test harness, that's 7.5 seconds of wasted sleep per run.

## The Fix
Gate the sleep on the `send_exit` flag:

```python
# New: only sleep if we actually triggered a reboot
serial_port.close()
if send_exit:
    time.sleep(0.5)  # DTR toggle causes FC reboot; wait for CDC
```

The sleep is only needed when the code explicitly sent an exit command that triggers a DTR-based reboot. If you're just closing the port normally, the FC doesn't reboot, and the sleep is unnecessary.

## Where This Lives
- `cli/fc.py` — in the close/disconnect sequence

## Impact
- Apply cycle: 500ms → 0ms savings per apply
- Eval harness: 15 tests × 500ms = 7.5s savings per run
- Agent commands: noticeable snappier feedback

## Why This Matters
In interactive mode (dt agent), users perceive 0.5s delays as sluggish. In test automation, unconditional sleeps compound. Always measure your sleep assertions — if they're not load-bearing, remove them.

## Related
- Serial port behavior on STM32F7 microcontrollers
- DTR toggle → reboot pattern (CDC device behavior)
