---
name: Discoveries architecture
description: Top-level build discoveries list; per-note discoveries are audit trail; compression is wrong solution
type: feedback
originSessionId: 8145a63b-1f79-46fc-aea9-700b34e11ae2
---
Build-specific discoveries (facts JARFACE learns about a specific craft) must be stored in a top-level `build['discoveries']` list, not only inside `session_notes` entries.

**Why:** `format_build_context()` only injects the last 3 session_notes entries. Without a top-level list, discoveries from session 4 are invisible by session 8. The top-level list is always injected regardless of age.

**How to apply:** 
- `agent.py` write-back appends new discoveries to `build['discoveries']` with dedup (same logic as before, different target)
- `build_context.py` injects the top-level list under "Build-specific discoveries:" before session notes
- Per-session-note `discoveries` field is kept for auditability; it's not used for context injection

**Session note compression is the wrong solution.** Compressing 30+ entries adds Haiku latency, loses information, and doesn't help context quality (old entries weren't being injected anyway). File size at 30 entries is ~6KB — irrelevant. Don't reimplement compression.
