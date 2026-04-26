---
name: Betaflight DJI MSP OSD Configuration
description: Configuring DJI air unit MSP/DisplayPort for OSD on Betaflight; firmware gotchas; troubleshooting checklist
type: reference
---

# Betaflight DJI MSP OSD Configuration

## The architecture
DJI air units (O4, O4 Pro) communicate with Betaflight via MSP over UART. The air unit sends video + OSD canvas data back to the goggles via MSP/DisplayPort (bidirectional link). If the link is broken, the goggles won't display OSD.

## Firmware versions
**Betaflight 4.4.3 and 2025.12 (calendar-based naming, replaces 4.x.x)**

**Broken versions for DJI OSD**:
- Betaflight 4.5.2 — confirmed broken for DJI OSD (GitHub #14531). Do NOT recommend; DeepSpace (Jennifer) has stale guidance.
- Earlier 2025.x versions — unknown compatibility; 2025.12.2 is latest stable.

**O4 Pro air unit firmware**:
- Current on most units: 01.00.03.00
- Latest: 01.00.04.00 — worth updating if OSD issues persist after wiring is confirmed.

## CLI configuration (Betaflight 4.4.3)
Minimum settings required:

```
set osd_displayport_device = MSP
set vcd_video_system = HD
```

These tell Betaflight to use MSP (not CRSF, not SPI) for OSD comms and set the canvas resolution to HD (53x20 for DJI).

**Do NOT use** `displayport_msp_serial` — this parameter doesn't exist in 4.4.3. UART binding is automatic: whichever UART has VTX_MSP enabled (in the Ports tab) is used for DisplayPort.

### Betaflight 2025.12 (if upgrading)
Parameter renames for rate control:
- `roll_rate` → `roll_srate`
- `pitch_rate` → `pitch_srate`
- `yaw_rate` → `yaw_srate`

When migrating a 4.4.3 diff to 2025.12, perform these renames. Other params (rc_rate, expo, motor protocol, GPS, serialrx) keep the same names.

### 2025.12 DJI OSD CLI settings
If using 2025.12 firmware:

```
set osd_displayport_device = MSP
set vcd_video_system = HD
set osd_canvas_width = 53
set osd_canvas_height = 20
set displayport_msp_fonts = 0,0,0,0
```

Also: check **Build Configuration** during flash — ensure "OSD (Digital)" is checked.

## Betaflight Configurator version
Use **Betaflight Web Configurator** (PWA) at https://app.betaflight.com with firmware 2025.12. Older desktop Configurator versions silently corrupt settings. The web app forces a backup before flashing.

## 2025.12 Ports tab changes
The Ports tab UI was redesigned in 2025.12:
- Peripheral option for DJI is now **"VTX (MSP + DisplayPort)"** (was just VTX_MSP toggle)
- Enable the **MSP toggle** on the same UART as well (per DeepSpace factory config: both MSP=ON and VTX(MSP+DisplayPort) in Peripherals)
- Serial RX for ELRS/CRSF is now a toggle in a dedicated "Serial Rx" column
- There is a **Presets tab** with "OSD for FPV.WTF, DJI O3 & O4, Avatar HD" — apply this first to auto-configure Ports + OSD tab, then verify the correct UART was set

## 2025.12 CLI params — what changed
- `osd_canvas_width` and `osd_canvas_height` are **removed** in 2025.12 — canvas size is negotiated directly between FC and air unit over MSP
- `displayport_msp_fonts` default changed to `0,1,2,3` — set to `0,0,0,0` for DJI
- Rate params renamed: `roll_rate`→`roll_srate`, `pitch_rate`→`pitch_srate`, `yaw_rate`→`yaw_srate`
- **Removed completely in 2025.12**:
  - `gyro_1_align_yaw` (board-defined, not user-configurable)
  - `crashflip_expo` (crash flip redesigned)
  - `gps_rescue_throttle_min`, `gps_rescue_throttle_max`, `gps_rescue_throttle_hover` (GPS rescue subsystem redesigned)
  - `gps_ublox_mode` (replaced by `gps_ublox_flight_model`)

**Canvas size note:** Both O4 and O4 Pro use the same 53x20 HD MSP canvas. Positions transfer directly between firmware versions (e.g., migrating OSD element positions from 4.4.3 to 2025.12 requires no coordinate changes).

## Build Configuration (flash-time options)
When flashing 2025.12, the configurator requires choosing **Analog vs Digital** for OSD protocol. **Must select "Digital"** for DJI/Walksnail/HDZero — this is a compile-time flag. If not selected, `osd_displayport_device = MSP` will have no effect.

## DJI O4 Air Unit Pro firmware versions
- Factory on Seeker3: 01.00.03.00
- Latest confirmed (Apr 2026): **01.00.06.00**
- Update via DJI Assistant 2 (Consumer Drone Series) — NOT via Goggles 3 device tab
- Release notes: https://dl.djicdn.com/downloads/DJI_O4_Air_Unit_Series/RN/20250306/DJI_O4_Air_Unit_Series_Release_Notes_en.pdf
- Downloads: https://www.dji.com/o4-air-unit/downloads

## HAKRCF722V2 (Seeker3) factory serial port assignments
From factory diff (`serial` CLI command output):
```
serial VCP    1       → USB MSP (Configurator)
serial UART1  64      → Serial RX (ELRS/CRSF receiver)
serial UART2  0       → unused
serial UART3  0       → unused
serial UART4  131073  → VTX_MSP (131072) + MSP (1) = DJI O4 Pro
serial UART5  0       → unused
serial UART6  2       → GPS
```
Function bitmask reference: MSP=1, GPS=2, RX_SERIAL=64, VTX_MSP=131072

## Seeker3 / HAKRCF722V2 post-flash checklist
After any firmware flash, ALL port settings reset. Minimum to restore:
1. Ports tab: UART1 → Serial RX toggle ON (CRSF for ELRS)
2. Ports tab: UART4 → MSP toggle ON + Peripherals = "VTX (MSP + DisplayPort)"
3. CLI: `set osd_displayport_device = MSP` + `set vcd_video_system = HD` + `set displayport_msp_fonts = 0,0,0,0` + `save`
4. Verify with `serial` CLI command — expect UART4 = 131073

## Python serial FC CLI automation pattern

When automating Betaflight CLI commands via Python serial library:

1. **Open port** with appropriate baud rate (typically 115200)
2. **Wait ~1 second** after opening — FC needs settle time before responding
3. **Send bare `#` (no newline)** to enter CLI mode — newline after `#` breaks it
4. **Send `\r\n` after `#`** — if FC was already in CLI mode, `#` just echoes; blank line forces a fresh `# ` prompt regardless
5. **Wait for `# ` prompt** — do NOT use fixed sleep timers. The FC responds when ready.
6. **Send each command and wait for the `# ` prompt** before the next command
7. **`save` causes reboot** — after `save`, the serial port will close/disconnect mid-read. Catch `OSError` on `in_waiting`/`read` — this is expected and normal.
8. **Betaflight web configurator auto-reconnect gotcha**: The PWA automatically reconnects after the FC reboots from `save`. Disconnect the web configurator before running CLI scripts or it will claim the port.
9. **Multi-FC configurator bug**: Betaflight Web Configurator (Chrome PWA) always reconnects to the same port when two FCs are connected — regardless of which port you select. Workaround: unplug one FC when using the configurator. The Python CLI has no this problem (explicit port path).

Example flow:
```
→ open serial port
→ sleep 1s
→ send: "#"
→ send: "\r\n"
← recv: "# "
→ send: "get osd_displayport_device\r\n"
← recv: "osd_displayport_device = MSP\r\n# "
→ send: "save\r\n"
← recv: "Saving EEPROM..." (port closes on reboot — catch OSError)
```

## OSD position encoding (BF 2025.12, HD 53×20 canvas)

OSD element positions are stored as integers in CLI (e.g. `set osd_craft_name_pos = 3086`).

**Key rule: higher value = further right on screen. Lower value = further left.**

Each unit of 1 corresponds to approximately 1 OSD grid cell (column) of horizontal movement.

**Do NOT try to decode absolute x/y coordinates from the raw value** — the encoding involves a visibility bit and column/row packing that varies by firmware version and is easy to get wrong. Instead:

- To move an element **right**: increase the value
- To move an element **left**: decrease the value
- For vertical movement: the step size is larger (one full row = canvas_width units)
- Use **relative adjustments** from a known-good position rather than computing from scratch

To move N notches in a direction: `get osd_<element>_pos`, then add or subtract N, then `set osd_<element>_pos = <new_value>` + `save`.

**Confirmed empirically on Seeker3 (BF 2025.12.2, 53×20 canvas, 2026-04-07)**:
- `osd_craft_name_pos = 3086` → right edge of screen
- `osd_craft_name_pos = 3081` → 5 notches left of right edge (toward center)
- `osd_craft_name_pos = 3091` → 5 notches past right edge (wraps to next row)

## Troubleshooting checklist

### 1. Verify MSP UART assignment (Ports tab)
- FC UART4 (or whichever UART connects to O4) must have `VTX_MSP` enabled in the Ports tab.
- Save. Reboot FC via CLI (`reboot`).

### 2. Confirm bidirectional MSP wiring
The critical issue: **O4 Pro requires bidirectional MSP to exit low power mode.**

The 3-in-1 cable has two data wires:
- **O4 RX (FC TX4)**: FC sends OSD commands to air unit
- **O4 TX (FC RX4)**: Air unit sends MSP frames back to FC (critical)

If the return wire (O4 TX → FC RX4) is disconnected, the air unit enters low power mode (PSM) and stops sending MSP frames. The goggles won't know the OSD is available.

**Test with a multimeter**: Disconnect the 3-in-1 cable at the FC end. Probe the O4 TX wire for continuity to the FC RX4 pad. If open circuit, either the wire is broken or the pad is lifted.

### 3. Check CLI beeper config
Many users confuse `get beeper` with `beeper`:
- `get beeper` — returns hardware settings only (inversion, OD, freq). Does NOT show enabled events.
- `beeper` — shows which events are enabled.

Command: `beeper` (no args)
Expected output: `Disabled: none` (all events enabled) or list of enabled events.

If you see `Disabled: [long list]`, beeper events are restricted. This won't break OSD but won't beep on battery warnings.

### 4. Goggles behavior (DJI Goggles 3)
DJI Goggles 3 has **no "Custom OSD" toggle** in the menu. OSD either works or doesn't:
- If MSP link is live: OSD appears automatically
- If MSP link is dead: OSD doesn't appear (no menu option to diagnose or enable)

**Device type selection**: DJI Goggles 3 requires manually selecting the device type in the goggles menu (O4 Pro, Avata 2, Air 3, etc.) — there is no automatic device scan. Select the correct model to ensure proper firmware handling.

If you can't see OSD in the goggles, the MSP link is broken. It's not a goggles setting.

## Wiring integration gotcha
The DJI 3-in-1 cable in some frames (e.g., Seeker3) may be **permanently harness-integrated** to the frame. It's not user-swappable at a connector level — if the cable is damaged, the entire harness may need replacement.

Before concluding the cable is bad, test continuity at both ends (FC pads and air unit pads) with a multimeter.

## Definitive isolation test (when all config is correct but OSD still fails)
If config, wiring, CLI settings, and firmware are all confirmed correct but OSD still absent:
- Swap air units between two drones to isolate O4 defect vs FC defect
- If O4 works on a different FC → Seeker3 FC is the problem (UART4 output issue)
- If O4 fails on a different FC too → O4 hardware is defective

## Warranty case documentation checklist
- Factory CLI diff matches current `serial` output ✓
- Wiring pinout verified against DJI O4 Pro and HAKRCF722V2 diagrams ✓
- TX/RX continuity tested with multimeter, crossover confirmed correct ✓
- BF 2025.12.2 with Digital OSD build option ✓
- OSD preset applied + CLI settings verified ✓
- O4 firmware updated to latest ✓
- Goggles firmware updated ✓
- Still: "air unit in low power mode", no OSD

## Related
- Seeker3 OSD troubleshooting: `projects/seeker3/OSD_troubleshooting_plan.md`
- Reference guide: `memory/reference_fpv_betaflight.md` (system inventory, firmware versions, CLI commands)
- DeepSpace email thread attachments: Google Drive → Drone/Deep Space Seeker3/Troubleshooting/from-deep-space/
- Factory CLI diff on Drive: Drone/Deep Space Seeker3/Troubleshooting/SEEKER3_O4PRO_GPS_ELRS TBS_4.4.3.txt
