---
name: Gadfly multi-pass spec review — structural changes expose new surface area
description: Specs with new user-facing commands often require two Gadfly rounds; first pass finds structural issues, second pass finds surface-area gaps
type: feedback
---

Pattern: A spec underwent Gadfly review, received structural feedback, then required a second Gadfly round after revisions. The second round found product risks that were invisible until the structural rewrite exposed new user-facing surface area.

**The incident:** Session 2026-04-22 revised `specs/osd-profile-library.md` after Gadfly Round 1 feedback. Round 1 had identified that profiles needed to be export-first (saved to disk before showing in CLI). Round 2 then found additional gaps: the export output contract wasn't specified (JSON vs YAML?), concrete field names for HD/SD detection were missing, the preview legend/abbrev map wasn't defined, and a risk existed that GPS disabling could happen without user warning.

**Root cause:** Structural changes (export-first reframing) alter the user-facing API surface. Once the structure is rewritten, new command paths and outputs become visible. Gadfly's first pass focuses on high-level correctness; the revised surface area needs a second pass because it's essentially a new spec.

**How to apply:**

For any spec involving new user-facing commands or user-modifiable data:

1. **After Gadfly Round 1:** Expect structural feedback (data flow, decision trees, command ordering)
2. **If revisions are substantial** (section rewrites, command reordering, data model changes):
   - Plan for a second Gadfly pass before sending to CTO
   - Specifically ask: "Are there new user-facing contracts or risks exposed by this restructure?"
3. **Second Gadfly focus areas:**
   - Output format details (exact field names, JSON/YAML choice, abbreviation maps)
   - Confirmation/warning UI (what does user see before irreversible operations?)
   - Data risk boundaries (what can go wrong silently?)
   - Export/import contracts (serialization format, version compatibility)

**Why:**

Gadfly sees customer friction and product risk. Structural changes to how users interact with a feature create new friction surfaces. A first pass catches the high-level flow; a second pass catches the details that customers actually see.

**When to skip the second round:**

- Gadfly Round 1 found no structural issues, only parameter/naming tweaks
- Changes are internal only (no new user-facing command, output, or file format)
- CTO has already weighed in and approved the structure

**Consequence:** Skipping the second round on structural changes risks shipping incomplete output contracts and hidden data risks.
