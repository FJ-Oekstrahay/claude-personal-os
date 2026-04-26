---
name: Gemini Live Voice Bot Patterns
description: System prompt rules, model selection, and gotchas for voice bots using Gemini Live audio streaming
type: reference
---

# Gemini Live Voice Bot Patterns

## Model selection
- **gemini-3.1-flash-live-preview**: Fast, suitable for IVR bots. Has echo bias (see below).
- **gemini-3.1-pro-live**: Higher quality, better instruction following. Use if flash echo bias persists after prompt anchoring.

## System prompt architecture

### Role anchoring (critical for flash)
Gemini Flash has a training bias toward echoing/mirroring what it hears. Anchor the role explicitly:

```
You are the CALLER, not the IVR system.
You do NOT generate IVR prompts.
You do NOT repeat what you hear.
Your job is to respond appropriately to the IVR and speak to representatives.
```

**Why**: Without explicit anchoring, flash tends to parrot the IVR instead of responding to it. This breaks call flow.

### DTMF rules must be explicit
Include specific rules about when to use DTMF vs. speech:

```
Only use DTMF (press_dtmf) for explicit menu prompts like:
- "Press 1 for English, 2 for Spanish"
- "To continue, press any key"

Do NOT use DTMF for data entry fields like member ID, NPI, or tax ID.
These systems expect voice input even if they mention digit entry.
```

**Why**: Different insurance systems have different input methods. UHC, for example, uses speech recognition for all data entry. A generic rule like "use DTMF for numeric data" will fail on these systems.

### System-specific guidance
Document the actual behavior expected from the target system:

```
**UnitedHealthcare specifics:**
- All data entry (member ID, NPI, tax ID) uses speech recognition
- Menu selections use explicit "press X" prompts — use DTMF only for those
- If a field accepts "digits or voice", prefer voice for reliability
```

### Recovery rules
Include fallback behavior for unrecognized responses:

```
If the IVR says "I didn't catch that" or asks you to repeat:
- Repeat the last input with slight variations (clearer pronunciation, different pacing)
- If it still fails after 2 attempts, say "Agent" or "Representative"
- Never loop more than 3 times on the same input
```

## Integration with Pipecat
When using Pipecat + Gemini Live:
- System prompt is the only gate against bad tool calls (DTMF/speak) — transcript-based gates are unreliable
- Gemini Live calls tools mid-stream, not at turn boundaries
- If you need to validate a tool call, do it in the tool handler, not in the frame processor

## Debugging voice bot behavior

### Echo/repeat issues
If the bot is mirroring IVR prompts:
1. Verify the system prompt includes explicit role anchoring ("You are the CALLER, not the IVR")
2. Increase the specificity: "Do NOT generate IVR prompts. Do NOT repeat what you hear. This is critical."
3. If still occurring, try `gemini-3.1-pro-live` — flash has stronger echo bias

### DTMF at wrong time
If DTMF is being sent for data entry fields:
1. Review the system prompt — check that it explicitly forbids DTMF for non-menu prompts
2. Add system-specific guidance (e.g., "UHC requires speech for member ID")
3. Test with real IVR calls, not simulated ones — the actual system's behavior may differ from expectations

### Incomplete rule implementations
Before testing, have an architect review the prompt for:
- Numeric entry fields and speech guidance
- Recovery logic for failed inputs
- Role anchoring clarity
- System-specific rules

This catches gaps before deployment on live systems.

## Related
- Prior auth bot (voice agent example): `/Users/moltyjoe/.openclaw/workspace/memory/playbooks/prior_auth_test_call.md`
- Gemini model availability: `/Users/moltyjoe/.openclaw/workspace/memory/playbooks/gemini_live_model_availability.md`
