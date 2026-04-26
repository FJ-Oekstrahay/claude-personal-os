---
name: dt Agent BYOK Key Routing
description: BYOK Anthropic keys require explicit tier check; 'jarface' string match is insufficient
type: playbook
---

# BYOK Anthropic API Key Routing in dt Agent

## The Problem
When BYOK (Bring Your Own Key) Anthropic credentials are provided, the dt agent was not routing to higher-tier models (Sonnet) because the model tier selection only checked for the string `'jarface'` in the key_type.

```python
# Old: insufficient check
if prompt_key.key_type == 'jarface':
    model = 'sonnet'  # Only JARFACE gets Sonnet
```

This meant:
- BYOK keys stayed on Haiku (the default)
- Haiku's limited reasoning caused evaluation failures
- Tests flagged as failures when they actually just hit model tier limits

## The Fix
Add BYOK to the tier check:

```python
# New: covers both JARFACE and BYOK
if prompt_key.key_type in ('jarface', 'byok'):
    model = 'sonnet'
```

When a BYOK key is detected (via `api.json` or env), it signals higher computational needs — route to Sonnet automatically.

## Where This Lives
- `cli/eval_cmd.py` — tier routing logic
- `cli/agent.py` — AGENT_SYSTEM model selection

## Why BYOK Implies Sonnet
BYOK keys come from environments where the user is either:
1. Running private eval harness (needs full reasoning)
2. Testing agent decision quality (Haiku's shortcuts are visible and fail)

Using Haiku on BYOK is cheaper but unreliable. Use Sonnet for BYOK by default.

## Verification
When you see eval failures with BYOK keys, check:
1. Is the model tier Sonnet or Haiku? (Print the model selection decision)
2. Is the api.json key registered with `key_type: 'byok'`?
3. Does the tier selection code cover `'byok'` in the conditional?

If tier is Haiku + BYOK, the fix above applies.
