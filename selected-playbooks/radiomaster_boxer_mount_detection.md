---
name: Radiomaster Boxer Pocket mount detection on macOS
description: Radiomaster Boxer Pocket appears as 'Sam2TM' volume on macOS, not recognized name
type: feedback
---

The Radiomaster Boxer Pocket radio does not mount with a recognizable device name on macOS. Instead, it appears as a USB volume labeled `Sam2TM`.

**Identification:** When connected via USB, `diskutil list` shows the volume as `Sam2TM`. This is not a standard recognizable name; it's model/firmware specific.

**How to add to detection:** Add `Sam2TM` to the known radio volume list in `radio.py` or equivalent detection code.

**Why:** Default volume detection patterns expect names like "FLYSIGHT" or similar FAT filesystem labels. The Boxer Pocket uses a different firmware label that doesn't match those patterns.

**How to apply:** When adding support for new radio hardware, test the actual USB mount name on a connected device. Update the known-radio-volumes list to include it.
