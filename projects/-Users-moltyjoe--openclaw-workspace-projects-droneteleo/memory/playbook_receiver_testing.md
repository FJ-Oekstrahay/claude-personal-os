---
name: Receiver and modes testing requires battery power
description: FC won't talk to the ELRS receiver or power the O4 without battery; USB-only is insufficient for receiver/radio testing
type: project
originSessionId: 6ae72a11-f0b9-4516-859a-8a713ec04c1f
---
The drone does not respond to the controller unless connected to a battery (or bench power supply). USB-only powers the FC for BF config (PIDs, adjrange CLI, diff, etc.) but does not power the ELRS receiver or the O4 video system.

**Why:** The receiver and video transmitter draw more current than USB can supply; they're on the battery rail, not the USB 5V rail.

**How to apply:**
- Any test that requires verifying radio channels (aux channel reaction, receiver tab, adjrange end-to-end) needs battery connected.
- Applying BF CLI commands (adjrange, aux, save) is fine over USB alone.
- When advising Geoff on testing, distinguish between "apply the config" (USB OK) and "verify it works" (needs battery).
- The O4 goggles also need battery to power up — don't expect video feed without it.
