---
name: OSD apply pre-flight diff — warn on items going dark
description: Before applying an OSD profile, diff current FC state against incoming profile; warn if any active items (value >= 2048) are going to zero
type: feedback
---

Pattern: OSD profile application can silently disable active items (GPS, home position, craft name, etc.) if the incoming profile has them zeroed out. No warning is shown to the user before the apply.

**The incident:** Session 2026-04-22 during `specs/osd-profile-library.md` review identified that `dt osd apply` has no pre-flight check. A profile could disable GPS/home display without user awareness. If a pilot applies a profile with `osd_gps_enabled=0` over a crafted profile with GPS at a specific screen position, the GPS element goes dark without confirmation.

**Root cause:** OSD profiles are opaque sets of register values. Active elements are indicated by position fields (value >= 2048 in Betaflight coordinate space — 2048 is the magic offset). When a field drops from any non-zero to 0, the element is hidden. There's no built-in diff or warning.

**How to apply:**

Before implementing or executing `dt osd apply`:

1. **Read current FC OSD state** — query the FC for all OSD register values
2. **Diff against incoming profile:**
   - For each OSD position field in the profile (e.g., `osd_gps_enabled`, `osd_home_enabled`, craft name registers)
   - If current value >= 2048 (active) AND incoming value == 0 (hidden):
     - **Generate a warning:** "The following OSD elements will be hidden: [list]"
3. **Require explicit confirmation** before applying — show the list of items going dark and require the user to type "yes, apply" or similar
4. **Special care for:**
   - GPS indicators (safety-critical; home position loss)
   - Craft name (identification)
   - Battery voltage / capacity (race-critical)
   - Video transmitter power (regulatory)

**Why:**

OSD elements are not undo-able; once a profile is applied, the previous display configuration is lost. GPS/home hiding is especially risky because it's used for recovery and safety. No built-in warning means users can accidentally apply a minimal profile and lose critical flight data visibility.

**Example warning message:**

```
⚠️  Profile apply will hide these active OSD elements:
  - GPS (row 0, col 25)
  - Home position indicator (row 1, col 25)

Apply anyway? Type 'yes' to confirm:
```

**Consequence:** Skip this check and pilots lose critical telemetry visibility without realizing it. The check takes ~2s (FC query) and prevents a preventable UX failure.
