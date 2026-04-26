# Skills

Skills are prompt files loaded into Claude's context when invoked via `/skill-name`. The SKILL.md files are execution procedures — they stay lean by design. This README is the human-readable index.

---

## compact-checkpoint

Saves a session summary before running `/compact`, so context survives the compaction.

**When to use:** When context is getting heavy and you need to `/compact`, but want a written record of what was in progress. Use instead of plain `/compact` whenever there's meaningful state to preserve. Unlike `/snapshot`, this triggers an immediate `/compact` after writing.

**Invoke:** `/compact-checkpoint`

---

## critic

Adversarial reviewer — finds what's wrong, not what works.

**When to use:** When you want a harsh second opinion on a plan, config, architecture decision, or code. Unlike `/review` (which is balanced), Critic adopts an adversarial stance and outputs blockers, majors, and minors. Ends with a SHIP / REWORK / SCRAP verdict.

**Invoke:** `/critic` followed by the thing to tear apart (paste plan, code, or describe what to review)

---

## debug-agent

Focused diagnostic workflow for a specific OpenClaw agent.

**When to use:** When an OpenClaw agent is misbehaving — wrong outputs, tool failures, permission errors, silent exits. Spawns a Seymour subagent to pull identity, config, and recent session errors without reading sensitive config wholesale.

**Invoke:** `/debug-agent <agent-id>` (e.g. `/debug-agent bob`)

---

## deploy-task

Governance wrapper for deploying changes to the live OpenClaw system.

**When to use:** Any time a change touches a running agent, live config, or shared infrastructure. Enforces the read-GOVERNANCE → task-envelope → dry-run → explicit-go-ahead → evidence flow. Use this instead of making changes directly whenever the live system is involved.

**Invoke:** `/deploy-task` — describe the change after invoking; the skill walks through the governance steps

---

## openclaw-status

Snapshot of the live OpenClaw system state.

**When to use:** At session start, after a restart, or when something seems off. Reports gateway status, BlueBubbles status, channel enable/disable state, and recent agent session activity. Claude invokes this automatically at session start per CLAUDE.md instructions.

**Invoke:** `/openclaw-status`

---

## snapshot

Writes a handoff file capturing current session state, without compacting.

**When to use:** When you want to preserve session context for the next session but aren't ready to compact. Unlike `/compact-checkpoint`, this does NOT trigger `/compact` — it just writes the file. Use it mid-session to checkpoint or at natural stopping points.

**Invoke:** `/snapshot` — Claude picks the name and writes to `~/.openclaw/workspace/HANDOFF-{name}-{datetime}.md`
