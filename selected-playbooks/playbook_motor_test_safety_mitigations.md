---
name: Motor Test Safety Mitigations
description: 8 blocking mitigations from Safety Officer review; arming checks, motor watchdog, throttle cap, confirmation UX
type: feedback
---

Motor test feature has 8 baked-in safety mitigations per Safety Officer review (2026-04-20).

**Arming state check:**
- Query MSP_STATUS before any motor command via get_status() in pi/msp_bridge.py
- Block motor spin if armed == True
- Why: prevents accidental prop hazard during bench test
- How to apply: gate motor_test flow in agent.py before MSP_SET_MOTOR call

**Motor stop watchdog verification:**
- Read motor_stop BF master config parameter (new MSP read path) before test starts
- Confirm value in response before reporting test ready
- Why: motor_stop is the hardware failsafe; must be active to trust test safety
- How to apply: add motor_stop read + validation to motor_test setup phase

**Hard throttle cap at encode layer:**
- MSP packet encoder enforces MOTOR_TEST_MAX_THROTTLE = 1150 (out of 2000 PWM)
- No conditional logic in agent; cap is unconditional and immutable
- Why: failsafe against out-of-range throttle values leaking into payload
- How to apply: validate cap in pi/msp_bridge.py MSP_SET_MOTOR encode

**Confirmation UX — phrase-based re-prompt:**
- "PROPS OFF" full phrase required for confirmation (not just 'y')
- Re-prompt on every invocation (no "remember my choice")
- Why: accidental confirmation is catastrophic; phrase is harder to fat-finger
- How to apply: motor_test prompt includes phrase match check, never stored in session

**Per-motor 10s timeout in map mode:**
- Individual motor spins in map mode (--map flag) each timeout after 10s
- Prevents runaway if FC loses contact
- Why: single motor spin failure shouldn't block test completion for others
- How to apply: timeout wraparound in map loop, next motor proceeds on timeout

**MSP command completeness (v1 final scope):**
- Cut --all flag from v1 (all-motors spin deferred to v2)
- MSP_MOTOR readback (104) must confirm spin before reporting pass
- Why: --all introduces complexity; readback is belt-and-suspenders safety check
- How to apply: after MSP_SET_MOTOR, read MSP_MOTOR and validate response before success

**USB power claim correction:**
- SKILL.md updated: USB power is sufficient for config changes only
- Receiver/radio/channel test requires battery connected (props off)
- Why: O4 receiver draws power that USB cannot supply; battery is prerequisite for full test
- How to apply: receiver/radio tests gate on battery detection or user acknowledgment

**Known zero-implementation path:**
- BB analyst motor asymmetry signal (#4) not yet plumbed to output
- MSP_MOTOR (104), MSP_MOTOR_TELEMETRY (139) are new work
- Why: signal exists in analyst logic but no motor data path from droneteleo yet
- How to apply: future session — integrate BB analyst signal #4 into JARFACE output

