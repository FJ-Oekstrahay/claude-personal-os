---
type: playbook
title: EdgeTX Config Generation for Radiomaster Boxer
agents: [bob, seymour]
tags: [fpv, edgetx, radiomaster, boxer, radio, adjrange, serial conflict, playwright, betaflight]
created: 2026-04-08
updated: 2026-04-08
---

## Goal

Generate EdgeTX model YAML files and adjrange configurations automatically for Radiomaster Boxer radio, instead of manual step-by-step instructions. Used by droneteleo's `radio.py` CLI tool to write directly to radio SD card.

## When to Use

- Automating Betaflight adjrange binding to radio mixer channels (S1, S2 knobs on Boxer)
- Writing EdgeTX model config files to radio SD card via Boxer's USB-C mass storage
- Avoiding manual "open EdgeTX, go to Mixes, add adjrange" workflows

## Key Facts

### EdgeTX Model YAML Structure

- **Location on radio:** `/MODELS/*.yml` on SD card
- **Access:** USB-C → mass storage mode (no ejection needed)
- **Format:** YAML; schema per Boxer firmware version
- **Writing:** Atomic replacement — write whole file, not incremental edits

### Adjrange Function IDs

Betaflight adjrange commands reference function IDs that map to radio channels:

```
adjrange 0 0 100 0 0    # Gyro low-pass filter (function ID 0)
adjrange 1 0 100 0 1    # ... (function ID 1)
```

The function IDs are documented in Betaflight source, but **must be verified against the user's actual FC firmware version** before trusting them in production.

**Verification method:**
```bash
python3 radio.py --read  # Reads adjrange from live FC, prints function IDs
```

**Critical caveat:** `radio.py` function IDs are currently sourced from BF docs, not tested against live hardware. Always verify before deploying to user's FC.

### Serial Conflict: BF Configurator vs. radio.py

**Problem:** Betaflight Configurator (GUI) and `radio.py` (CLI) both try to open the same serial port to the FC. Windows/Linux allow concurrent opens; macOS does not.

**Symptoms:**
- `radio.py --read` hangs or fails with "port in use"
- BF Configurator is open in the background

**Workaround options:**
1. Close BF Configurator entirely before running `radio.py`
2. Use BF Configurator's Disconnect button, but stay in the app
3. (Spike) Use Playwright to automate BF Configurator's Disconnect/Connect buttons via CDP, avoiding manual steps

**Spike plan (not yet implemented):**
- Launch BF Configurator in headless mode via Playwright
- Click Disconnect button
- Run `radio.py --read` (serial port now free)
- Click Connect button in Configurator
- Verify FC state in Configurator UI

## Implementation Details

### radio.py Architecture

Location: `~/.openclaw/workspace/projects/droneteleo/cli/radio.py`

**Functions:**
- `generate_adjrange_edgetx()` — produces EdgeTX Mixes instructions + verification checklist for given adjrange commands
- File generation (not yet implemented) — write YAML to radio SD card directly

**Input:** Betaflight adjrange commands from `agent.py` proposal
**Output:** EdgeTX YAML (future) + verification checklist + adjrange function ID warnings

### Windows Port Detection

For future Windows support, `serial.tools.list_ports.comports()` replaces glob-based scanning. ~2 lines of code.

## Testing Checklist

From `TEST_PLAN.md`:

- [ ] Boxer + FC connected via USB
- [ ] `python3 radio.py --read` returns live adjrange list with no errors
- [ ] Function IDs match Betaflight Configurator (CLI mode)
- [ ] EdgeTX model YAML written to SD card (Boxer USB-C, no ejection)
- [ ] Boxer radio boots and loads model without errors
- [ ] S1/S2 knobs respond to adjrange changes in-flight (live test on Seeker3)

## Known Gaps

- **YAML schema validation** — need actual Boxer model YAML example to build schema validator
- **Atomic write safety** — no rollback if write fails mid-file; consider temp file + atomic rename
- **Firmware version auto-detection** — currently manual; should read from FC and adjust function IDs
- **Cross-platform testing** — verified on macOS (Boxer USB-C); needs Windows/Linux CI

## References

- Betaflight adjrange docs: `docs/Adjrange.md` (Betaflight GitHub)
- EdgeTX radio.py integration: `cli/radio.py` in droneteleo project
- Serial conflict diagnostics: `playbooks/playwright_web_automation.md` (Playwright + BF Configurator spike)
- Battery-low alerts: `edgetx_radio_battery_alert.md` (complements adjrange and logical switch setup)

## Next Steps

1. Verify adjrange function IDs against live FC (`python3 radio.py --read`)
2. Collect actual Boxer model YAML to build schema validator
3. Implement file generation (write to `/MODELS/*.yml`)
4. Test on live hardware (Seeker3 + Boxer + Harakart FC)
5. Consider Playwright BF Configurator disconnect spike if serial conflicts become frequent
