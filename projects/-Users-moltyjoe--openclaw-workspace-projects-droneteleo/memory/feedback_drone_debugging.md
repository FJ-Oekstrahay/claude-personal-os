---
name: Drone debugging workflow
description: How to approach live drone debugging sessions — use droneteleo software, motor test procedure, key reminders
type: feedback
originSessionId: 27695732-48ac-444c-b80c-0e55fc46264d
---
When Geoff brings a drone issue and it's connected, always use the droneteleo software to assist. Don't just give generic advice — actually connect, read params, and use the tools.

**Why:** Droneteleo is the product. Using it in real debugging sessions is both useful and validates the product.

**Always offer first:** When a diagnostic action can be done by droneteleo (spin a motor, read a param, apply a fix), ask "do you want me to do that, or do you want to do it yourself?" Don't default to instructing the user to use BF Configurator when the CLI can do it.

**How to apply:**
- Run `droneteleo detect` first to identify which quad is connected and which port
- Check memory for that quad's build/config info before asking Geoff
- Read current FC params directly instead of guessing
- If port is busy (Errno 16), immediately tell Geoff: "Port is busy — click the **Disconnect button** in Betaflight Configurator first." Use "Disconnect button" not just "disconnect" — user might physically unplug the cable otherwise.
- Before every CLI action that needs the port, remind user to click the Disconnect button. Don't assume they remembered from last time.

## Motor testing procedure

When motor testing is needed:
1. **Always say: "Make sure props are off before running motor tests."** Never skip this.
1a. **Always show the safety warning before spinning any motor** — same language as BF Motors tab:
    > ⚠️ MOTOR TEST — Remove all propellers before proceeding. Motor test mode may remain active after the test. Arming may not stop the motors. **Disconnecting the USB cable may not stop the motors** — battery disconnect is the safest emergency stop.
    Require explicit confirmation ("props off confirmed") before issuing any motor spin command.
2. For verifying motor spin direction, suggest either:
   - The **dollar bill method** — hold a thin piece of paper near the spinning motor; it deflects toward the direction of spin
   - Oscar Liang site (oscarliang.com) has motor direction guides; no specific video found yet
3. Remind user to check **A vs B props** — clockwise props on CCW motors (or vice versa) causes exactly the violent-flip-on-throttle symptom

## Troubleshooting violent flip on throttle/pitch

Standard checklist (in rough order of likelihood):
1. Wrong A/B props on wrong motors
2. Motor spin direction wrong (check in BF Motors tab, one at a time, props OFF)
3. Motor/ESC signal numbering mismatch (M1 position doesn't match physical motor)
4. FC orientation not configured (check BF Setup tab — move quad, watch 3D model)
5. Gyro miscalibration (power on while moving during a repair)

For "drone flew fine before, only X changed": focus on what could have been disturbed during the repair, even if not intentionally rewired.
