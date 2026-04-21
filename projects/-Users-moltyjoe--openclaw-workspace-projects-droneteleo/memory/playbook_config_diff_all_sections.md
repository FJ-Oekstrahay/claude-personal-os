---
name: Betaflight config diff — completeness validation
description: Ensure diff output includes all section types, not just dict-based config
type: feedback
originSessionId: 27695732-48ac-444c-b80c-0e55fc46264d
---
## Config diff must cover all section types

**The problem:** Betaflight config has both **dict-based sections** (single key=value pairs) and **list-based sections** (indexed multi-element structures). When comparing two configs, it's easy to miss the list sections if the diff algorithm only iterates over parsed dict keys.

**List-based sections that were blind spots:**
- `feature` — enabled/disabled features (like `SOFTSERIAL`, `DJI_OSD`)
- `serial` — UART assignments and baud rates
- `aux` — auxiliary channel mappings (arming switches, failsafe, etc.)
- `beacon` — beeper configuration
- `adjrange` — Betaflight Adjrange definitions for radio adjuster channels

**Why this matters:** Changing these sections is safety-critical. For example:
- Swapping `aux` channels changes which RC input arms the quad
- Changing `serial` ports changes where telemetry/OSD is wired
- `feature` changes can enable/disable entire subsystems

If a diff misses these sections, the CLI output shows "No changes" even when critical arming or failsafe behavior changed.

**Validation pattern:**
1. Parse BFConfig object to populate all fields (dict + list)
2. When generating diff output, explicitly iterate over list sections separately
3. Use a `_diff_list()` helper: compare indices, check for added/removed/modified list items
4. Format list changes clearly (show old and new values, not just "added" or "removed")
5. Merge list diffs into the main diff output alongside dict diffs

**Applied fix:** config.py `diff()` method now calls `_diff_list()` for all five list sections. Parser was also fixed to avoid re-entering profile sections after restore lines.

**Test this:** Run `droneteleo diff` after changing any list-based section (e.g., remap an aux channel). The diff output should show the change. If it doesn't, the parser is still blind to that section type.
