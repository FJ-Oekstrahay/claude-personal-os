# claude-personal-os

The Claude Code configuration I run every day: hooks that enforce rules instead of suggesting them, commands that pace parallel agent work, a roster of review agents with a deliberate order, and a knowledge library that outlives any single session. Published as a curated, reviewed snapshot of my private setup.

Companion page: **[fj-oekstrahay.github.io/claude-personal-os](https://fj-oekstrahay.github.io/claude-personal-os)**. I'm Geoff Hoekstra; more about me at the end.

---

## What this is

Claude Code loads a config directory at startup: instructions, slash commands, hooks, agent definitions, skills. Most people's version of that directory is a `CLAUDE.md` and a few aliases. Mine grew into an operating layer because I use Claude Code for real work across a dozen projects (hardware tooling, financial modelling, a shipped game, family infrastructure) and the same failures kept repeating until I made them structurally impossible.

Three ideas run through everything here:

**Enforce, don't request.** A rule written in a prompt is a request the model can drop under context pressure, usually at the moment it matters. The rules I care about live in hooks. A `Stop` hook refuses to end a session that did substantial work without writing a handoff document. A `PreToolUse` hook rejects any handoff filename with a hand-typed date, because the model kept confabulating tomorrow's date from a UTC timestamp. A file-protection hook exits 2 on writes to credentials, and it fails closed: if it can't parse its input, it blocks.

**Pace by measurement.** Two hooks track how full the context window is (read from the session log against the model's real window size, not a guess) and how many tool calls fired in the last sixty seconds. The batch-dispatch command reads both before every wave and shrinks or pauses before a rate limit hits, not after.

**Move work off the model.** Every hook here is shell or Python with no model call. The prompt-scoring nudge targets under 50 ms and uses string signals only. The memory anti-ratchet hook computes which beliefs are stale and tells the model to act on the result rather than re-derive it. I hold the same line in the products I build: if a step can be deterministic, it should be, and the user should not pay tokens for it.

### Where this stands next to native Claude Code

Anthropic ships fast, and several patterns I built have since appeared natively in some form. Hooks (June 2025), custom subagents (July 2025), auto memory (February 2026), Remote Control (by February 2026), the Workflow tool for deterministic multi-agent orchestration (by May 2026), and cross-machine session messaging (August 2026) all landed while this config was in use, and I use the native versions where they cover the need. I'm not going to claim I got there first; the changelog is public and most of those dates come before my earliest verifiable commit.

What I will say is narrower and checkable. When I built the pieces below, the native equivalent was either absent, a research preview behind an experimental flag, or still changing weekly. Agent teams entered research preview behind an experimental flag in February 2026. Remote Control saw more than half of its changelog entries in August and September 2026. Knowing when the native version has matured enough to retire your own is part of the job, and the Discord section below is an example of doing exactly that.

Still not native as of September 2026, and the reason this repo is worth reading:

| Capability | Here | Native |
|---|---|---|
| Structured session handoff, enforced by a Stop hook that blocks ending the session without one | `commands/session-handoff.md`, `hooks/batchc-stop-gate.py` | `--resume` restores a transcript; nothing writes or requires a handoff |
| Wave-sized parallel dispatch driven by live context-fill and tool-call burst rate | `commands/batchc.md`, `hooks/resource-pressure.py`, `hooks/wave-counter.py` | Workflow tool has a concurrency cap but no pressure signal |
| Adversarial review in a fixed order: product skeptic before technical planner, so the plan doesn't anchor the critique | `commands/review-sequence.md`, `agents/` | `/code-review` finds bugs in a diff; different job |
| Curated, cross-project playbook library with semantic search, synced across machines | `selected-playbooks/` (subset) | Auto memory is per-project, flat, and does not sync |
| Hooks that make specific past failures impossible: hand-typed timestamps, a stray API key in the environment, writes to credentials | `hooks/` | Sandbox and deny rules cover different ground |
| One config repo that runs correctly on two machines with different usernames | described below | Nothing native handles config portability |

---

## Start here

If you read four things: [`LESSONS.md`](LESSONS.md), [`hooks/batchc-stop-gate.py`](hooks/batchc-stop-gate.py), [`commands/review-sequence.md`](commands/review-sequence.md), and [`commands/batchc.md`](commands/batchc.md). Between them they show the enforcement idea, the pacing idea, and the review order.

If you want to lift one thing into your own setup, take [`hooks/handoff-timestamp-guard.sh`](hooks/handoff-timestamp-guard.sh). It is under a hundred lines, it targets one specific hallucination, and the comment block explains why a prompt rule was not enough.

---

## What's in the repo

**[`CLAUDE.md`](CLAUDE.md)** is a trimmed version of the instruction file Claude Code loads at every session start. The private version carries standing orders tied to my machines and projects; this one keeps the parts that transfer.

**[`LESSONS.md`](LESSONS.md)** is the shortest useful document here: hook exit-code asymmetry, why a `Write|Edit` matcher misses every `Bash` write, the file that looked like a device ID and held a private key. Each entry exists because the thing it describes broke.

**[`hooks/`](hooks/)** holds the enforcement and telemetry layer. Wiring is in [`settings.example.json`](settings.example.json), which is the hooks block from my live settings file and nothing else. Highlights:

- `batchc-stop-gate.py` blocks a session stop when substantial work happened and no handoff was written. It deliberately fails open, the opposite of the file-protection hook, because a Stop hook that fails closed wedges every session; its docstring makes the argument.
- `resource-pressure.py` and `wave-counter.py` are the two measurements the batch protocol paces on.
- `handoff-timestamp-guard.sh` and `anthropic-key-tripwire.sh` each exist because of one incident, named in the file.
- `memory-anti-ratchet.py` reads belief metadata off auto-memory files (when a belief was last challenged, by whom, how many sessions it has been carried) and, at session start, tells the model which beliefs are due for an independent challenge. It generalizes a mechanism I first built for a clinical-reasoning project.
- The `discord-*` hooks stream a session to Discord. See the Discord section for why they exist and what has changed.

**[`commands/`](commands/)** are the slash commands. `batchc` is the paced parallel-dispatch protocol. `review-sequence` decides which reviewers run and in what order. `session-handoff` and `load-handoff` are the two halves of continuity between sessions. `plan-session` proposes a wave plan and stops for approval. `mmguns` is a research-to-integration loop that ends in a dispatch, not a report. `orchcheck` and `caution` are trigger words: one pauses to pick an orchestration mechanism, the other checks for concurrent sessions before touching anything shared. `longrun` drains a feature queue with model-routed workers and is deliberately opt-in.

**[`agents/`](agents/)** defines the subagents. The review agents matter most: Gadfly (hostile product skeptic), CTO (sequencing and deferral), The Architect (structural code review, on Opus), and Safety Officer (hardware risk, whose first question on every review is "unexpected prop spin"). Cob and Seymour are the two implementation tiers, Sonnet and Haiku, and the routing rule for which one gets a task is in `CLAUDE.md`.

**[`workflows/`](workflows/)** are scripts for Claude Code's Workflow tool, where fan-out and loops are code rather than model judgment. `deep-research.js` caps the built-in research workflow at under thirty agents (the uncapped version spawns up to 97) so it stays inside subscription rate limits; the two constants that set the cap are documented with their exact per-increment agent cost. `feature-build.js` routes queued features to model tiers and encodes two platform facts I had to learn by testing: Workflow scripts have no filesystem access, and a Workflow agent cannot switch providers.

**[`skills/`](skills/)** are the auto-invoked skills I wrote myself. `critic`, `gadfly`, and `cto` wrap the review agents. `deep-research` is the capped harness's entry point. The others are small conveniences. Third-party skills I have installed are not included.

**[`output-styles/`](output-styles/)** has `engineering-rigor`, the default in any directory that runs real infrastructure: declare THROWAWAY or EXTENSION before writing code, read the source of truth before hardcoding a constant, stop and present options for any non-trivial change. `quick-explore` is the escape hatch.

**[`templates/`](templates/)** are opt-in hook and prompt templates, never auto-installed.

**[`selected-playbooks/`](selected-playbooks/)** is the public subset of the knowledge library, described next.

---

## Memory

Three tiers, on different timescales.

1. **Rules** in `CLAUDE.md`, loaded every session. The test for what belongs there: does it need to be true every time, regardless of what was discussed last?
2. **Playbooks**, more than 450 of them as of September 2026, in a private repository cloned on both of my machines. Each records what broke, why, and how to apply the lesson. A playbook gets written when a root cause wasn't obvious, a workaround wouldn't be discovered naturally, or a constraint appeared that no documentation mentions. They are indexed for semantic search, so a session can ask "have I seen this before" across every project, not just the current one. The subset here was chosen for carrying no client or personal data; a few name my own side projects (Droneteleo, this repo's own tooling) as the example context, which is a deliberate choice, not an oversight.
3. **Auto memory**, Claude Code's own per-project mechanism, plus the anti-ratchet hook above so that a corrected belief doesn't quietly revert when older entries are re-read.

Handoff documents sit between sessions. Two hooks guard them: one makes the filename timestamp impossible to hand-type, the other refuses to let a working session end without one.

---

## Two machines, one config

This directory is a git repo cloned on a Mac mini and a MacBook Air with different usernames. Everything portable is committed. Machine facts (paths, hostnames, which services run where) live in one gitignored file that the main `CLAUDE.md` imports by reference. Absolute home paths are the failure mode: when the two trees were first reconciled, eleven of twenty-seven differing files differed only in the username inside a path. The rule that came out of it is short: write `~/`, and where `~` can't expand, resolve home at runtime.

---

## Discord as a command center, and retiring it

In early 2026 I wanted to run sessions from my phone. I built it on Discord: a `PreToolUse` hook posts the model's narrative text before each tool call, a `PostToolUse` hook posts a one-line summary after, approvals page me in a channel, and a keyword-dispatch hook lets a dictated word like "batchc" trigger a slash command without typing a slash. A separate router daemon held the gateway websocket and mapped channels to sessions.

Anthropic was building the same shape at the same time. Remote Control existed by February 2026, channels shipped in March, push notifications in April. That is convergence, not precedence, and I say so because the dates are public. Remote Control now covers the monitoring case, and the router is not published here. The hooks stay in the tree because streaming every tool call to a channel is still not a native feature and because keyword dispatch by dictation is a pattern worth copying.

---

## Projects this config runs

Everything below is private except where linked. The two family-facing systems are built around my own household's needs; a general version of either is possible and not started.

**Agentic Roblox game development** ([public repo](https://github.com/FJ-Oekstrahay/agentic-roblox-gamedev)). A live, monetized Roblox game built with an AI coding agent as the primary implementer, published with about 40,000 lines of the actual Luau source, a permalinked code tour, and a candid account of what the agent structurally cannot do on a closed engine. This is the most complete public evidence of how I work.

**Droneteleo.** A command-line tool that holds a live USB connection to a Betaflight flight controller and lets a pilot tune it by describing the problem instead of hand-editing firmware parameters. Every change stages to RAM and nothing touches flash without an explicit save. A dedicated safety-review agent audits any feature that could spin a motor. The design direction I care most about: blackbox chirp detection, the signal processing behind it, and the parameter recommendations it produces are deterministic Python, and the session write-back records what changed from the command log instead of asking a model to infer it. A model narrates results and interprets logs; it does not produce the recommendations. Users pay for fewer tokens and get recommendations that don't vary run to run.

**Retirement planning engine.** A projection engine with a certified Monte Carlo core, a versioned decision registry, and a claims gate that checks every number in every report against its source before the report ships. Built and used for my own household. An interactive design study with synthetic numbers exists for showing how a spending dial interacts with a guaranteed floor.

**Health reasoning system.** A structured personal medical corpus reasoned over by specialty personas that are built to disagree with each other, under an ordering gate (specific indication, standard-of-care support, a decision that would actually change) and the anti-ratchet mechanism now generalized in this repo. The architecture is the publishable part; the data is not.

**Family infrastructure.** A Cloudflare Worker serving a shared family board, email and SMS intake workers feeding a structured wiki, an event-registration flow with a one-time-passcode gate, and a macOS screen-time daemon that had to work around the system's own notification suppression to be reliable.

**AI phone agent for prior authorization.** A proof of concept that calls an insurer's line, navigates the IVR by tone injection, and conducts the authorization conversation. Before any live call it was red-teamed against a second model playing the insurer, which caught real domain gaps. Paused since April 2026; no Business Associate Agreement is in place, so no real patient data has flowed through it.

**Bambu 3D-print settings tool** ([public repo](https://github.com/FJ-Oekstrahay/bambu-3mf-maker-with-settings)). Two Python scripts that turn an STL plus a plain-language description into a ready-to-print `.3mf`, by treating the project file as what it is (a zip of JSON and XML) and patching it directly.

---

## How this repo is produced

It is a reviewed export from my private config, not an automatic mirror. Files are copied by an explicit manifest, swept for private strings, and committed by hand after a diff review. An earlier version of this repo was auto-synced nightly with a wholesale allowlist; that pipeline is retired, and the incident that retired it is the reason the sweep exists.

A few scripts reference paths under `~/.openclaw/`. That directory predates this setup and once hosted a separate multi-agent system, since retired. Several files here still reference it — a workflow default and a few agent instructions — because that's where some of my project directories genuinely live. If you adopt this config, swap those paths for your own.

---

## Using this as a parts library

This is not an installer. Pick what fits:

- **File protection:** `hooks/protect-sensitive-files.sh`. Adjust the path list; keep `Bash` in the matcher.
- **Handoff enforcement:** `commands/session-handoff.md` plus the two hooks that guard it.
- **Paced parallel work:** `commands/batchc.md` with `resource-pressure.py` and `wave-counter.py` wired as in `settings.example.json`.
- **Review order:** copy the Gadfly-before-CTO rule from `commands/review-sequence.md` into your own instructions even if you copy nothing else.
- **Playbooks:** read a few in `selected-playbooks/` for the format, then write your own. The value is in the accumulation.

---

## About

I'm Geoff Hoekstra. MSEE from the University of Virginia, then thirty years in technical sales and marketing, which means I have spent a career translating between people who build systems and people who buy them. Since early 2026 I have been building AI systems: agent orchestration, governance and verification, and the tooling that turns a model demo into something that runs unattended. The hooks, commands, and agents here run on my machines every day.

GitHub: [github.com/FJ-Oekstrahay](https://github.com/FJ-Oekstrahay)

MIT licensed. See [`LICENSE`](LICENSE).
