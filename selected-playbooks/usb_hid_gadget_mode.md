---
name: USB HID Gadget Mode Hardware Selection
description: Choosing between Mac Mini, Pi Zero, and Pi 5 for USB gadget mode implementation; hardware limitations and capabilities
type: reference
---

## Problem
Building software that acts as a USB HID device (keyboard/mouse) to a host computer, or needs USB composite gadget mode (HID + Ethernet simultaneously).

## Hardware Decision Matrix

**Mac Mini (Apple Silicon)**
- Cannot act as a USB gadget device
- Host-only mode only — no USB gadget/device mode support
- Not suitable for this use case

**Raspberry Pi Family Rankings** (best to worst for gadget mode)
| Model | Gadget Support | Notes |
|---|---|---|
| Pi Zero 2W | Yes, native | dwc2 USB controller; quad-core; WiFi; ideal for v1 prototyping |
| Pi Zero W | Yes, native | Same as Zero 2W but single-core (too slow) |
| Pi 3A+ | Yes | USB micro OTG port; underrated option |
| Pi 4B | Partial | USB-C power port supports gadget mode but shares with power input |
| Pi 5 | No | Explicitly dropped USB gadget support |

**Raspberry Pi Zero 2W** ✓ RECOMMENDED FOR V1
- Supports USB gadget mode (device, not host)
- Can present as both HID (keyboard/mouse) AND Ethernet adapter (RNDIS/ECM) simultaneously over a single USB cable (USB composite gadget)
- Cost-effective ($15–20)
- Full Linux kernel support for configurable gadget mode
- Linux `libcomposite` framework enables custom USB personality configurations
- Sufficient for TCP daemon + GPIO + persistent camera capture

**ESP32-S3** ✓ RECOMMENDED FOR V2
- Native USB HID device mode (no Linux, no gadget configuration needed)
- Built-in WiFi (both 2.4GHz and 5GHz capable)
- Arduino-compatible toolchain (C/MicroPython)
- 240MHz dual-core processor
- Smaller form factor and lower power draw (~150mA vs Pi's 400mA+)
- ~$5 cost
- No OS overhead — suitable for production miniaturization
- **Trade-off:** No SSH/interactive development; requires firmware flashing loop instead of Python iteration

**Arduino Pro Micro (ATmega32U4)**
- Excellent USB HID (native ATmega32U4 USB controller, `Mouse.h`/`Keyboard.h` in IDE)
- No gadget configuration needed; HID reports emit in microseconds
- **Rejected for Turk:** No WiFi; no TCP stack; absolute mouse positioning requires custom HID descriptor; would need ESP8266/W5500 shield combo
- **Better for:** USB-only devices, bare serial control, latency-critical HID (no Linux scheduler jitter)

**Raspberry Pi 5**
- Explicitly dropped USB gadget support
- Host-mode only
- Cannot be used for gadget mode projects
- Use older Pi models (Zero 2W, 3A+, 4B) instead

## Why
Mac Mini runs macOS with no USB gadget support at the kernel level — the architecture is host-only. Pi 5 removed gadget mode to streamline the product. Pi Zero 2W has sufficient CPU for the Linux gadget stack and costs a fraction of other embedded boards while delivering full gadget mode support.

## How to Apply
- If building USB HID automation or gadget-mode projects, start with Pi Zero 2W
- Do not attempt gadget mode on Mac Mini — redirect to Pi hardware
- If someone suggests Pi 5 for gadget mode, flag that it dropped support — use older Pi models instead
- For projects needing both HID and Ethernet via one cable, use Pi Zero 2W USB composite gadget configuration

## Gotchas

### USB Descriptor Spoofing (Endpoint Security Avoidance)
**Problem:** Default Linux Foundation VID/PID (`0x1d6b:0x0104`) is obviously synthetic and may be flagged by endpoint security software.

**Solution:** Spoof a legitimate OEM VID/PID with non-falsifiable strings.
- **Holtek Semiconductor Inc. (0x04d9:0xa0f8):** Extremely common OEM keyboard vendor; no public database of serial numbers exists; target sees "USB Input Device" from a plausible OEM
- Pair with realistic strings: `manufacturer="Holtek Semiconductor"`, `product="USB Input Device"`, `serial="<random>"` (not obviously sequential)
- Not cryptographically secure but defeats simple pattern-matching in security tools

## Related
- [[usb_composite_gadget_config]] — configuring RNDIS/HID composite gadgets on Pi Zero 2W
