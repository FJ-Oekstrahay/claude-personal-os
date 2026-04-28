# claude-personal-os

My Claude Code configuration — skills, commands, hooks, and settings. The OS layer under every session: what the model is allowed to do, what it does automatically, how context moves between sessions.

This is a dotfiles repo, not a framework. It covers the Claude-side components of the system — the configuration layer, automation, and connective tissue. There are references to a companion multi-agent system (OpenClaw) that isn't public yet, but that's coming soon.

**New here?** The patterns that transfer to any Claude Code setup: [`commands/review-sequence.md`](commands/review-sequence.md) (adversarial review sequencing — why Gadfly must run before CTO), [`commands/batchc.md`](commands/batchc.md) (parallel subagent dispatch with wave sizing), [`skills/critic`](skills/critic/) (harsh pre-commit review), and [`LESSONS.md`](LESSONS.md) (hook exit codes, matcher scope gotchas, and what broke in production). Everything else requires the OpenClaw companion system, covered in the sections below.

---

## What's here

**`CLAUDE.md`** — the session-level instructions Claude Code loads on every startup. Sets the working model, behavioral constraints, tool permissions, and the context Geoff expects at the start of each session. The lessons-learned section at the bottom is the most honest part: `exit 2` vs `exit 1` in hooks, why `Write|Edit` as a hook matcher misses `Bash`-based writes, a private key found inside a file that looked like a device ID.

**`LESSONS.md`** — the hard-won knowledge extracted from production use, standalone as a reference. Covers hook exit codes and matcher scope, git permission gotchas, file staging risks, and skill design constraints. This is the content that moved from notes and incident post-mortems into durable documentation.

**`hooks/`** — shell scripts that fire at specific lifecycle points. `protect-sensitive-files.sh` blocks writes to live config and credentials on every `Write`, `Edit`, or `Bash` call. `discord-notify.sh` sends Discord notifications on file mutations and approval requests, so you can monitor a long session from your phone without watching the terminal. See [`hooks/README.md`](hooks/README.md) for design details.

**`commands/`** — user-invoked slash commands. `review-sequence` runs adversarial reviewers in the correct order (gadfly before CTO, or the CTO's plan anchors everything). `batchc` dispatches parallel subagent work with wave sizing and merge-before-parallelize enforcement. `session-handoff` writes a structured resumption document so the next session can pick up without re-reading the full transcript. See [`commands/README.md`](commands/README.md) for the full list.

**`skills/`** — Claude-invoked tools triggered automatically by context, not explicit user commands. `critic` runs adversarial review before you commit to a plan. `gog` gives Claude access to Gmail, Calendar, Drive, and Sheets through a locally-authenticated CLI. Several skills require the OpenClaw companion system — they're included as examples of the delegation pattern, not portable tools. See [`skills/README.md`](skills/README.md).

---

## Playbooks

Playbooks are the long-term memory of the system. Each one records a specific thing that broke, or a pattern that worked, or a behavioral constraint that emerged from real use. They're stored in a separate location (outside `~/.claude/`) and loaded into context by the agent when a task matches the topic.

The format is consistent: what happened, why it happened, and how to apply the lesson going forward. They accumulate over time across different domains — firmware tooling, agent behavior patterns, API quirks, hardware interfaces, macOS gotchas.

**`selected-playbooks/`** contains a representative subset with no personal information or customer-specific context. Excluded from this folder: playbooks that reference specific systems, personal accounts, internal tooling, or project-specific operational details. What's here: technical gotchas and behavioral patterns that are broadly reusable.

The full library is ~150 playbooks across these categories:

- **Agent behavior** — prompt execution model quirks, third-person language artifacts, confirmation/contradiction loops, model selection tradeoffs
- **Betaflight / FC tooling** — serial reconnect, MSP framing, blackbox parsing, OSD coordinate validation, CLI gotchas
- **Claude Code / API** — hook exit codes, tool matcher scope, rate limit partial completion, multimodal content field handling
- **Hardware interfaces** — USB HID gadget mode, composite gadget config, serial port contention, CDC sleep overhead
- **macOS** — Homebrew venv requirement, sed/bash gotchas, FAT32 permissions, device path vs file path
- **Build / CI patterns** — eval harness compression, dev volume flag testing, mock daemon virtual testing
- **Safety and protocol** — motor test safety mitigations, protocol mismatch gate patterns, signal swallowing
- **LLM products** — system prompt safety language, context injection gap, output filtering patterns

This methodology — skills, hooks, and playbooks as a persistent knowledge layer — is being productized into software products we're actively developing. The pattern applied at the personal-config level here is the same pattern applied at the product level for end users: knowledge that accumulates through use, codified so it doesn't have to be rediscovered.

---

## The sync pipeline

This repo is auto-synced from my private `~/.claude` directory on a nightly cron. The sync script lives at `sync-to-public.sh` in this repo — the same script that produced what you're reading.

What it does:

1. Pulls the latest from this remote
2. Wipes the working directory (preserving `.git`)
3. rsyncs the source, excluding sessions, memory, credentials, caches, and agent data
4. Does a redaction pass — personal identifiers and secret tokens replaced mechanically
5. Copies selected playbooks from the workspace memory library (explicit allowlist, no grep heuristics)
6. Commits and force-pushes if there are changes

The design goal: the repo stays current automatically, sanitization is mechanical rather than manual, and there's nothing to remember to export. What's here reflects the actual config as it ran last night.

The script demonstrates the fail-closed trap pattern: any unexpected non-zero exit hits the `fail()` function, which logs the error and appends to an alert file before exiting. The trap is explicitly disarmed on clean exit so it doesn't fire twice. The exclude list (`claude-public-exclude.txt`) is also in the repo.

---

## Hook errata

Two things about Claude Code's PreToolUse hook model that aren't obvious from the docs:

**Exit codes are not symmetric.** `exit 2` blocks the tool call and surfaces your stderr message to the model. `exit 1` does not block — it's treated as a non-blocking failure. If your hook is meant to enforce a constraint, it must exit 2, not 1.

**Hook matchers cover tool names, not file operations.** A matcher of `Write|Edit` won't catch `Bash` calls that write files (`cp`, `tee`, `>>`). If you're protecting a path, the matcher needs to include `Bash` and your hook logic needs to inspect the command string.

Both of these came from things that broke in production.

One other thing worth noting: the fail-closed design of the hook is intentional even though it means a misconfigured hook blocks all tool use. The alternative — failing open — would silently allow writes to protected files if the hook misbehaves. A broken hook that blocks everything is a visible problem. A broken hook that protects nothing is an invisible one. Visible problems get fixed.

---

## Background

MSEE from UVa Engineering, 30+ years in technical sales and marketing. I use Claude Code as a daily tool, not as a platform I'm building products on. The config here is what happens when someone who can read and write code — but isn't primarily a software developer — spends serious time figuring out how to make this tool work well.

The config reflects genuine use over time, not a designed showcase. Some parts are cleaner than others. The lessons-learned section is the most honest indicator of what actually got built — those entries exist because the things they describe broke in production.

Some of what's here has since been productized — Anthropic and OpenAI have shipped features in the past month that cover patterns I was building manually. That's not a surprise. Building it first is how you know the problem was real.

The companion system runs 6 named agents simultaneously on different models. Whether that's thorough or overkill probably depends on your perspective.

---

## OpenClaw

The companion system — multi-agent, Discord-connected, scheduled ops, named agents on different models — is not public yet. When it is, it'll be in a separate repo. Several skills and commands here reference it directly.
