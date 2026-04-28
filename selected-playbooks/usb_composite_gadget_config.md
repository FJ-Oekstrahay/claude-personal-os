---
name: USB Composite Gadget Configuration on Raspberry Pi Zero 2W
description: Setting up RNDIS/ECM + HID simultaneously on a single USB cable; one-cable keyboard/mouse + Ethernet adapter setup
type: reference
---

## Problem
Need a Raspberry Pi to present as both a USB HID device (keyboard/mouse) AND a USB Ethernet adapter over a single USB connection to a host computer. Typical use case: automated control + network access via one cable.

## Solution: USB Composite Gadget

Raspberry Pi Zero 2W supports `libcomposite` to create multi-function USB devices that present multiple personalities over a single USB connection.

**Typical composite configuration:**
- **HID gadget** — presents as keyboard/mouse input device
- **RNDIS or ECM gadget** — presents as Ethernet adapter (RNDIS for Windows, ECM for macOS/Linux)
- Single micro-USB cable to host delivers both interfaces

## Setup Overview (Linux `libcomposite`)
1. Load `libcomposite` kernel module
2. Create gadget config with two functions (HID + RNDIS/ECM)
3. Bind both functions to UDC (USB Device Controller)
4. Host recognizes two devices: HID device + network adapter
5. Configure Ethernet on the Pi side (DHCP server or static IP)

## Why
This eliminates the need for separate USB cables or hubs. One micro-USB port on the Pi provides:
- Keyboard/mouse control (HID)
- Network connectivity (Ethernet over USB)

Host sees two USB devices but they share one physical cable.

## How to Apply
- Search for `libcomposite hid rndis` or `libcomposite hid ecm` examples (OS-specific)
- Use `configfs` to configure gadget personalities
- Test with `lsusb` on host to verify both interfaces are enumerated
- Verify HID device is recognized in `input-devices` or similar
- Verify Ethernet interface appears in `ifconfig` or `ip link`

## Hardware Requirement
- **Only Raspberry Pi Zero 2W** (or older Pi Zero with USB OTG support)
- Not available on Pi 5 (dropped gadget mode)
- Not available on Mac Mini (host-only)

## Example Use Case
Automated drone configurator:
- HID for sending RC stick commands to simulator
- Ethernet for uploading telemetry logs back to host
- All over one USB cable

## Related
- [[usb_hid_gadget_mode]] — hardware selection and why Pi Zero 2W is the only current choice
- [[serial_port_contention]] — managing resource access when Pi is controlling hardware via GPIO/serial

## Resources
- Linux `configfs` documentation
- Adafruit guides for Pi Zero USB gadget setup
