---
name: EdgeTX Radio Battery-Low Alert Setup
description: Configuring transmitter battery low-voltage alerts on Radiomaster Pocket; battery calibration requirement; YAML auto-apply gotchas
type: reference
---

# EdgeTX Radio Battery-Low Alert Setup

## Overview

The `dt radio battery-alert` CLI command configures a transmitter battery low-voltage alert in EdgeTX. It exists in `cli/radio.py` (lines 370-611) and handles both connected and disconnected radio cases.

## Prerequisites: Battery Calibration (Critical)

Before setting up the alert, **you must calibrate the battery voltage in the radio**:

1. Connect the radio
2. Go to **RADIO SETUP → Battery Calibration**
3. Run the calibration procedure

**Why:** Without calibration, the threshold will fire at the wrong voltage. A calibrated battery allows EdgeTX to accurately measure and report cell voltage.

**How to apply:** Always run battery calibration before `dt radio battery-alert`. If alerts fire at unexpected voltages, recalibrate.

## Radiomaster Pocket Defaults

The Radiomaster Pocket is a 2S battery radio (two cells in series). Defaults for the CLI command are:

```
--cells 2          # 2S battery
--threshold 3.5    # Alert fires at ≤3.5V per cell (7.0V total for 2S)
```

These are appropriate for the Pocket. Adjust only if using a different cell count or voltage curve.

## CLI Command: dt radio battery-alert

```bash
dt radio battery-alert [--cells CELLS] [--threshold VOLTS]
```

The command creates a logical switch with a low-battery condition and attaches it to the audio alert system.

### Connected Radio

When the radio is connected, the command:
1. Reads the current EdgeTX config via the serial protocol
2. Adds/updates the battery-alert logical switch entry
3. Writes the config back to the radio
4. Verifies the change took effect

### Disconnected Radio (YAML auto-apply)

When the radio is not connected, the command:
1. Reads the profile YAML file (e.g., `~/.openclaw/workspace/projects/droneteleo/profiles/radiomaster_pocket.yaml`)
2. Adds/patches the logical switch entry
3. Writes the YAML back to disk

**Gotcha:** The YAML auto-apply path encoding is unverified on live hardware. The command patches `v1: 'Tx Batt'` into a logicalSw entry, but this encoding has never been tested by connecting a radio after a YAML-only patch.

**How to apply:** After applying via YAML, verify the setting was accepted when you next connect the radio in person. Check RADIO SETUP → Logical Switches to confirm the entry exists.

## Logical Switch Structure

The battery-alert logical switch uses:
- **Source:** Tx voltage (`Tx Batt`)
- **Function:** Less than or equal (`≤`)
- **Value:** Threshold in volts (e.g., 3.5 for 2S)
- **Output:** Attached to audio alert

When Tx voltage drops to or below the threshold, an audio cue sounds to alert you to low battery.

## References

- `dt radio` command suite: `cli/radio.py` lines 370-611
- `radio_edgetx_config_generation.md` — EdgeTX YAML schema and model config generation
- `betaflight_adjrange_radio_binding.md` — other radio logical switch patterns
