# Agent Model Selection

## Rule
For worker agents that must reliably follow system-prompt instructions — especially tool-use sequences (memory search, task handling) — use **Haiku minimum**. Do not use GPT-4.1-mini.

**Why:** GPT-4.1-mini cannot reliably follow system-prompt instructions when competing with user-turn imperatives. Confirmed 2026-03-25: Gerbilcheeks and Bob (both on mini) were failing to search memory before acting. Switching to `anthropic/claude-haiku-4-5` fixed it immediately. Haiku follows structured standing orders; mini does not.

**How to apply:**
- New worker agents: default to Haiku 4.5 (`anthropic/claude-haiku-4-5`)
- If an agent is consistently skipping mandatory steps (memory search, structured handoffs), check its model first before debugging prompts
- GPT-4.1-mini may still be acceptable for pure text tasks with no tool-use discipline required
- MoltyJoe-Sec (GPT-4.1) is a special case — security review, not standing orders compliance

## Lumpy research quality — structural limitation

Lumpy (Haiku + Brave Search API) only receives snippets, not full page content. This means:
- Cannot quote sources accurately — only paraphrase 2-sentence blurbs
- Cannot verify business status (open/closed), menus, or dynamic content
- "Always cites sources" in IDENTITY.md doesn't fix this — the underlying data is insufficient

**For reliable research that requires citations, full page content, or current business data:** use a Claude Code Sonnet session with WebFetch or Playwright MCP instead of delegating to Lumpy. Lumpy is acceptable for shallow lookups where approximate answers are fine.

**Long-term fix needed:** Give Lumpy WebFetch/Playwright capability + upgrade to Sonnet model.

## Current model assignments (as of 2026-03-25)
| Agent | Model |
|---|---|
| moltyjoe | claude-sonnet-4-6 |
| bob | claude-haiku-4-5 |
| gerbilcheeks | claude-haiku-4-5 |
| bridgernelson | claude-haiku-4-5 |
| lumpy | claude-haiku-4-5 |
| moltyjoe-sec | gpt-4.1 |
| moltyjoe-casual | claude-sonnet-4-5 |
| moltyjoe-public | claude-sonnet-4-5 |
| defaults.model.primary | haiku-4-5 |
