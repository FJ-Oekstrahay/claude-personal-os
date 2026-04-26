---
name: --dev-volume Flag Pattern for Hardware-Independent Testing
description: Testing hardware-dependent CLI commands without physical hardware; local path substitution
type: feedback
---

## The Pattern

Hardware-dependent commands (SD card access, serial port operations, USB device detection) are hard to test without the actual hardware. The `--dev-volume PATH` pattern lets you substitute a local filesystem path for the hardware interface, enabling offline testing and CI/CD validation.

## When to Use

- Testing SD card read/write operations without a flight controller
- Testing USB mass storage discovery without physical radio/FC
- Testing volume detection logic (mount paths, free space checks)
- Offline validation of config/log file operations
- CI/CD pipelines where hardware isn't available

## Implementation Pattern

```python
import argparse
import os

parser = argparse.ArgumentParser()
parser.add_argument('--dev-volume', type=str, default=None,
                    help='(TEST) Use local path instead of actual USB/SD volume')
args = parser.parse_args()

def get_working_volume():
    """Return either the test path or the actual hardware volume."""
    if args.dev_volume:
        # Test mode: use local path
        os.makedirs(args.dev_volume, exist_ok=True)
        return args.dev_volume
    
    # Normal mode: detect actual USB/SD volume
    return detect_msc_volume_on_hardware()

# All subsequent code uses get_working_volume() and is agnostic to whether
# it's a real USB mount or a test directory.
volume = get_working_volume()
for logfile in os.listdir(volume):
    process_log(os.path.join(volume, logfile))
```

## Test Setup

```bash
# Create a test structure before running the command
mkdir -p /tmp/test_fc_volume/logs
cp sample_blackbox.bbl /tmp/test_fc_volume/logs/

# Run the CLI command against the test volume
python cli/fc.py seeker3 --dev-volume /tmp/test_fc_volume --extract-logs

# Verify output
ls -la /tmp/test_fc_volume/logs/
```

## Benefits

1. **Speed:** No USB enumeration, mount delays, or physical reconnection
2. **Repeatability:** Same test files every time; no state carryover
3. **CI/CD compatible:** No hardware required in test runners
4. **Debugging:** Easy to inject edge cases (empty volumes, corrupted files, symlinks)
5. **Safety:** Test code that deletes files without risk of actual data loss

## Notes

- **Flag naming:** Use `--dev-volume` (not `--test-mode` or `--mock`) so it's clear this is a development/test override
- **Path validation:** Ensure the path exists and is writable before dereferencing
- **Error handling:** Same error paths should work in both modes (missing files, permission errors, etc.)
- **Don't ship it:** This flag is development-only; document it as such in help text
