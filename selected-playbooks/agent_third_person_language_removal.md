---
name: Agent Third-Person Language Removal
description: Remove "run X in your terminal" instructions from AGENT_SYSTEM; implement features transparently in code instead
type: feedback
---

## Rule

AGENT_SYSTEM must not instruct pilots to run CLI commands in their terminal. If a feature requires a CLI step, implement it transparently in code (in agent.py or the CLI entrypoint) so it runs *before* the agent's turn and injects results into context.

**Why:** When AGENT_SYSTEM says "Run `droneteleo blackbox pull` in your terminal," the agent becomes a meta-instruction layer, not an autonomous system. Pilots see terminal commands instead of reasoning, breaking the conversational flow. The fix is to move the operation behind the scenes.

**How to apply:** When flagging eval cases or capturing agent learnings:
1. Search AGENT_SYSTEM for phrases like "Run X", "in your terminal", "command line", "CLI command" (case-insensitive)
2. For each match, check: is this operation *already implemented in code* but just not being invoked?
3. If yes: move the invocation to agent.py or CLI entrypoint; inject results into context; update AGENT_SYSTEM to describe the *results*, not the instruction
4. If no: implement the operation in code, then inject results as above
5. Remove all third-person instructions from AGENT_SYSTEM

## Examples

**Before (stale instruction):**
```
To pull the latest blackbox logs, run: droneteleo blackbox pull
Then analyze them with: droneteleo blackbox analyze
```

**After (transparent, code-driven):**
```
Blackbox logs are automatically analyzed when you upload a .bbl file.
Results appear in build['blackbox_analysis'] with metrics for gyro peaks, 
motor desync, and vibration patterns.
```

**Before (incomplete):**
```
You can help with radio configuration. Recommend pilots run EdgeTX on their Radiomaster.
```

**After (transparent):**
```
I can read and suggest Radiomaster Boxer EdgeTX model files. When a .yml file is provided,
I analyze it and suggest adjustments based on your FC parameters and flying style.
You don't need to manually edit EdgeTX — I generate the YAML.
```

## Related

- [[agent_system_stale_capability_instruction]] — verifying code implementations before updating capability docs
- [[droneteleo_safety_philosophy]] — warn vs block distinction (this rule is about transparency, not safety gating)
- [[jarface_input_length_guard]] — related pattern: validate inputs before passing to agent, don't ask agent to reject
