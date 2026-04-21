---
name: Data philosophy
description: Standing principle for all data collection decisions in droneteleo — what we collect, how, and the cultural norm around it
type: feedback
originSessionId: dcd9075b-bb37-4ba0-a297-7d9ee122a171
---
All non-personal data is ours to learn from. Data gathering is woven into daily product operation, not a separate user action.

**Why:** Manifesto established 2026-04-17 after CTO + Gadfly + Architect review session. Backed by JetBrains, GitHub Copilot, Spotify precedents.

**How to apply:**
- Silent collection via ToS clickwrap is the consent mechanism — not per-action prompts
- JARFACE_LEARNING=off is the env var escape hatch (buried in ToS footnote + --help, not surfaced in UI)
- No UI toggle — toggles cue users to turn things off
- No dedicated "contribute" command — collection is automatic
- Personal identifiers (craft names, callsigns, GPS home, free-text PII) stripped at Worker boundary before storage
- Pseudonymous install UUID (SHA256 of UUID4) not anonymous — preserves cohort features
- Blackbox logs, crash photos, long-form surveys, external account linkage, identifiable cohort surfacing require explicit opt-in
- Metrics are for selling, not for making pilots feel charitable

**Influencer conflict:** The community expects "data stays on your device" language. Our actual plan is silent collection. Resolution: Option C framing — position collection as a feature ("JARFACE gets smarter as the community tunes together"), not a side effect. Never say "data stays on your device" if it doesn't. Requires Gadfly session before any influencer outreach.
