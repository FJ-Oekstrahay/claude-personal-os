---
name: Camera-Based vs HDMI Capture for Computer Control Automation
description: Comparing physical cameras and HDMI capture cards for screen-based AI control; when to use each approach
type: reference
---

## Problem
Building AI-driven computer control systems that need to read screen content (computer vision, image analysis) and send keyboard/mouse input. Deciding between physical camera and HDMI capture card approaches.

## Comparison

**Physical Camera Approach**
- Requires calibration for angle, lighting, distance
- Subject to environmental variation (reflections, ambient light)
- Pixel accuracy depends on camera resolution and focus
- Latency affected by camera firmware and processing
- Prone to false positives from slight position shifts
- More complex debugging (optical vs software issues)

**HDMI Capture Card Approach** ✓ RECOMMENDED
- **Perfect pixel accuracy** — directly reads screen output, no optical variance
- No calibration needed — pixel positions are deterministic
- $15-30 cost (USB3 HDMI capture dongle)
- Works with existing `--webcam` flag in automation frameworks
- Deterministic, reproducible results
- Dramatically simpler debugging (no camera/angle issues)
- Low latency (milliseconds, no camera processing)

## Why
HDMI capture is a direct digital feed from the host's GPU output. Physical cameras introduce optical variance (calibration drift, lighting changes, focus issues) that makes reliable AI control difficult. A $25 capture card eliminates all optical variables while providing pixel-perfect image input.

## How to Apply
- **Default approach:** Use HDMI capture card for any screen-based AI automation
- **Physical camera:** Only if HDMI capture is not available (air-gapped systems, non-digital displays)
- **Existing frameworks:** Most automation tools already support `--webcam` with video capture APIs — HDMI capture cards present as USB webcams, so no code changes needed
- Check framework docs for capture device selection flags

## Gotchas

### OpenCV VideoCapture Persistence (Critical for HDMI Capture Cards)
**Problem:** Opening and closing a VideoCapture per frame causes dropped frames and long enumeration delays when using HDMI capture cards.

**Solution:** Hold the VideoCapture object open persistently across the entire session.
- Lazy-open once, reuse across all frames
- Reconnect-once on dropped frame (if HDMI unplugged mid-session), then keep handle open
- Release only in cleanup/destructor
- OpenCV caches the device handle internally — repeated open/close forces re-enumeration
- **Pattern:** `VisionAgent._cap` (webcam) and `_rtsp_cap` (RTSP stream) held open between calls

## Related
- [[hardware_isolation_testing]] — diagnostic methodology for hardware component issues
- [[usb_composite_gadget_config]] — can combine HDMI capture + USB gadget for full bidirectional control
