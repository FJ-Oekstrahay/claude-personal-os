---
name: Betaflight Blackbox Pull Modes (Flash vs SD Card)
description: Distinguishing blackbox retrieval between SD-card-based FCs (MSC mode) and flash-based FCs (serial download); when droneteleo blackbox pull fails
type: playbook
---

# Betaflight Blackbox Pull Modes

## The Distinction

Flight controllers store blackbox logs in two places depending on hardware:

- **SD card–based FCs** (most 5" builds, some 3" freestyle): Use USB mass storage class (MSC) mode; blackbox data is on physical SD card.
- **Flash-based FCs** (compact builds like Seeker3 3"): Blackbox logs stored in onboard 16MB flash storage; MSC mode not applicable.

The droneteleo `blackbox pull` command assumes SD card + MSC mount. Flash-based FCs need a different retrieval method.

## How to Detect

Check the FC hardware in `hardware_inventory.md` or inspect in Betaflight Configurator:

1. Open Blackbox tab in BF Configurator
2. Look for SD card indicator or "Device" field:
   - "SD Card" or "Removable Media" → SD-based; use MSC
   - "Device Flash" or "Internal Flash" → Flash-based; use `blackbox download`

## Flash-Based FC Retrieval: BF CLI `blackbox download`

**Betaflight CLI command** (over serial connection):

```bash
# List available logs
python cli/fc.py <fc_name> --exec "blackbox"

# Download specific log by index
python cli/fc.py <fc_name> --exec "blackbox download 0"
```

The output streams the binary log data to stdout. Capture it to a file:

```bash
python cli/fc.py <fc_name> --exec "blackbox download 0" > log_0001.bbl
```

**Gotchas:**

- Serial connection must remain open during download (no MSC reboot).
- Large logs may take 10–30 seconds depending on baud rate (typically 115200).
- After download, optionally erase via `blackbox erase <index>` to free flash space.

## SD-Based FC Retrieval: MSC Mode (Existing Pattern)

Documented in `betaflight_msc_mode_sd_card.md`. Quick summary:

```bash
# Trigger MSC mode (FC reboots)
python cli/fc.py <fc_name> --exec "msc"

# Wait for /Volumes/<sd-card-name> to appear
# Copy *.bbl files from LOGS directory
# Eject and FC reboots back to normal
```

## How to Apply

When implementing `blackbox pull` in droneteleo:

1. **Detect storage type** — read FC hardware profile or Betaflight config
2. **Route to correct method:**
   - Flash-based → use `blackbox download <index>` over serial
   - SD-based → use MSC mount + file copy

**Example branching logic:**

```python
if fc_has_sd_card:
    # Existing MSC mode flow
    msc_volume = get_msc_volume()
    copy_blackbox_logs(msc_volume)
else:
    # Flash-based flow
    for log_idx in range(num_logs):
        download_via_blackbox_cmd(fc_name, log_idx)
```

## Storage Capacity Reference

| Type | Capacity | Typical Logs | Notes |
|------|----------|-------------|-------|
| SD Card | 4–128 GB | Hundreds | Common on 5" freestyle |
| 16MB Flash | 16 MB | 2–5 logs | Seeker3, compact 3" freestyle |

## Related

- `betaflight_msc_mode_sd_card.md` — MSC mode implementation for SD-based FCs
- `hardware_inventory.md` — FC inventory with storage type marked
- `reference_fpv_betaflight.md` — Seeker3 hardware details
