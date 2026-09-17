---
description: Bootstrap platform competence from zero — surveys first-party, bundled, and third-party capability surfaces, pins a toolchain, decides on enforcement, and produces a phased prompt set so the buildout survives across sessions.
---

# /platform-expert <platform> [-- <flags>]

Build working competence on a platform or app-development target you don't yet have installed
knowledge of — tools, doc-index knowledge, a toolchain manifest, survey docs, and (if warranted) an
enforcement hook. This is not `/become-expert` (a thinking lens — different machine entirely, do not
extend or shadow it) and not `/mmguns` (a single-topic SOTA loop scoped to one capability area
inside a project you already know how to build in). Full selection reasoning and the evidence this
command is built from: `docs/reference/PLATFORM-EXPERT-SPEC.md` in the games repo — read it once if
extending this file; every phase below traces to a dated incident recorded there. A phase you want to
add that has no row in that table is speculation; find the incident or don't add it.

## Argument parsing

`$ARGUMENTS` follows the `/mmguns` convention: everything before the first `--` is the platform name
(treat multi-word names as one concept, e.g. "Unreal Engine 5", "Cloudflare Workers"). Everything
after `--` is flags.

- (no flag) — full bootstrap: run Phase 0 inline, then generate the Phase 1–6 prompt set.
- `--phase <n>` — (re)generate a single phase's prompt file only. Use after Phase 0 has already run.
- `--status` — run the stop-condition checklist against what exists on disk for `<platform>` and
  report gaps. Produces no new files.
- `--refresh [--window <days>]` — run the staleness check (see "Refresh trigger") across this
  platform's survey docs and report which are old **and** about to be relied on. Default window 30
  days.

If no platform was given, ask for one and stop. Don't guess — a guessed platform produces a
generic survey, which is this command's named failure mode.

## Scope inference

Before Phase 0, infer where this platform's artifacts belong:

- `<docs-dir>` — this project's reference-docs directory (e.g. `docs/reference/`). If none exists,
  ask where surveys should live before writing anything.
- `<tools-dir>` — this project's tracked-mirror directory for things installed outside the repo
  (e.g. `tools/`). Read its `README.md` if present — it documents the install-step pattern to match.
- `<prompts-dir>` — this project's phased-prompt convention (e.g. `prompts/`). If the project has no
  such convention, Phase 0's output should say so explicitly and propose one rather than silently
  inventing a new location.
- `<memory-mechanism>` — however this project makes findings durable (a `memory/` directory, a
  `.claude/agent-memory/` store, a user-level `MEMORY.md`). Phase 6 needs this.

---

## Phase 0 — Scoping (run inline, before anything else)

**Do not skip this. A skipped scoping step is what makes every later phase generic** — the one
time this command's shape was proven out, the scoping answer (a specific audience, a specific
delivery constraint, a specific judge of "good enough") drove nearly every survey decision that
followed it. Worked example: `docs/reference/PLATFORM-EXPERT-SPEC.md`'s appendix.

Answer, out loud, before researching anything:

1. **What is this platform?** One or two sentences — engine/framework/cloud target, its category.
2. **What are we building on it?** The actual project, genre, or app shape — not the platform's
   full capability space. A platform has hundreds of features; only some matter to this build.
3. **What does "competent" mean here, for this build specifically?** Name the constraint that will
   filter every later survey (an audience constraint, a performance budget, a licensing boundary, a
   single-shared-instance constraint — whatever actually bites). If nothing comes to mind, that's a
   sign this step is being rushed, not that there's nothing to say.
4. **Who's the practical judge of "good enough"?** The person whose reaction settles whether output
   is right (an end user, a reviewer, a specific stakeholder) — this shapes which survey findings
   matter later.

Write the answer to `<prompts-dir>/<platform>-expert-00-scope.md` before generating anything else.
Every phase file generated after this one must open with a one-line callback to this scope, so a
session picking up phase 4 in isolation doesn't re-derive it from scratch.

---

## Phase 1 — First-party surface

**Rationale (no proper nouns):** ask the vendor's own documentation what it already ships *before*
asking the community — this is consistently the single highest-leverage step available, because
vendor doc sites disproportionately expose everything through one machine-readable index that a
generic web search does not surface as the top result.

