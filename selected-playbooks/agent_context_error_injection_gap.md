# Agent Context: Error Injection Gap Pattern

## Pattern
When a CLI component (e.g., blackbox analyzer, motor baseline checker) runs and catches an error, that error must be injected into the agent's context so the agent can see it. If errors are silently swallowed, the agent sees nothing — no analysis result, no error message — and follows stale script instead of reasoning about what went wrong.

## Why
Common architecture: CLI subprocess runs analysis, catches exceptions, logs internally, but doesn't inject the failure signal into the agent context. The agent:
1. Doesn't see a result at the expected context location
2. Doesn't see an error message
3. Falls back to default behavior (often a stale instruction like "I can't do X")

From the agent's perspective, the feature didn't run — even though the code caught and handled the error.

## Pattern

When implementing a feature that:
- Runs transparently before the agent's turn
- Catches its own errors
- Injects results into context

Also inject error signals:

```python
# In agent.py or CLI entry point:
if subprocess_failed:
    build['<feature>_error'] = {
        'error_type': 'analysis_failed',
        'reason': str(exception),
        'timestamp': time.time(),
    }

# In AGENT_SYSTEM, document:
"""
Feature X may fail. If it fails, you see:
- `build['<feature>_error']` with error details
- No `build['<feature>_result']` (absence of result + presence of error indicates failure)
When you see an error, tell the pilot: "X failed because [reason]. Next steps: [suggestion]"
"""
```

## Examples

**Symptom:**
```
Pilot: "Analyze my blackbox"
Agent: "I'll analyze your blackbox" (stale script)
CLI: [runs analysis, catches exception: "bad file header"]
Agent: [sees nothing in context, follows stale script]
Agent: "Use Blackbox Explorer for advanced analysis"
```

**Fix:**

1. Catch the error in agent.py:
```python
try:
    bb_analysis = blackbox.analyze(build['blackbox_path'])
    build['blackbox_analysis'] = bb_analysis
except Exception as e:
    build['blackbox_error'] = {
        'error': 'analysis_failed',
        'reason': str(e),
        'timestamp': time.time(),
    }
```

2. Document in AGENT_SYSTEM:
```
When blackbox analysis runs, you receive either:
- build['blackbox_analysis'] — successful result with gyro FFT, motor data, etc.
- build['blackbox_error'] — analysis failed; tell pilot the reason

If both are missing: analysis hasn't run yet (no .bbl file provided).
```

3. Test: feed a corrupt .bbl file, verify agent sees the error and explains it to the pilot.

## How to Apply

When review finds "agent not aware of feature failure":

1. Check agent.py or CLI entry point for the subprocess
2. Verify error handling: is the error caught? Is it silently ignored?
3. Add: `build['<feature>_error'] = {...}` when exception occurs
4. Add context injection in main CLI initialization
5. Update AGENT_SYSTEM to document error scenarios
6. Test with a failing case to confirm agent sees and reports the error

## Related
- [[agent_system_stale_capability_instruction]] — matching AGENT_SYSTEM to code behavior
- [[agent_context_key_params_visibility]] — context visibility of data
- [[unresolved_reference_placeholder_pattern]] — when to block progress vs continue
