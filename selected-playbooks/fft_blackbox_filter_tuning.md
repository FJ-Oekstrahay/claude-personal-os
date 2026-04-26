---
name: FFT Analysis Floor and Filter Tuning
description: Interpreting FFT peaks for mechanical resonance; 80 Hz floor separates control from hardware; 5 Hz minimum separation rule
type: playbook
---

# FFT Analysis Floor and Filter Tuning

## The distinction: control input vs mechanical resonance

When analyzing blackbox FFT plots for filter tuning, **not all peaks are mechanical resonances that need filtering**.

- **Below 80 Hz**: propwash (wind effects), control inputs (stick movements, rapid altitude changes), weight shift during flight. These are transient and not worth filtering — filtering them degrades responsiveness.
- **80–500 Hz**: mechanical resonances (frame vibration, blade harmonics, component resonance). This is the useful tuning range — peaks here indicate where notch filters or dynamic notch filters should be deployed.
- **Above 500 Hz**: usually electrical noise (PWM, servo noise). Less relevant for Betaflight tuning.

## The 80 Hz floor rule

**Do not apply notch filters or dynamic notch filters to peaks below 80 Hz.** They are not mechanical problems and filtering them will make the quad feel sluggish.

When reviewing FFT output:
1. Ignore peaks from 0–80 Hz (control / transient effects)
2. Focus on peaks 80–500 Hz (mechanical resonance candidates)
3. Apply filters only to consistent, narrow peaks in the mechanical range

## The 5 Hz minimum separation rule

FFT resolution depends on flight log duration and sample rate. High-resolution logs can show fine granularity, but **adjacent-bin peaks that are only 1–4 Hz apart are the same resonance**, not separate problems.

**Correct interpretation:**

| Peak 1 | Peak 2 | Likely interpretation |
|--------|--------|---|
| 185 Hz | 193 Hz | Same resonance (8 Hz apart) — single notch filter at ~189 Hz |
| 200 Hz | 205 Hz | Same resonance (5 Hz apart) — single notch filter at ~203 Hz |
| 150 Hz | 165 Hz | Distinct resonances (15 Hz apart) — check if two separate filters needed |
| 210 Hz | 210 Hz (repeated across bins) | Aliasing or log artifact — rerun with different duration |

## Practical workflow

When tuning with FFT:

1. **Pull blackbox logs** from a test flight with known vibration
2. **Run FFT analysis** (blackbox_decode with CSV output, then FFT tool)
3. **Filter the output** to remove anything < 80 Hz
4. **Identify peaks** spaced > 5 Hz apart — these are distinct resonances
5. **Deploy notch filters** targeting the center frequencies
6. **Re-test** to confirm peak reduction

## RPM filter and dynamic notch floors must be below the noise band

Betaflight's RPM filter and dynamic notch each have a minimum frequency floor. **If the floor is set above the actual motor noise band, the filter does nothing for those frequencies.**

Common misconfiguration:
```
rpm_filter_min_hz = 125   ← won't track below 125 Hz
dyn_notch_min_hz = 150    ← won't track below 150 Hz
```

If FFT shows primary resonance at 82–108 Hz (typical for 5"), both of these floors miss the entire problem band.

**Fix:** Set both floors to ~80 Hz:
```
set rpm_filter_min_hz = 80
set dyn_notch_min_hz = 80
```

This is safe — the RPM filter dynamically tracks motor speed, so at low throttle it simply won't fire, regardless of the floor setting. There's no stability risk to lowering the floor.

To check current filter floor settings from a connected FC:
```bash
source .venv/bin/activate && python cli/read_fc.py /dev/cu.usbmodem... 2>&1 | python3 -c "
import sys
lines = sys.stdin.read().splitlines()
keywords = ['dshot_bidir', 'rpm_filter', 'gyro_rpm', 'notch', 'dyn_notch', 'gyro_lowpass']
for line in lines:
    for kw in keywords:
        if kw in line.lower():
            print(line)
            break
"
```

Note: `cli/fc.py` is a library module — it has no `dump` subcommand. Use `cli/read_fc.py` for dumping FC config. The grep-via-Python pattern above avoids macOS grep syntax issues with multi-pattern matching.

## Dynamic Notch Filter (DNF) vs Manual Notches

Betaflight 2025.12 supports Dynamic Notch Filter, which automatically tracks resonance peaks without pre-tuning.

- **If peaks are clean and consistent across flights**: Manual notches are simpler and more predictable
- **If peaks shift between flights** (e.g., different weather, load, prop wear): Dynamic notch filter is better

Both work in the 80–500 Hz range.

## Related

- `reference_fpv_betaflight.md` — Seeker3 firmware, CLI commands
- `betaflight_blackbox_pull_modes.md` — retrieving logs for analysis
- `betaflight_blackbox_tools_compilation.md` — decoding logs to CSV for FFT input
