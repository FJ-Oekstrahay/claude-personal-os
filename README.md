# claude-personal-os

Most people use Claude Code as a pair programmer. This is the config layer for using it as a virtual organization.

The setup: engineering and business background, wanted to ship products. Instead of building a traditional team, I built a virtual one — named agents with defined roles. Developer, researcher, CTO, head of growth. The shift isn't just about coding. The CTO reviews an architecture question and hands back a decision. A spec gets drafted, reviewed by Gadfly, reviewed by Critic, and only then lands on my desk. The obvious objections have already been raised and resolved before I spend time on it. The work that would normally require a team happens before the document reaches me.

This repo is the operating system that makes that work: role-based review cycles, parallel work dispatch, a playbook library that accumulates knowledge across sessions, and operator tooling for the work that happens outside the IDE.

---

## What this looks like

You're building a hardware product. You have an architecture question — you hand it to the CTO while you're still in the problem space, not after you've already committed to a direction. A spec draft goes through Gadfly (would a real user pay for this?) and then Critic (is this correct and complete?) before you read it. By the time you review, the weak points have already been surfaced. The session-handoff document means the next session starts with full context instead of re-reading a transcript.

You don't start from scratch. You don't argue with yourself about every trade-off. You don't rediscover lessons from the last project. That's the point.

---

## Who this is for

**Founders and solo operators** who are already using Claude Code and have hit the ceiling of pair programmer usage: context loss between sessions, no way to delegate beyond coding, every decision starting fresh.

**Practitioners** who want working examples of hook design, review sequencing, and parallel dispatch. The LESSONS.md and selected playbooks are useful regardless of how you use the rest.

---

## Review cycles

`review-sequence` defines four roles and the order they run:

| Role | Question |
|---|---|
| Critic | Is this correct, complete, and clean? |
| Gadfly | Would a real user buy or use this? |
| Architect | Does this structure hold under real load? |
| CTO | What should be built, and in what order? |

Sequencing matters. Gadfly runs before CTO — a polished CTO plan anchors every subsequent reviewer inside a document that's already internally coherent. Running Gadfly on the raw idea first gets unanchored pushback. CTO incorporates it.

The result: by the time you're reviewing a plan, the adversarial pass has already happened. You're reading the output, not doing the work.

---

## Parallel dispatch

`batchc` is a protocol for dispatching parallel work. It classifies tasks into parallel, sequential, or subagent work; enforces wave size limits to prevent thrashing; and requires dependency chains to be named before work starts. It prevents the common failure: pre-initializing all work at once, then hitting file conflicts and redoing it.

---

## Persistent memory

Playbooks are the long-term memory of the system. Each one captures what broke, what worked, or what constraint emerged from real use — with enough context that the lesson carries forward rather than getting rediscovered. The system loads relevant playbooks automatically based on task context.

`selected-playbooks/` contains a sanitized subset with no personal information or project-specific context. The full library is ~150 entries across:

- **Agent behavior** — prompt execution quirks, confirmation/contradiction loops, model selection tradeoffs
- **Betaflight / FC tooling** — serial reconnect, MSP framing, blackbox parsing, OSD coordinate validation
- **Claude Code / API** — hook exit codes, tool matcher scope, rate limit partial completion, multimodal content handling
- **Hardware interfaces** — USB HID gadget mode, composite gadget config, serial port contention
- **macOS** — Homebrew venv requirement, sed/bash gotchas, FAT32 permissions
- **Build / CI patterns** — eval harness compression, dev volume flag testing, mock daemon virtual testing
- **Safety and protocol** — motor test safety mitigations, protocol mismatch gate patterns
- **LLM products** — system prompt safety language, context injection gap, output filtering patterns

---

## Operator tooling

`agog` is a Claude Code skill that wraps the `gog` Google Workspace CLI. It covers Gmail, Calendar, Drive, and Sheets — defining the exact command forms, auth model, and guardrails so Claude can use them reliably. Useful when the work isn't code: reviewing what's in your inbox, scheduling around a deadline, pulling a document into a session.

`session-handoff` writes a structured resumption document at the end of a session — what was decided, what's pending, what context the next session needs. The next session reads it instead of the transcript.

---

## Governance

`protect-sensitive-files.sh` blocks writes to live config and credentials on every `Write`, `Edit`, or `Bash` call. `discord-notify.sh` sends notifications on file mutations and approval requests — useful for monitoring a long session without watching the terminal.

---

## The config files

**`CLAUDE.md`** — session-level instructions loaded on every startup. Behavioral constraints, tool permissions, and context expected at session start. The lessons-learned section at the bottom is the most honest part of the file: `exit 2` vs `exit 1` in hooks, why `Write|Edit` as a hook matcher misses `Bash`-based writes, a private key found inside a file that looked like a device ID.

**`LESSONS.md`** — production knowledge extracted into a standalone reference. Hook exit codes and matcher scope are the most commonly applicable sections.

**`hooks/`** — see [`hooks/README.md`](hooks/README.md).

**`commands/`** — see [`commands/README.md`](commands/README.md).

**`skills/`** — see [`skills/README.md`](skills/README.md).

---

## Hook errata

`exit 2` blocks a tool call and surfaces your stderr to the model. `exit 1` does not block. A matcher of `Write|Edit` won't catch `Bash` calls that write files — include `Bash` and inspect the command string.

Both from things that broke in production.

The fail-closed design is intentional. A broken hook that blocks everything is a visible problem. One that silently protects nothing isn't.

---

## Background

MSEE, 30+ years in technical sales and marketing. Engineering background meant I could read and write the code. Business background meant I cared whether it shipped.

The config here reflects real use over time, not a designed showcase. Some parts are cleaner than others. The lessons-learned section is the honest indicator — those entries exist because the things they describe broke.

---

## OpenClaw

The companion system — multi-agent, Discord-connected, named agents on different models — isn't public yet. Separate repo when it is.

---

## Sync pipeline

Auto-synced nightly from `~/.claude`. The script (`sync-to-public.sh`) wipes the working directory, rsyncs with an exclude list, does a mechanical redaction pass, copies selected playbooks from an explicit allowlist, and force-pushes if there are changes. Nothing to remember to export.
