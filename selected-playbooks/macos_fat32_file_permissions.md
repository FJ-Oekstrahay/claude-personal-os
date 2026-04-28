---
name: macOS FAT32 File Permissions and shutil.copy2
description: Handling user-immutable flags copied from FAT32 volumes; EPERM errors on re-pull
type: feedback
---

## The Problem

When copying files from FAT32 volumes (e.g., SD card reader on macOS), the OS stamps files with the user-immutable BSD flag (`uchg`). Using `shutil.copy2()` propagates this flag to the destination, making the destination immutable. Subsequent re-pulls to overwrite fail with `EPERM: operation not permitted`.

## Why This Matters

**Why:** macOS treats FAT32 as a special case and applies the uchg flag as a safety mechanism, but this breaks CI/CD workflows, automated re-pulls, and iterative file updates where the destination must be overwritable.

**How to apply:** Whenever pulling/copying files from external or removable storage (SD cards, USB drives, FAT32 partitions) into a repo or working directory, use explicit file operations instead of `shutil.copy2()`.

## Solution Pattern

```python
import shutil
import os

def safe_copy_from_fat32(src, dest):
    """Copy a file from FAT32, stripping immutable flags on destination."""
    # If destination exists, remove the immutable flag and delete it
    if os.path.exists(dest) or os.path.islink(dest):
        try:
            os.chflags(dest, 0)  # Clear all BSD flags
        except (OSError, AttributeError):
            pass  # Not on macOS or flag already clear
        os.remove(dest)
    
    # Use copyfile (no metadata copy) instead of copy2
    shutil.copyfile(src, dest)
    
    # Explicitly set modification time
    stat = os.stat(src)
    os.utime(dest, (stat.st_atime, stat.st_mtime))
    
    # Ensure destination is writable
    try:
        os.chflags(dest, 0)  # Clear any flags inherited from source
    except (OSError, AttributeError):
        pass
```

### Key Differences from `shutil.copy2()`
- **`shutil.copyfile()` only copies file content**, not permissions, times, or flags
- **Explicit `os.utime()`** restores modification time without propagating uchg flag
- **Pre-emptive `os.chflags(dest, 0)`** clears flags before overwriting
- **Platform-safe** — the try/except catches non-macOS platforms where `os.chflags` doesn't exist

### When to Use
- Copying blackbox logs from SD card reader
- Pulling flight controller firmware/config from external storage
- Any automated re-pull workflow where idempotency matters
