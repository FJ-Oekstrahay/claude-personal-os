---
name: FPV Influencer Strategy
description: Key influencers in FPV/Betaflight community, what they care about, approach sequencing, and data messaging conflict
type: project
originSessionId: dcd9075b-bb37-4ba0-a297-7d9ee122a171
---
## Priority influencers

| Name | Platform | Why they matter |
|---|---|---|
| Oscar Liang | oscarliang.com | Technical authority, trusted for accuracy, open-source ethos |
| Chris Rosser | Patreon, AOS RC | Engineering credibility, data-driven, methodology-focused |
| Joshua Bardwell | YouTube 200k+ | Gatekeeper for beginners, teaching-first philosophy |
| Mads Tech | YouTube ~30k, EU | European gatekeeper, privacy-forward, skeptical of hype |
| Rotor Riot | YouTube 50k+, retail | Cultural legitimacy, community leadership, Phase 4 only |
| IntoFPV mods | Forum | Grassroots credibility, firewall against spam perception |

## What drives endorsement vs. rejection

- Rewards: transparency, teaching value, respect for open-source culture, explainable recommendations
- Kills: black-box AI, "let AI do it for you" framing, data collection without disclosure, parasitic-on-BF perception

## Recommended sequencing

1. Private advisor loop: Oscar Liang + Chris Rosser — vet technical accuracy before anything public
2. Methodology white paper on a trusted platform (not JARFACE site)
3. Private beta with forum mods (IntoFPV, FPV Drone Pilots)
4. Rotor Riot partnership — Phase 4, post-credibility

## Per-influencer talking points

- **Oscar Liang**: "Every recommendation is transparent and explainable. Same physics you teach. Would you vet the accuracy?"
- **Chris Rosser**: "Built on flight dynamics data. Methodology is reviewable. We'd want your feedback."
- **Joshua Bardwell**: "Helps beginners learn *why* Betaflight tuning works — complements your teaching, doesn't replace it."
- **Rotor Riot**: "Let's grow the hobby together. Partnership that benefits both communities."
- **Mads Tech**: "Privacy-first, EU-compliant, transparent data handling."

## Critical data messaging conflict (unresolved as of 2026-04-17)

Seymour's recommended launch language: "Your flight data never leaves your device unless you choose to sync."
Our actual plan: silent collection via ToS clickwrap, JARFACE_LEARNING env var as the only opt-out.

These conflict. The community will packet-sniff the CLI. We will get caught if messaging doesn't match reality.

**Recommended resolution (Option C):** Position collection as a feature, not a side effect.
"JARFACE gets smarter as the community tunes together. Your anonymized outcomes help the next pilot with your exact board."
- Use Option A language in ToS (honest, specific)
- Use Option C framing in influencer communications

**Requires Gadfly session before any influencer outreach.**

## Why: Rising tide framing

If we lower the barrier to entry for the hobby, more people buy drones and parts, more people seek out Bardwell/Oscar Liang content. This aligns JARFACE with influencer interests — we grow their audience, they grow ours.

**How to apply:** Lead every influencer pitch with the ecosystem growth story, not the product feature story.
