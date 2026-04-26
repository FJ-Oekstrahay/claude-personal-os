---
name: Betaflight OSD coordinate validation
description: Validating OSD element placement; catching AI-generated off-screen coordinates; HD vs SD display differences
type: feedback
---

Betaflight OSD coordinate system has physical display constraints that vary by display type. AI models frequently ignore both the formula bounds and display-specific limits.

**Standard SD display (30×15):**
- **Formula:** Position = row*64 + col + 2048 (where row and col are 0-indexed)
- **Physical constraints:** Col 0-29, Row 0-14 (positions >= col 30 or row >= 15 are off-screen)
- **AI gotcha:** Models generate col 50-59 range (valid integers, physically invisible)

**HD display (53×20) — droneteleo empirical discovery:**
- **Formula:** Same — Position = row*64 + col + 2048
- **Physical constraints:** Col 0-52, Row 0-19
- **V_STEP:** 64 (vertical step size)
- **Visibility control:** VISIBILITY_BIT = 0x800 (bit 11 in config flags)
- **Coordinate reference:** Confirmed in `cli/osd_edit.py` — read that file for HD layout logic, not SD documentation

**How to apply:**

1. **Before writing OSD config generation code:** Read `cli/osd_edit.py` to see actual coordinate handling — don't assume SD limits
2. **When generating positions via AI:** Validate against the correct display bounds:
   - For SD: reject if col >= 30 or row >= 15
   - For HD: reject if col >= 53 or row >= 20
3. **Visibility:** If elements are invisible despite valid coordinates, check the VISIBILITY_BIT (0x800) — bit manipulation, not coordinate issue
4. **Testing:** Verify on actual hardware; OSD coordinates are display-dependent and can silently fail

**Why:** 
- Initial OSD work used SD documentation (30×15) — HD displays need different bounds
- HD layout has different constraints discovered empirically during session motor-night (2026-04-21)
- `cli/osd_edit.py` is the authoritative reference for coordinate validation logic across display types