Generate `<prompts-dir>/<platform>-expert-01-first-party.md`, instructing the executing session to:

- Find the platform's machine-readable documentation index first (an `llms.txt`-shaped file, an
  OpenAPI/API-reference index, a docs-site sitemap — whatever the vendor exposes). Search it for
  terms describing what this build needs before reading any individual page.
- Produce `<docs-dir>/<PLATFORM>-INFO-SOURCES.md`: a tiered list of where to look things up, each
  tier stating what it's actually good for and what it isn't (an API reference settles "does this
  exist"; it never settles "does this feel right" — that needs the live artifact or a played
  reference).
- Tag every source with a verification level (see "Standing rules" below) from the moment it's
  written, not retroactively.

---

## Phase 2 — Bundled / installed surface

**Rationale:** catalog what's already available in the current toolchain or environment before
building or fetching anything new — an already-installed capability discovered by accident, late,
after weeks of not using it, is pure waste that a five-minute inventory would have prevented.

Generate `<prompts-dir>/<platform>-expert-02-bundled.md`, instructing the executing session to
produce `<docs-dir>/<PLATFORM>-CAPABILITIES.md`: every bundled tool, SDK feature, or built-in
service already available, what it actually gives you, and when to reach for it. Mark anything
listed but never actually run as unverified — do not imply it works from the fact that it's
installed.

---

## Phase 3 — Third-party ecosystem

**Rationale:** this must be a phase of its own, not a sub-bullet of Phase 2. A single "survey the
ecosystem" instruction reliably collapses into whichever half (bundled or third-party) is easier to
reach from where the session already is, and the half that gets skipped is silently never revisited.

Generate `<prompts-dir>/<platform>-expert-03-third-party.md`, instructing the executing session to
produce `<docs-dir>/<PLATFORM>-THIRD-PARTY-SURVEY.md`: community libraries, plugins, or integration
packages relevant to what Phase 0 scoped this build as. For each candidate, record: license,
maturity signal, verification level, and an explicit install/adopt/skip/defer verdict with one-line
reasoning — "interesting" is not a verdict. A dead-link / unreachable section is required even if
empty, so a candidate that turns out to be gone doesn't get rediscovered as live by a later search.

---

## Phase 4 — Toolchain

**Rationale:** a toolchain gap that nobody checked for stays invisible for exactly as long as nobody
checks, and by the time it's found, work has usually already been produced without it.

Generate `<prompts-dir>/<platform>-expert-04-toolchain.md`, instructing the executing session to
produce `<docs-dir>/<PLATFORM>-TOOLCHAIN-MANIFEST.md` with one row per conventional category for
this kind of platform, each marked measured / unverified / declined-with-reason (never silently
absent):

version pinning · package manager · linter · formatter · type/schema checker · test runner ·
build/sync or deploy path

A category legitimately not applicable to this platform still gets a row saying so — an omitted row
reads as "nobody checked," which is exactly the failure this phase exists to prevent.

---

## Phase 5 — Enforcement

**Rationale:** a written reminder that a check should happen, placed in project instructions, is not
an enforcement layer — it can be and has been silently skipped under normal working pressure.
Enforcement means something reads for *evidence* the check happened before allowing the action that
depended on it.

Generate `<prompts-dir>/<platform>-expert-05-enforcement.md`, instructing the executing session to:

1. Name this platform's two risk moments: the *reinvention* moment (about to hand-build something
   the platform or ecosystem already ships) and the *false-negative* moment (about to assert
   something is impossible without having checked).
2. Record an explicit **build / skip / defer** decision with reasoning — regardless of outcome, the
   decision itself must be written down, in the toolchain manifest from Phase 4.
