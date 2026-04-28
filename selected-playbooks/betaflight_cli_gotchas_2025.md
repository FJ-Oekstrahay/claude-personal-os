---
name: Betaflight CLI Gotchas 2025.12.2
description: Parameter name changes, acc_calibration behavior, and port management in BF 2025.12.2
type: reference
---

# Betaflight CLI Gotchas (2025.12.2)

## Renamed parameters

BF 2025.12.2 renamed several parameters from earlier versions. If a param is not found in CLI, check if it has been renamed.

**Common renames:**
- (To be documented as discovered)

**Why:** Firmware parameter names evolve; historical scripts break against new versions.

**How to apply:** When setting a param fails with "unknown parameter", check the current `dump all` output or BF Configurator source to find the new name.

## acc_calibration triggers live calibration sequence

Running `acc_calibration` in CLI immediately triggers the accelerometer calibration process — the FC starts the sequence and will not accept further commands until complete.

**Gotcha:** If you're scripting or expecting to queue multiple commands, acc_calibration blocks the serial connection until calibration finishes (typically 5-10 seconds).

**Why:** This is by design — Betaflight treats acc_calibration as an immediate action, not a configuration parameter.

**How to apply:** Only run acc_calibration when the drone is on a level surface with no props. Run it in isolation; don't pipeline other commands after it without a wait/timeout.

## save command kills the serial port

Issuing `save` in Betaflight CLI causes an immediate serial port reconnect. The port goes unavailable briefly (typically 1-3 seconds) as the FC reboots to persist config.

**Gotcha:** If you issue `save` and then immediately send another command without waiting for port reconnect, the second command hangs or times out.

**Why:** Betaflight reboots the FC on save to ensure clean EEPROM persistence.

**How to apply:** After `save`, implement exponential backoff retry logic or a fixed ~3-second wait before sending additional commands. See `betaflight_serial_reconnect_timeout.md` for detailed patterns.

## Constraining adjrange values at firmware level doesn't work (2025.12.2)

adj_min/adj_max values are stored and displayed in `adjrange` output, but BF 2025.12.2 **ignores them** for certain functions (pitch_roll_i/function 7, others TBD). The parameter's hard limit (0-200 for pitch_roll_i) is always enforced instead.

**Workaround:** Enforce range constraints at the radio/mixer level using EdgeTX weight/offset on the encoder channel (e.g., P1 potentiometer).

**Why:** This is a firmware regression/bug in 2025.12.2. Earlier versions (4.4.3) honored adj_min/adj_max.

**How to apply:** Use radio.py `radio apply-range` subcommand to document intent (patches FC config, saves, verifies) but know that the actual enforcement must happen in the radio mixer. See `betaflight_adjrange_radio_binding.md` for the radio mixer workaround.

## References

- `betaflight_dji_msp.md` — firmware version compatibility notes
- `betaflight_serial_reconnect_timeout.md` — handling port unavailability after reboot
- `betaflight_adjrange_radio_binding.md` — adjrange limitations and radio enforcement patterns
