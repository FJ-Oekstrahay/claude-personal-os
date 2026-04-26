---
name: OSD bare element verification gap
description: OSD bare assignments (osd_item_pos_*) can't be verified by existing set-form loop; known limitation in apply/verify cycle
type: feedback
---

## Pattern

OSD elements in Betaflight have two configuration forms:

1. **Set form:** `set osd_<element>_enabled=1/0` (existing CLI set commands, verified by `get osd_<element>_enabled`)
2. **Position form:** `osd_item_pos <element_index> <row> <col>` (bare command, no setter equivalent)

The apply/verify cycle in `agent.py:run_session()` → `build_context.py:apply_fc_config()` handles set-form params by reading them back via `get` commands. Position assignments (`osd_item_pos_*`) are written to FC but cannot be verified — there is no `get osd_item_pos` equivalent; position state lives only in FC memory.

## Why this matters

**Symptom:** An OSD profile applies successfully (no CLI errors), but the agent can't confirm that position changes took effect. The apply/verify loop skips position validation, creating a gap between "CLI said OK" and "position actually set".

**Risk:** If pilot confirms an OSD profile change without verification, and the position assignments silently failed (e.g., due to a firmware bug or MSP issue), the agent won't catch it. Pilot has to manually check goggles to catch the failure.

**Session context:** Session 2026-04-23 built OSD profile library with APPROVED spec requiring position changes. Implementation discovered that `osd_item_pos` (bare command) can't be round-tripped for verification.

## How to apply

1. **Document in AGENT_SYSTEM:** Add a note explaining OSD position limitations:
   ```
   OSD element positions can be changed via bare commands (osd_item_pos_row, osd_item_pos_col),
   but these cannot be verified by reading them back (no read-equivalent command exists).
   After applying an OSD profile, you cannot automatically confirm position changes succeeded.
   Pilot must visually inspect goggles to confirm.
   ```

2. **At verification time:** If OSD profile contains position changes, skip automatic verification and ask pilot for manual confirmation:
   ```python
   if 'osd_item_pos' in profile:
       build['osd_apply_result'] = {
           'status': 'applied',
           'requires_manual_verification': True,
           'reason': 'position changes cannot be auto-verified; pilot must check goggles'
       }
   ```

3. **Longer-term:** Investigate Betaflight firmware to see if `osd_item_pos` can be read back (may require firmware enhancement, not in scope for v1)

4. **Session state:** Use `_last_action_was_osd` flag to gate agent re-entry into the profile (don't re-offer same profile in same session if already applied)

## Example

**Correct flow (manual verification):**
```
Agent: "Switching to high-latency OSD (row/col positions will change)"
Agent: [applies profile via bare commands]
Agent: "Position changes applied. Check goggles to confirm placement looks correct."
Pilot: "Looks good" or "Revert"
Agent: [acts on feedback]
```

**Wrong flow (auto-verification that can't work):**
```
Agent: "Switching to high-latency OSD"
Agent: [applies profile]
Agent: [tries to verify positions by reading back]
Agent: [reads back fail — no read command exists]
Agent: [incorrectly tells pilot "position change failed"]
```

## Backlog

- Investigate Betaflight firmware: can `osd_item_pos` state be queried? File enhancement request if not.
- If firmware adds position readback, this playbook becomes obsolete (remove from index).

## Related

- [[osd_coordinate_validation]] — validating OSD coordinates before sending
- [[agent_first_feature_design]] — agent-owned OSD profile workflow
