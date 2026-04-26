---
name: Radiomaster Pocket mount detection on macOS
description: Detecting Radiomaster Boxer Pocket radio via USB; handling false positives from user drives
type: reference
---

# Radiomaster Pocket Radio Detection on macOS

## USB mount behavior

Radiomaster Pocket Radio Controller mounts as an **external volume named "NO NAME"** when connected via the data cable on macOS.

Verify with:
```bash
diskutil list external | grep -i "no name"
```

Or:
```bash
mount | grep -i media
```

## False positive: "Sam2TM" drive

When implementing radio detection, beware **personal external drives named with similar prefixes**. "Sam2TM" is a user's personal external drive and can falsely match radio detection heuristics.

**Why:** Radio detection code that checks for USB volumes with certain naming patterns needs to be specific. "Sam2TM" looks like it could be a radio but it's just a personal drive.

**How to apply:** 
- Use specific volume names: "NO NAME" or known hardware vendor strings, not partial pattern matches
- Check USB vendor/product IDs (VID/PID) if available via `ioreg` for higher confidence
- Fallback: prompt user to confirm the mount path rather than auto-detecting ambiguous names

## Testing

1. Plug in Pocket via data USB cable
2. Verify "NO NAME" volume appears in Finder sidebar
3. Check `diskutil list` or `mount` output
4. If implementing programmatic detection, validate against false positives with `lsblk` or `ioreg -p IOUSB`

## References
- `playbook_radio_edgetx_config_generation.md` — EdgeTX model YAML generation with radio detection
