---
name: OSD ASCII canvas preview — low-fidelity disclaimer required
description: Terminal ASCII preview of OSD layout is too crude to set accurate expectations; agent must disclaim before showing
type: feedback
---

## Pattern

When showing an OSD element layout preview via terminal (ASCII canvas), the rendering is often crude compared to actual goggles display:

- **ASCII:** Single monospace chars, fixed row/col, no fonts, poor spatial resolution
- **Actual goggles:** Scaled fonts, sub-pixel positioning, color, real rendering engine

This gap causes pilot expectations mismatch: "Looks fine in ASCII" → "Looks terrible in goggles".

## Why this matters

**Session context:** Session 2026-04-23 built OSD preview rendering in terminal via Rich table (shows element placement as ASCII grid). When pilot sees the preview, they may approve based on ASCII appearance without realizing the actual goggles display will look very different due to font scaling and actual DJI O4 rendering.

**Risk:** Pilot approves profile in agent, applies it, checks goggles, sees misaligned elements, requests undo. Agent has to detect this failure mode (via pilot feedback "Revert") and restore backup. Preventable with upfront disclaimer.

## How to apply

**In AGENT_SYSTEM, add disclaimer before any OSD preview:**

```
When showing OSD element layouts in this chat, I always include this disclaimer:

"Preview is ASCII text-based — actual goggles display uses fonts, scaling,
and color rendering that differ significantly. Approve based on element
selection, not exact positioning. Actual positioning only confirms in goggles."
```

**In code, before rendering preview:**

```python
def show_osd_preview(profile_name, elements):
    print("="*60)
    print("OSD Profile Preview (ASCII — actual appearance differs)")
    print("Element placement shown below. Approve based on elements,")
    print("not exact positioning. Check goggles for final confirmation.")
    print("="*60)
    
    # Render ASCII canvas
    canvas = render_osd_canvas(elements)
    print(canvas)
    
    print("\nSay 'apply <profile_name>' to apply, or 'cancel' to skip.")
```

**In agent loop:**

```python
if pilot_action == 'apply_osd':
    # Show preview
    show_osd_preview(profile_name, elements)
    
    # Agent injects into context:
    build['osd_preview'] = {
        'profile': profile_name,
        'disclaimer': 'ASCII preview only; actual goggles rendering differs'
    }
    
    # Wait for pilot confirmation
    # Only proceed if pilot explicitly confirms after seeing disclaimer
```

## Testing

1. Render a profile in ASCII
2. Verify pilot can read element names (e.g., "THROTTLE at row 5, col 8")
3. Apply to drone
4. Pilot checks goggles — should see similar element placement but with actual fonts/scaling
5. If pilot says "looks different", refer back to disclaimer: "Yes, ASCII vs. actual rendering differ; adjust if needed"

## Backlog

- Consider richer preview (HTML snapshot or rendered image sent via webhook) as v2 improvement
- For v1, disclaimer is the correct guard against expectation mismatch

## Related

- [[osd_apply_verification_gap]] — verification limitations in OSD apply flow
- [[agent_first_feature_design]] — agent-managed OSD workflow
