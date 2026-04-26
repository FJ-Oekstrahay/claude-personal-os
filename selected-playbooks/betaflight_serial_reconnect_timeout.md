---
name: Betaflight serial port reconnect timeout
description: Serial port disappears after disconnect; FC reboots on exit + DTR toggle; retry with backoff is the fix
type: playbook
---

## Problem
When BetaFlight CLI exits, the FC performs a hardware reboot triggered by the DTR (Data Terminal Ready) signal toggle. During this ~2-3 second window, the serial port device vanishes from the OS and is unavailable.

Attempting an immediate reconnect will fail with "port not found" or "permission denied."

## Why
- `exit` command in BF CLI sends a disconnect message
- DTR signal toggle on close triggers a hardware reset on the FC
- During reset, the UART isn't enumerated — the `/dev/tty*` device disappears
- OS re-enumerates the device after reset completes (~2-3 seconds)

## How to apply
When writing code that connects → executes → disconnects → reconnects to the same FC in sequence:

1. **Wrap reconnect in retry loop** with exponential backoff (50ms → 100ms → 200ms, max 3-5 attempts)
2. **Check port existence** before attempting open: `if not port in get_ports(): continue`
3. **Catch connection exceptions** explicitly and feed into backoff (don't assume instant failure means permanent failure)
4. **Avoid `pkill`-style force termination** — let the `exit` command run cleanly so the DTR toggle actually happens
5. **For multi-step workflows** (backup → config → reboot → verify), use a connection manager that auto-retries on known transient port errors

## Code pattern
```python
import time
from serial.tools.list_ports import comports

def connect_with_backoff(port, attempts=5, initial_delay_ms=50):
    for attempt in range(attempts):
        try:
            conn = serial.Serial(port, timeout=1)
            return conn
        except (serial.SerialException, FileNotFoundError):
            if attempt < attempts - 1:
                delay = initial_delay_ms * (2 ** attempt) / 1000.0
                time.sleep(delay)
            else:
                raise

def is_port_available(port):
    return any(p.device == port for p in comports())
```

## Related
- `serial_port_contention.md` — general serial port conflict patterns
- `betaflight_cli_gotchas_2025.md` — other FC/CLI quirks (acc_calibration, board_align, etc.)
