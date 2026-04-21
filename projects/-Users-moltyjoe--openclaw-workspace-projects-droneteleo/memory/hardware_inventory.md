---
name: Hardware Inventory
description: Geoff's FPV hardware available for Droneteleo testing — FCs, radios, goggles
type: user
originSessionId: 0710c7f3-8476-408c-b055-c7c8256ee29b
---
## Flight Controllers / Drones

- **QAV** — Lumenier QAV-S 2 Sub-250 Joshua Bardwell SE 3". FC: Lumenier LUX HD AIO G4 (STM32G473, ICM42688P gyro, 16MB blackbox). ESC: AM32 35A, bidir DSHOT supported. Motors: Xilo Stealth 1404 4500KV. Video: **DJI O4 Air Lite** (thermal-sensitive — hits 80°C+ in standby without airflow; requires active cooling on bench; must launch immediately after arming, unplug immediately after landing). Sub-250g AUW. Adjrange in use from prior session. BF target unconfirmed — check on next connect.
- **DeepSpace Seeker3** (HAKRCF722V2) — Frame: 3" freestyle, 139mm WB, sub-250g. FC: F722 MCU, ICM42688P gyro, DPS310 baro, 16MB blackbox. ESC: BL32 40A 4-in-1. Motors: Aether 1505 4000KV (4S). Props: HQProp T3X3X3 (CCW) / T3X3X3R (CW). Video: DJI O4 Air Pro. GPS: front-mounted. Battery: 4S 650–1100mAh. yaw_motors_reversed=ON. align_board_roll=180 (set 2026-04-12 after cable repair reoriented FC). BF 2025.12.2, target HAKRCF722V2.
- **Flywoo Flytimes 85 HD O4 2S Micro FPV Drone** — small micro, available for testing
- **Tinyhawk III** (one or both tinyhawks are III) — available for testing

## Radios

- **Radiomaster Boxer Max** — primary reference hardware for EdgeTX YAML work
- **Radiomaster Boxer Pocket** — same EdgeTX schema as Boxer Max; variant doesn't matter, BF version does
- **EMAX** (FrSky protocol) — lower priority; Geoff not focused on FrSky for now
- **Jumper T Lite** (FrSky protocol) — lower priority
- **DJI RC3 and RC2** — unclear if useful for Droneteleo scope

## Goggles

- **DJI Goggles 3** — digital
- **Skyzone Cobra X V4** — analog
- **EMAX box style** — analog

## Raspberry Pi

- **Pi dev kit ordered** (2026-04-11) — specific model TBD from order confirmation; noted in system info memory file

## Bench Equipment

- **ToolkitRC P200 V2.0 Mini Desktop Power Supply** — ordered 2026-04-15. 30V/10A, AC100W/DC200W, 65W USB fast output, IPS color display. Replaces HOTA charger in power supply role (HOTA was fried twice). Intended for powering FC on bench without depleting flight batteries.

## Storage

- **No FC uses an SD card.** All blackbox logging is to onboard flash (16MB on both QAV and Seeker3). `droneteleo blackbox pull` is not applicable — there is no SD card to mount or eject.

## Weight (Measured)

| Component / Configuration | Weight |
|---|---|
| Tattu R-Line 850mAh 4S Battery | 98g |
| QAV Props Only (GEMFAN Hurricane 3020-3, set of 4) | 6g |
| Seeker3 Props Only (HQProp T3X3X3B-PC, set of 4) | 6g |
| QAV-S2 (Dry/No Props) | 156g |
| QAV-S2 (With Props) | 160g |
| QAV-S2 (Props + Battery) | 256g |
| Seeker3 (Dry/No Props) | 112g |
| Seeker3 (With Props) | 118g |
| Seeker3 (Props + Battery) | 216g |

## Notes

- **DJI O4 naming convention** — Official DJI names are "DJI O4 Air Unit Pro" and "DJI O4 Air Unit". "Lite" is community shorthand for the base unit (no "Pro"). Joshua Bardwell explicitly endorses this usage. Use either form; when writing copy that might be read by newcomers, prefer the official name with "(a.k.a. O4 Lite)" on first reference.
- Boxer Max and Pocket use the same EdgeTX YAML schema — no software difference for testing
- BF version matters more than quad model for adjrange validation
- Battery should not stay connected too long on bench — drains to dangerous voltage level. Batch all battery-required tests together.
