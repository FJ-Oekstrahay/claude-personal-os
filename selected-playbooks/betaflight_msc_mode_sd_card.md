---
name: Betaflight CLI MSC Mode and SD Card Access
description: Using BF CLI msc command to mount FC SD card as USB mass storage; volume detection on macOS
type: feedback
---

## The Pattern

Betaflight firmware supports USB mass storage class (MSC) mode via the CLI `msc` command. This is useful for:
- Direct SD card access without GUI
- Automated blackbox log retrieval
- Batch firmware/config file operations

The FC reboots into MSC mode when the command executes — no Betaflight Configurator needed.

## How It Works

1. **Trigger MSC mode:**
   ```bash
   python cli/fc.py <fc_name> --exec "msc"
   ```

2. **FC behavior:** The flight controller reboots into USB mass storage mode and the serial connection closes.

3. **Mount detection (macOS):** The SD card appears as a new volume under `/Volumes/`.

## Volume Detection Pattern

```python
import os
import time
import subprocess

def get_msc_volume(timeout_sec=10):
    """Poll /Volumes for a new mount after msc command."""
    volumes_before = set(os.listdir('/Volumes'))
    
    # Command already sent; FC is rebooting
    start = time.time()
    while time.time() - start < timeout_sec:
        volumes_now = set(os.listdir('/Volumes'))
        new_volumes = volumes_now - volumes_before
        
        # Filter out common system volumes
        msc_candidates = [v for v in new_volumes 
                         if v not in ('Macintosh HD', 'System Reserved')]
        
        if msc_candidates:
            return f'/Volumes/{msc_candidates[0]}'
        
        time.sleep(0.5)
    
    raise TimeoutError(f"MSC volume not mounted within {timeout_sec}s")

# Usage:
path = get_msc_volume()
print(f"SD card mounted at: {path}")
# Now iterate blackbox files, copy configs, etc.
```

## Exit Pattern

To reboot the FC back to normal mode:
1. Eject the volume: `diskutil eject /Volumes/<name>` (macOS) or `umount /media/...` (Linux)
2. FC reboots automatically when USB is released
3. Reconnect to serial port and resume normal CLI/configurator operations

## Notes

- **USB mass storage is read-write.** Be careful with concurrent access to avoid corruption.
- **No serial connection while in MSC mode.** The serial interface is disabled during USB mass storage.
- **Timeout is typically 2-5 seconds** from `msc` command to full mount on most systems.
- **Volume name varies** — use snapshot-before pattern if name detection is critical.

## When NOT to Use

- Betaflight Configurator doesn't use MSC mode; use the SD card button in the GUI if you need GUI-based file access.
- Don't use MSC mode in parallel with CLI connections (they're exclusive).
