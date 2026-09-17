Go become a genuine expert in **$ARGUMENTS**. Not a caricature — the real thing: how a top practitioner in this field actually thinks, what they prioritize, where consensus is, and where it's contested.

**Project-specific framing:** if `.claude/become-expert-local.md` exists in this project, read it now — it supplies the domain authorities/scope, the apply-target paths, and the register-target for step 3 below. If it doesn't exist, ask what domain corpus and register location to use before proceeding.

Do this in three passes:

**1. Research to current standard.** Use the project's research discipline (`CLAUDE.md`):
- Point facts (rates, deadlines, current guidance) → Perplexity inline. Anything to stake a decision on → `/deep-research` (capped version per global CLAUDE.md). Cache everything you look up.
- Cover: the field's core framework and mental models; current authoritative guidance *and its limitations*; the primary sources a leader would actually cite (statutes/regs, published guidelines, case law, academic literature, etc. as appropriate to the domain); standard tools/strategies/interventions; live controversies and areas where practitioners disagree. Note knowledge cutoff and flag anything that may have moved since.
- For non-clinical/non-technical domains (coach, Zen master, etc.), same rigor applies: foundational texts/lineage, actual practice, common misunderstandings, how a true adept differs from a dabbler.

**2. Build the persona file.** Write `personas/[slug]_persona.md`, modeled on the existing personas in this project. Capture:
- **Identity & stance** — how this expert thinks, what they optimize for, their characteristic moves.
- **Analytical framework** — the lens they apply, the questions they ask first, what they weight heavily vs. dismiss.
- **Standards of evidence** — what they trust, what they're skeptical of. For each major claim in this section and in the analytical framework, tag it: *settled* (broad consensus, clear authority), *mainstream-but-disputed* (common practice, contested in the literature/courts), or *fringe-but-defensible* (minority view with a real argument behind it).
- **Blind spots** — be honest, not flattering. Every expert lens has failure modes; name them.
- **Falsifiability** — what specific evidence or outcome would cause this lens to revise its recommendation. Not a hedge — a concrete claim: "if X were true, I would recommend Y instead."
- **Where it agrees/disagrees with the lenses already in place** (see the local delta for which ones apply here).
- **Metadata**: `verified_as_of: [YYYY-MM-DD]`, `re_verify_before: [YYYY-MM-DD or trigger event]` — note anything flagged as potentially stale.
- If the research warrants it, also create `personas/[slug]_research_cache.md` for worked lookups, citations, and rule references, in the same format as the project's existing research caches.

**3. Apply it.** Reason about the actual situation through this lens, using the apply-target paths from the local delta. Say what this expert sees that the current lenses miss, what they'd do differently, where they'd push back on the current plan. The value is in the disagreement, not the agreement.

Any domain-specific compliance/safety gate named in the local delta (e.g. a tax-authority check, a clinical ordering gate, an anti-entrenchment discipline) still applies — a new expert lens is additive, not a license to bypass it.

**Register it:** follow the register-target instructions in the local delta so the persona is discoverable and gets read-first treatment next time.
