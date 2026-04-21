---
name: Betaflight CLI motor testing
description: Motor command behavior, reboot triggers, and safe testing sequence
type: feedback
originSessionId: 27695732-48ac-444c-b80c-0e55fc46264d
---
## Motor test via Betaflight CLI

Motor test via `motor` command in BF CLI requires specific handling:

**Speed range:** Only low speeds work reliably. Use values in the **1070 out of 2000 range** (approximately 5% throttle). High speeds will trigger safety cutoffs.

**Reboot on session exit:** When you exit the BF CLI session (type `exit` command), the FC will reboot. This is normal behavior — the motor command leaves the FC in a transient state. Scripts must handle `TimeoutError` after motor stop commands because the reboot happens immediately.

**Safe sequence:**
1. Connect via CLI
2. Issue `motor 0 1070` (test motor 0 at low speed)
3. Observe behavior and ask user for feedback before moving to next motor
4. Stop motor: `motor 0 1000` (idle, zero throttle)
5. Repeat for other motors (1, 2, 3)
6. Type `exit` — FC will reboot
7. Wait ~4 seconds for reboot to complete before attempting to reconnect

**Why:** Motor test mode is a special FC state. The reboot clears it safely. Don't try to reconnect immediately after exit — the serial port will timeout while the FC is rebooting.

**One motor at a time:** Always test one motor, get user feedback ("spinning correctly?"), stop it, ask before moving to next. Don't test multiple motors in a sequence without checking each result.

**User confirmation required:** Ask user what they observed (spin direction, speed, sound) after each motor test before proceeding to the next.
