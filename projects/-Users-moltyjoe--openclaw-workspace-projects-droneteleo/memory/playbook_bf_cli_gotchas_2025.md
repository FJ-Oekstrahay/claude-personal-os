---
name: Betaflight CLI Gotchas — BF 2025.12.2
description: Commands that behave differently or fail in BF 2025.12.2 vs older versions; serial port handling after save/reboot
type: project
originSessionId: 0ffe1c8f-3e75-44df-b82b-e4880308157d
---
## BF 2025.12.2 CLI Gotchas

### Parameter renames
- `motor_direction` — INVALID in 2025.12.2. Renamed; `get motor_direction` returns error.
- `gyro_1_align` — INVALID. Use sensor alignment via board_align instead.
- `gyro_align` — INVALID. Same.

### `acc_calibration` is a command, not a readable value
- `get acc_calibration` → shows current offsets (safe)
- `acc_calibration` (bare, no `get`) → **immediately starts a live calibration sequence**
- If drone is not flat/still when this runs, you write bad cal data
- Always use `get acc_calibration` to inspect; use bare `acc_calibration` only when drone is flat and explicitly ready

### Serial port disconnects after `save`
- `save` in BF CLI triggers an immediate FC reboot
- The serial port (e.g. `/dev/cu.usbmodem*`) disappears mid-script
- Any `read_all()` or `in_waiting` call after `save` raises `OSError: [Errno 6] Device not configured`
- Fix: close the serial object before `save` output is read, sleep ~5s, then open a new Serial connection
- Do NOT use `exit` for this — `exit` also reboots but `save` is more abrupt

### `resource list` / `resource motor` syntax changed
- These commands fail in 2025.12.2; syntax differs from older BF

### `diff gyro` output is long
- Can overflow a fixed read timeout — use longer sleep (1.5s+) or read until prompt

## Board Alignment Fix Pattern
When 3D model in Setup tab doesn't match physical movement:
1. Identify which axes are correct/reversed/swapped by moving the drone
2. Compute board_align offset (see below)
3. Set via CLI: `set align_board_roll = X`, `set align_board_pitch = Y`, `set align_board_yaw = Z`
4. `save` — port will die, wait 5s, reconnect
5. Verify with `get align_board_roll` etc.
6. Redo accel calibration (axes changed)

### Common symptom → fix mapping
| Roll | Pitch | Yaw | Fix |
|------|-------|-----|-----|
| correct | reversed | reversed | `align_board_roll = 180` |
| reversed | correct | reversed | `align_board_pitch = 180` |
| reversed | reversed | correct | `align_board_yaw = 180` |
| reversed | correct | correct | `align_board_yaw = 90` or 270 (needs testing) |

**Why:** Roll correct + pitch reversed + yaw reversed = 180° rotation around the roll axis (FC physically flipped/rotated around nose-tail axis in the stack).

## adjrange — function IDs and channel indexing (BF 2025.12.2)

### Function IDs (verified empirically on HAKRCF722V2 / BF 2025.12.2)
- fn=3 = `thr_expo` (throttle expo) — confirmed by wheel test
- fn=8 = `pitch_roll_d` (D-term roll+pitch combined) — assumed correct per radio.py; verify by wheel test
- fn=12 = `rate_profile` selector

### adjrange channel field is 0-indexed from AUX1
- Field 7 (adj_ch): 0=AUX1, 1=AUX2, 2=AUX3, 3=AUX4, 4=AUX5, 5=AUX6
- Field 3 (range_ch): same indexing

### RATE_PROFILE (fn=12) selection behavior
- Both adjrange entries must use the SAME adj_ch (the switch channel, e.g. AUX4=3)
- Profile is chosen proportionally from adj_ch PWM: low (~1000) → profile 0, high (~2000) → profile max
- With 3 accessible profiles: AUX4 high → profile 2 (not 3 — never reaches index 3 due to floor arithmetic)
- `adj_min=0, adj_max=0` = step/select mode (proportional); non-zero adj_min/adj_max = range mode
- DO NOT use different adj_ch values in the two entries — causes one switch position to lock to wrong profile
- value=4 wraps to profile 0 (do not use)

### `get name` ambiguity
- `get name` matches both `rateprofile_name` and `profile_name` — returns both
- To set PID profile name: `set profile_name = <name>` (not `set name`)
- Max 8 chars for profile_name

## Accel Calibration Procedure
- `acc_calibration` (bare command) is **NOT a valid CLI command in BF 2025.12.2** — returns "UNKNOWN COMMAND"
- `get acc_calibration` works and shows stored offsets (safe, read-only)
- To actually calibrate: use BF Configurator → Setup tab → "Calibrate Accelerometer" button
- Calibration offsets are in sensor frame, not body frame — changing `board_align` does NOT invalidate stored cal values; only recalibrate if the sensor chip physically moved relative to the FC board
