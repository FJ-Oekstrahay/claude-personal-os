---
name: FPV / Betaflight / DJI reference
description: Key FPV drone knowledge from Seeker3 troubleshooting — CLI commands, DJI OSD diagnostics, Betaflight versions, ELRS binding
type: reference
---

## Betaflight CLI — beeper
- `beeper` (no args) — lists all events with `+` (enabled) / `-` (disabled). "Disabled: none" = all events on.
- `get beeper` returns hardware config only (inversion, OD, frequency) — NOT event list.
- `beeper LOW_BATTERY` — enable event. `beeper -LOW_BATTERY` — disable.
- `beeper RX_LOST` — good to enable when flying without OSD.

## DJI O4 Pro — OSD / Low Power Mode
- "Air unit in low power mode" = O4 receiving zero MSP frames from FC.
- MSP is **bidirectional**: FC TX4 → O4 RX (sends OSD data), O4 TX → FC RX4 (sends arm state back).
- Low power mode persists if the **return wire (O4 TX → FC RX4) is broken**, even if TX direction works.
- "Custom OSD" toggle does NOT exist in Goggles 3 — OSD just appears automatically when MSP works.
- Canvas Mode = HD in goggles is correct setting.

## DJI O4 Pro — Firmware versions
- O4 Pro latest: **01.00.04.00** (Jan 2026). Standard O4 latest: 01.00.03.00.
- Update via **DJI Assistant 2 (Consumer Drone Series)** — Goggles 3 Device tab may not work for AU firmware.

## Betaflight firmware — DJI OSD compatibility
- **Avoid 4.5.0–4.5.2**: confirmed OSD regression (GitHub #14531 — HD DisplayPort broken).
- **Avoid 4.4.2**: `vcd_video_system` reverts to AUTO (GitHub #13056).
- **Safe versions**: 4.4.3, 4.6.0+.

## Betaflight CLI — DJI OSD verification
```
get osd_displayport_device   → must be MSP
get vcd_video_system         → must be HD
```
`displayport_msp_serial` doesn't exist in BF 4.4.3 — auto-binds from whichever UART has VTX_MSP.

## DeepSpace Seeker3 + HAKRCF722V2
- FC: HAKRC F722 mini V2 (HAKRCF722V2), STM32F7X2
- Ships with BF 4.4.3
- DJI O4 Pro on **UART4** — pre-configured at factory
- UART3 = SBUS receiver (RX3)
- Jennifer at DeepSpace recommended 4.5.2 — that's wrong, it's a broken version

## Radiomaster Boxer — bind without SYS button
- SYS not needed for binding. Go: **MDL → Setup page → Internal/External RF → [BIND]**
- ELRS bind phrase: if TX and RX share the same phrase, they bind automatically on power-up.

## Power & Battery settings (Seeker3)
- Warning Cell Voltage: 3.8V (already set)
- Minimum Cell Voltage: 3.5V
- Beeper triggers at warning threshold. Land at first beep, don't push to minimum.

## USB-to-serial adapter (UART test)
- Need 3.3V logic adapter (CP2102, FTDI FT232, CH340)
- Connect: adapter GND → FC GND, adapter RX → FC TX4 pad
- Open terminal: `screen /dev/tty.usbserial-* 115200`
- Binary data = UART alive. Silence = UART TX dead.
