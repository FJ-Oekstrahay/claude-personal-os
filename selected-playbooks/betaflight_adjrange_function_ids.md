---
name: Betaflight adjrange function IDs and profile commands
description: Function ID mappings (HAKRCF722V2, BF 2025.12.2), profile naming command, and adj_channel indexing for adjrange configuration
type: reference
---

# Betaflight adjrange Function IDs and Profile Commands

## Function ID mappings (BF 2025.12.2, HAKRCF722V2)

Confirmed function IDs in `adjrange` commands on Betaflight 2025.12.2:

| Function ID | Name | Parameter Controlled |
|---|---|---|
| 3 | thr_expo | Throttle expo |
| 8 | pitch_roll_d | Pitch/roll D term |
| 12 | rate_profile | Rate profile selection |

Other function IDs exist (pitch_roll_p, pitch_roll_i, etc.) but the above are the ones confirmed in live testing.

**Why:** Betaflight 2025.12.2 has 4 PID profiles (not 3), and function IDs map to firmware-internal enums that change between versions.

**How to apply:** When writing adjrange commands, use the function ID that corresponds to the parameter you want to adjust. Always verify with `adjrange` (no args) in CLI to see current mappings on your FC.

## Rate profile selection via adj_channel

**The 7th field in adjrange is adj_channel (0-indexed from AUX1), NOT a profile index.**

Example (correct — Seeker3 using AUX4 shoulder switch):
```
adjrange 0 0 3 900 1300 12 3 0 0   # range_ch=AUX4, fn=12, adj_ch=AUX4 (index 3), low PWM→profile 0
adjrange 1 0 3 1700 2100 12 3 0 0  # range_ch=AUX4, fn=12, adj_ch=AUX4 (index 3), high PWM→profile 2
```
Format: `adjrange <slot> 0 <range_ch> <start> <end> <fn> <adj_ch> [adj_min] [adj_max]`

Profile selection is **proportional** based on PWM value of the adj_ch channel:
- Low PWM (~1000) → profile 0
- Mid PWM (~1500) → profile 1 or 2 (depending on available profiles)
- High PWM (~2000) → highest reachable profile

**For a 2-position switch:** Both adjrange entries must point adj_ch at the same switch channel. The switch's PWM output determines which profile is active.

**Why:** Betaflight uses a single analog/PWM axis (the adj_ch) to select between 1-4 profiles. If you have a 2-position switch sending to AUX1, both adjrange entries must use adj_ch=0 (AUX1). The switch's low/high PWM values then activate the low/high ranges.

**How to apply:**
1. Identify which radio channel controls rate profile switching (e.g., AUX1 for a 2-position switch)
2. Convert to adj_ch (0-indexed from AUX1): AUX1=0, AUX2=1, AUX3=2, AUX4=3, AUX5=4, AUX6=5, AUX7=6, AUX8=7
3. Set both adjrange entries to the same adj_ch value
4. Test with `rate_profile` command in CLI while moving the switch through its range

## Profile naming command

Use `set profile_name = <name>` to name a PID profile in BF 2025.12.2. NOT `set name`.

Example:
```
profile 0
set profile_name = Low
profile 1
set profile_name = High
```

**Why:** BF 2025.12.2 renamed the command from `name` to `profile_name` to distinguish PID profile names from other config names (e.g., rateprofile_name).

**How to apply:** When documenting or scripting profile naming, use `profile_name`. If `set name` fails, check `dump all` to confirm the parameter name in your BF version.

## Gotcha: `get name` is ambiguous

`get name` in CLI matches multiple parameters (rateprofile_name, profile_name, etc.) and may return unexpected results.

**Workaround:** Use `get profile_name` or `get rateprofile_name` explicitly to avoid ambiguity.

**Why:** Betaflight's CLI parser uses prefix matching; `get name` matches both `profile_name` and `rateprofile_name`.

**How to apply:** Always use the full parameter name in get/set commands; don't rely on prefix matching.

## References

- `betaflight_adjrange_radio_binding.md` — channel indexing, range modes, non-overlapping ranges for multi-position switches
- `betaflight_cli_gotchas_2025.md` — general firmware gotchas and parameter changes
- `playbook_betaflight_cli_motor_testing.md` — motor test procedure and rate profile confirmation
