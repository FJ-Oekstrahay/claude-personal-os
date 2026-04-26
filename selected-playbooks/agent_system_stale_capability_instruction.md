# Agent System: Stale Capability Instructions vs Live Code

## Pattern
When a feature is implemented transparently in CLI code (executing *before* the agent's turn), the agent's AGENT_SYSTEM must match the live behavior. Stale "I can't do X" instructions will override what the code already does, causing the agent to follow outdated script instead of recognizing the capability.

## Why
A common architecture pattern: CLI detects a file type (e.g., `.bbl` for Blackbox logs), runs analysis before the agent sees it, and injects results into the agent's context. The agent should acknowledge what happened and reason over the results.

If AGENT_SYSTEM contains "I cannot read .bbl files" (from an earlier phase when this was true), the agent ignores both:
1. The code that already ran the analysis
2. The results already injected into context

Instead, the agent follows the stale instruction and tells the user "I can't do that" — creating a false capability gap.

## Pattern

Before writing or updating AGENT_SYSTEM instructions that say "I can't/don't do X", verify:
1. Grep the actual codebase for implementations of X
2. Trace the code path: when does it run relative to the agent's turn?
3. If it runs *before* the agent's turn, update AGENT_SYSTEM to say:
   - "Feature X is automatically analyzed before I see it. I receive results at [context location]. I reason over them by [method]."
4. If it runs *after* the agent's turn (agent output triggers it), document that: "I recommend X by [output format]. The CLI executes it."

## Examples

**Before (stale, from earlier phase):**
```
You cannot read Blackbox .bbl files directly. 
The raw CSV format has no FFT data — FFT requires Blackbox Explorer.
Recommend pilots use Blackbox Explorer for advanced analysis.
```

**After (reflects live code):**
```
Blackbox analysis happens automatically. When a .bbl file is provided:
1. droneteleo CLI detects it and runs automated analysis
2. Results are injected into your context at `build['blackbox_analysis']`
3. You reason over gyro peaks, motor desync, vibration patterns using those results
You don't need to instruct pilots to use Blackbox Explorer for these discoveries.

Known limitation: Raw CSV doesn't include FFT peaks — those are computed by Blackbox Explorer.
```

**Before (incomplete):**
```
I can read flight logs and analyze motor health.
```

**After (reflects actual data sources):**
```
Motor health analysis uses:
1. Baseline data in `build['motor_baseline']` (auto-captured at first session)
2. Current flight data injected as `build['motor_telemetry']` from MSP
3. Historical trends from `build['motor_health_log']`
I compare current against baseline + trends to flag drift >10%.
```

## How to Apply

Symptom: Agent claims inability on something the code does.

1. Search codebase: `grep -r "feature_name" cli/ specs/`
2. Trace the code path in agent.py or main CLI entry point
3. Determine: does it run *before* or *after* agent's turn?
4. Update AGENT_SYSTEM to match actual behavior
5. Test with `dt agent` to confirm the agent now recognizes the capability

## Related
- [[agent_system_prompt_execution_model]] — documenting resource ownership
- [[fc_context_key_params_visibility]] — similar pattern for parameter visibility
- [[spec_implementation_verification]] — verifying specs match code reality
