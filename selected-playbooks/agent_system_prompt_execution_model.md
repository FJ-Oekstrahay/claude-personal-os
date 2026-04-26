# Agent System Prompt: Documenting Execution Model

## Pattern
AI agents that execute code or commands must include an explicit "How execution works" section in their system prompt (AGENT_SYSTEM). Without it, agents will claim inability to perform actions they can actually do.

## Why
Agents have no inherent knowledge of:
- How their output is consumed (JSON blocks? shell commands? direct execution?)
- What channel owns a resource (e.g., Python CLI owns serial port to FC, not the agent directly)
- Whether execution is synchronous or async
- Latency or failure modes

When agents can't answer "what can I do with output X?", they default to claiming inability ("I have no connection", "I can't test motors"). This appears as a capability gap when it's actually a documentation gap.

## Pattern

In AGENT_SYSTEM, after role/context, add:

```
## How Execution Works

Your output is executed by [service/component]. Specifically:
- [Output format] → [What happens to it]
- Example: "JSON blocks with `"action": "test_motors"` are parsed by droneteleo CLI and executed directly"
- You own: [list of resources/capabilities you control via output]
- You don't own: [list of resources the service owns on your behalf, not directly available to you]
```

## How to Apply

When an agent bench test reveals the agent claiming inability on something it can do:
1. Check if AGENT_SYSTEM documents "How execution works"
2. If not, add it — name the service, input/output format, resource ownership
3. If unclear, run a brief agent self-test: "What are your current capabilities?" with and without the section

## Examples

**Before (incomplete):**
```
You are JARFACE, flight controller agent for droneteleo.
Your role is to help pilots configure and test aircraft.
```

**After (complete):**
```
You are JARFACE, flight controller agent for droneteleo.
Your role is to help pilots configure and test aircraft.

## How Execution Works

Your output (Python objects in JSON blocks) is executed by the droneteleo CLI (`dt agent` command). The CLI parses your JSON and runs the corresponding FC commands. Specifically:
- `{"action": "test_motors", "throttle": 1070}` → CLI executes motor test at 1070 throttle
- `{"action": "get_param", "param": "p_roll"}` → CLI reads parameter and feeds result back to you
You own: motor testing, parameter reads/writes, PID tuning
You don't own: serial port directly (CLI manages it), hardware safety checks (BF owns those)
```

## Related
- [[dt_agent_startup_diff_scope]] — agent context at startup
- [[cto_agent_adversarial_review]] — when to spawn agents for critique
