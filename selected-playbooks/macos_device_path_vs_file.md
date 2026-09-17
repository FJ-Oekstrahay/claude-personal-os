---
name: macOS device paths pass os.path.exists()
description: On macOS, serial port device paths like /dev/cu.usbmodemXXXX pass os.path.exists() — always use os.path.isfile() when checking for regular files
type: feedback
keywords: os.path.exists, os.path.isfile, macos, serial port, device path, /dev/cu
---

## Problem

On macOS, `/dev/cu.usbmodemXXXX` (serial port device paths) pass `os.path.exists()` because they exist as character device files. Code that accepts either a file path or a port path as input will silently try to open the device as a text file, producing garbage or a decode error.

## Pattern (broken)

```python
if args.target and os.path.exists(args.target):
    with open(args.target) as f:   # BUG: opens /dev/cu.usbmodem14201 as text
        text = f.read()
```

## Fix

```python
if args.target and os.path.isfile(args.target):
    with open(args.target) as f:
        text = f.read()
else:
    # treat as port path or use auto-detect
    port = args.target or find_fc('seeker3')
```

## When to apply

Any CLI tool that accepts either a backup file path OR a serial port path as the same argument. Common in Droneteleo CLI tools (`analyze.py`, `agent.py`).
