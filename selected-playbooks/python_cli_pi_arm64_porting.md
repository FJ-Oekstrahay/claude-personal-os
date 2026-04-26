---
type: playbook
title: Python CLI Porting to Raspberry Pi ARM64
description: Python CLI tools using pyserial, rich, requests run on Pi ARM64 with zero code changes; USB serial enumerates as /dev/ttyACM0
agents: [bob, gerbilcheeks]
tags: [python, raspberry pi, arm64, serial port, cli, porting, deployment]
updated: 2026-04-12
---

## Goal
Clarify the expectation when porting a standard Python CLI (using common libraries like pyserial, rich, requests) to Raspberry Pi ARM64. The answer: **no code changes needed**.

## Quick Summary
If a Python CLI runs on macOS or Linux x86 using:
- `pyserial` for serial port access
- `rich` for terminal formatting
- `requests` for HTTP
- Standard library (os, json, argparse, etc.)

Then it will run unmodified on **Raspberry Pi 5 ARM64** (or Pi 4 ARMv8, though Pi 4 is 32-bit by default).

**Only setup required:** Add user to `dialout` group for serial port access.

## Porting Checklist

- [ ] **Dependencies install cleanly:** Run `pip install -r requirements.txt` on Pi. Most pure-Python packages have ARM64 wheels; compiled packages (e.g., `cryptography`) usually do too.
- [ ] **Serial port enumerates correctly:** USB serial devices appear as `/dev/ttyACM0` (not `/dev/cu.usbmodemXXXX` like macOS). Code using device path heuristics may need adjustment.
- [ ] **User can access serial port:** Add user to `dialout` group: `sudo usermod -a -G dialout $USER`. Logout/login required.
- [ ] **No hardcoded absolute paths:** If code references `/Users/...` or `C:\...`, use `pathlib.Path.home()` or `expanduser()` instead.
- [ ] **Temporary files:** Use `tempfile` module or `/tmp` (not Windows-specific temp paths).

## Common Changes (Rarely Needed)

| Issue | Trigger | Fix |
|---|---|---|
| Serial port path | Code assumes `/dev/cu.*` (macOS) or `COM*` (Windows) | Use `serial.tools.list_ports.comports()` or accept device path as argument |
| Platform-specific temp | Code hardcodes `C:\Temp` or `~/temp` | Use `tempfile.gettempdir()` or `pathlib.Path.home() / "temp"` |
| File permissions | Scripts not executable | `chmod +x script.py` once on Pi; no code change |
| Clock/timezone | Time-based operations diverge | Only relevant if Pi clock is wrong; fix system time |

## Device Path Gotcha

**On macOS:** `/dev/cu.usbmodem14201`, `/dev/tty.usbmodem14201`
**On Pi (Linux):** `/dev/ttyACM0`

If code tries to detect the device path automatically, use `serial.tools.list_ports.comports()` instead of hardcoding or glob patterns:

```python
from serial.tools import list_ports

def find_fc_port():
    for port, desc, hwid in list_ports.comports():
        if 'STM32' in hwid or 'Betaflight' in desc:
            return port
    return None
```

## Dependencies: What Works

These all have reliable ARM64 wheels or pure-Python implementations:
- `pyserial` ✓
- `rich` ✓
- `requests` ✓
- `pyyaml` ✓
- `click` ✓
- `pydantic` ✓
- `aiohttp` ✓

**Compiled packages** (cryptography, numpy, pandas) also have pre-built ARM64 wheels since ~2021; installation is fast.

**Gotcha:** `python-multipart` on some systems requires compilation. Usually fine on modern Pi OS; if it fails, try `pip install --only-binary :all: python-multipart` or just use native form parsing.

## Testing Locally (Before Deploying to Pi)

If you don't have a Pi handy:
1. Use Docker with `--platform linux/arm64` to test the build
2. Or just trust the checklist above — the odds of hidden ARM64 issues are very low for standard CLI tools

```bash
docker run --rm --platform linux/arm64 python:3.11-slim bash -c "pip install -r requirements.txt && python cli.py --help"
```

## When to Worry About ARM64 Compatibility

Most issues are **environmental**, not architectural:
- Missing `dialout` group membership (serial access)
- File paths hardcoded for macOS/Windows
- Clock skew (if Pi clock is wrong)
- Storage I/O slower on SD card (not ARM64 issue, but noticeable)

**Actual ARM64 incompatibilities are rare** in pure-Python + standard-wheel packages.

## Related Playbooks
- [[serial_port_contention]] — if the Pi CLI is sharing a serial port with other processes
- [[serial_delimiter_false_positives]] — if the CLI reads serial data and uses delimiters
- [[low_touch_mode]] — autonomous Pi deployments (CLI runs unattended)

## Standing Expectation
When porting a Python CLI from macOS/Linux x86 to Pi ARM64: **expect zero code changes for business logic**. Budget 15–30 min for environment setup (dialout group, file paths, testing), not for porting effort.