3. If **build**: a hook (or platform-equivalent enforcement mechanism) that is fail-open, fires at
   most once per session/run, is scoped so it cannot fire in an unrelated project or context, and is
   verified against synthetic cases before being trusted. Hand-write it for this platform. Do not
   build or reach for a generic hook-generator framework — that machinery is only justified once a
   second and third platform buildout show the scaffolding is genuinely reused (see the spec's
   design-decision #4 for the concrete threshold).

---

## Phase 6 — Portability

**Rationale:** anything installed or configured outside the project's own tracked repository is
invisible to a second machine, a fresh clone, or a teammate — until someone needs it there and
discovers it was never written down.

Generate `<prompts-dir>/<platform>-expert-06-portability.md`, instructing the executing session to:

- For every component installed outside this repo (a global hook, a global command, a machine-level
  tool config), place a tracked copy under `<tools-dir>`, write the install steps, and add a
  `<tools-dir>/README.md` section following whatever pattern that file already establishes.
- Add one manifest row per installed component to the Phase 4 toolchain manifest, so "is this on the
  second machine" is answerable by reading one file.
- Explicitly re-check this command's own registration step (see "Registration," below) against the
  same rule — a buildout that documents portability for everything except its own launch point is
  self-undermining.

---

## Standing rules — apply across every phase above, not owned by any one of them

**Capability-claim discipline.** Before any "this platform can't do X" claim reaches a prompt, a
doc, or a final answer: two checks, not one — a check over this project's own code/config for "do
*we* already do X," and a check over the platform's own doc index for "does the platform *support*
X." Neither costs more than a few minutes; the failure this prevents costs a whole design fork built
on a false premise.

**Conflict-resolution rule.** When imported general advice (a blog post, a generic best-practices
guide, a community skill) contradicts something this project has actually measured, the measured
finding wins — *but state the specific claim on both sides before declaring a winner.* A blanket
"local always wins" rule has been shown to lose real capability when applied without stating the
claim first; type both claims, then decide.

**Verification tagging.** Every survey row, in every doc this command produces, carries a
verification level from the moment it's written: platform-authoritative (docs/API, read and cited),
readme-only (claims taken from the source's own description, unverified), unread (metadata only),
or measured (actually run/cloned/tested here). No untagged rows. A doc with no tags ages into
fiction — nothing distinguishes a citation from a rumor a year later.

**Capture loop.** A discovery that lives only as prose in a handoff or a chat turn is not durable.
Every phase that produces a genuinely reusable finding (not a one-off detail) writes it to
`<memory-mechanism>` before the phase is considered done — state which memory type it is (a
project fact, a standing-feedback rule, a reference pointer) using this project's existing type
taxonomy if one exists.

---

## Refresh trigger

Not a calendar. Fires at the moment a capability claim is about to be relied on — checking freshness
on a schedule fires when nobody is thinking about the platform, and a documented "re-check every N
weeks" list is a reminder wearing a different hat, which is the exact mechanism that already failed
once (see the spec's evidence table).

`--refresh [--window <days>]` (default 30) checks each survey doc's last **version-control commit**
date (never filesystem mtime — a fresh clone or a stray touch resets mtime and would report a
two-year-old doc as fresh) against the window. A doc past the window is flagged **only as additive
context** appended to whatever check is already about to fire (the enforcement hook from Phase 5, or
a manual capability-claim check if enforcement was skipped) — staleness alone never blocks anything
on its own.

---

## Stop condition — `--status` checks exactly this

1. Every artifact named in Phases 0–6 exists at its path.
2. Every row in every survey doc carries a verification tag; each survey doc has a dead-link /
   unverified section, present even if empty.
3. The toolchain manifest has one row per conventional category from Phase 4, none silently absent.
4. The Phase 5 enforcement decision (build/skip/defer) is recorded with reasoning.
5. Everything installed outside the project repo has a Phase 6 tracked mirror, install steps, and a
   manifest row.
6. This command's own registration pointer (see below) exists and resolves.
7. At least one durable memory entry exists recording the Phase 0 scoping answer and the top
   findings — the capture loop is closed, not left as prose only.

Report each of the 7 as pass/fail with the specific missing path or row when it fails. Do not report
a soft "mostly done" — every check is binary. Without a checklist like this the buildout has no end
state and keeps accreting phases indefinitely.

---

## Registration

State, in Phase 0's output, where the pointer to this platform's buildout goes so the next session
finds it without re-discovering it — normally one line added to whatever this project's equivalent
of a "read this first" file is (a root `CLAUDE.md`, a global instructions file). If that edit lands
outside the current project's own tracked repo (as it did for this command itself — see
`docs/reference/PLATFORM-EXPERT-SPEC.md`'s "Registration" section in the games repo for the worked
example), treat that edit itself as a Phase 6 portability item: it needs to be listed in the
install steps for a second machine, not silently assumed to already be there.
