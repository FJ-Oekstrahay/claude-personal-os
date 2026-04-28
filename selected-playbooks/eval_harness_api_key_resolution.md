---
name: Eval Harness API Key Resolution
description: Eval harness inherits shell ANTHROPIC_API_KEY instead of droneteleo api.json; use prompt_key_source() guard
type: playbook
---

# Eval Harness API Key Resolution

## The Problem
The eval harness was picking up whatever `ANTHROPIC_API_KEY` happened to be set in the parent shell, instead of using the droneteleo-specific key from `api.json`.

When running eval via `dt eval`:
1. The shell might have a personal Anthropic key in `ANTHROPIC_API_KEY`
2. The eval harness checks `os.getenv('ANTHROPIC_API_KEY')`
3. It sees the personal key and uses that
4. Model tier routing is wrong (personal key ≠ jarface/byok tier)
5. Tests fail with confusing "wrong model" symptoms

## The Fix
In `cli/eval_cmd.py`, use a guard pattern that respects `prompt_key_source()`:

```python
# Before: blindly injects the droneteleo key
api_key = get_api_key_from_config()
os.environ['ANTHROPIC_API_KEY'] = api_key

# After: only inject if not already set
if 'ANTHROPIC_API_KEY' not in os.environ:
    api_key = get_api_key_from_config()
    os.environ['ANTHROPIC_API_KEY'] = api_key
```

This respects the shell's environment while ensuring droneteleo has its own key if none is set.

## Why This Matters
`prompt_key_source()` in `cli/agent.py` is the central API key resolution function. It checks:
1. Is there a shell env var already set? Use it.
2. Is there an `api.json` config? Use that.
3. Fall back to Anthropic default.

The eval harness was bypassing step 1, overwriting whatever the user's shell had. Now it respects the hierarchy.

## Verification
When eval tier routing feels wrong:
1. Check `echo $ANTHROPIC_API_KEY` in the shell
2. Check the key registered in `api.json` (via `dt config show`)
3. Print the key that eval_cmd actually uses
4. Verify it matches the intended source

If eval overwrites a shell key that shouldn't be overwritten, apply the guard pattern.

## Where This Lives
- `cli/eval_cmd.py` — harness startup
- `cli/agent.py` — `prompt_key_source()` (source of truth)
- `api.json` — droneteleo key config
