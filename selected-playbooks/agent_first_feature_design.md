---
name: Agent-first feature design pattern
description: When building features accessed both by agent and CLI, design the agent loop first; CLI is fallback only
type: feedback
---

## Rule

Features accessible via both agent session and CLI should be designed with agent-owned workflow first. CLI subcommands are fallback-only when the pilot directly calls them — the primary loop runs through session state management.

**Pattern:** Agent holds state (e.g., `_osd_backup_path`, `_last_action_was_osd`) and drives the workflow loop (backup → apply → verify → confirm/restore). CLI subcommands (`dt osd apply`, `dt osd restore`) exist for direct use but are not the primary path.

**Why:**

Session 2026-04-23: OSD profile library shipped with agent-managed loop: pilot says "switch to high-latency OSD", agent captures current backup, applies profile, waits for pilot feedback from goggles, then confirms or restores if pilot rejects. This lives entirely in agent session state machine (`agent.py:run_session()`).

Direct CLI access (`dt osd apply <profile>`) exists but is secondary — pilot rarely uses it directly because the agent loop is more user-friendly (pilot gets asked for confirmation, agent handles rollback).

If the feature was designed CLI-first, the agent would be calling subcommands instead of owning state, leading to less agency and worse UX (no confirmation, no automatic rollback, more manual steps).

## How to apply

When designing a feature that touches both agent and CLI:

1. **Identify agent ownership:** What session state needs to persist across turns? (e.g., backup path, last action type, pending user decision)
2. **Design the agent loop first:** Write out the state machine in `agent.py:run_session()`:
   - Pilot triggers with natural language: "use high-latency OSD"
   - Agent sets session state flags, runs apply operation
   - Agent waits for pilot feedback (goggles view, `confirm` command, etc.)
   - Agent makes final decision (confirm or restore)
3. **CLI as fallback:** Implement bare subcommands for direct use only (no state management, no rollback logic)
4. **Scope boundary:** If a feature has no natural rollback point or confirmation step, it belongs in CLI-only, not agent-first

## Example

**OSD Profile Library (correct — agent-first):**
```
Agent state:
  _osd_backup_path = /tmp/osd_config_backup_2026_04_23.txt
  _last_action_was_osd = True

Pilot: "Switch to high-latency OSD"
Agent: [backs up current config]
       [applies high-latency profile]
       [injects: "OSD switched. Check goggles. Say 'keep' or 'revert'."]
       [awaits pilot feedback]

Pilot: "Revert"
Agent: [restores backup from _osd_backup_path]
       [confirms restore]

CLI fallback: dt osd apply high-latency
  (direct apply, no backup, no rollback)
```

**Motor Test (correct — CLI-only, no agent state):**
Motor testing doesn't have a rollback step (motors run; you observe). So it stays CLI-only. Agent can call it transparently (`dt motor test <motor_id>`) if needed, but there's no session state loop.

## Related

- [[agent_system_stale_capability_instruction]] — keeping AGENT_SYSTEM in sync with feature design
- [[agent_context_error_injection_gap]] — error handling in agent-owned features
