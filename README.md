# claude-personal-os

My Claude Code config. Skills, commands, hooks, settings — the layer that decides what the model is allowed to do, what fires automatically, and how context survives across sessions.

It's a dotfiles repo, not a framework. There's a companion multi-agent system (OpenClaw) that some skills lean on; that's a separate repo, coming soon.

If you just want the parts that travel without OpenClaw: [`commands/review-sequence.md`](commands/review-sequence.md) (why Gadfly runs before CTO), [`commands/batchc.md`](commands/batchc.md) (parallel subagent dispatch with wave sizing), [`skills/critic`](skills/critic/) (pre-commit adversarial review), and [`LESSONS.md`](LESSONS.md) (the things that broke).

---

## What's in here

`CLAUDE.md` — what Claude Code loads on startup. Working model, behavioral constraints, tool permissions, session bootstrap. The lessons-learned section at the bottom is the most useful part of the file.

`LESSONS.md` — same content, lifted out as a standalone reference. Hook exit codes, matcher scope, git permission gotchas, file staging risks, skill design constraints. Notes from things that misbehaved in production.

`hooks/` — shell scripts wired to Claude Code lifecycle points. `protect-sensitive-files.sh` blocks writes to live config and credentials across `Write`, `Edit`, and `Bash`. `discord-notify.sh` pings Discord on file mutations and approval requests so a long session is monitorable from a phone. Design notes in [`hooks/README.md`](hooks/README.md).

`commands/` — slash commands. `review-sequence` orders adversarial reviewers correctly (gadfly first, or the CTO's plan anchors everything). `batchc` does parallel subagent dispatch with wave sizing and a merge-before-parallelize rule. `session-handoff` writes a resumption document so the next session doesn't start from zero. Full list in [`commands/README.md`](commands/README.md).

`skills/` — context-triggered tools (Claude invokes them, not the user). `critic` for pre-commit review. `gog` for Gmail/Calendar/Drive/Sheets via a locally-authenticated CLI. Several others depend on OpenClaw and are here as examples of the delegation pattern, not portable utilities. See [`skills/README.md`](skills/README.md).

---

## Playbooks

Long-term memory of the system. One file per thing that broke, pattern that worked, or constraint that emerged. Stored outside `~/.claude/` and pulled into context when a task matches the topic.

`selected-playbooks/` is a representative subset — no personal data, no customer or project-specific details. The full library is around 150 files spanning:

- Agent behavior (prompt execution quirks, third-person artifacts, confirmation loops, model selection)
- Betaflight and FC tooling (serial reconnect, MSP framing, blackbox parsing, OSD coords, CLI gotchas)
- Claude Code and the API (hook exit codes, matcher scope, rate-limit partial completion, multimodal payloads)
- Hardware interfaces (USB HID gadget mode, composite gadgets, serial contention, CDC sleep overhead)
- macOS (Homebrew venv, sed/bash gotchas, FAT32 permissions, device vs file paths)
- Build and CI (eval harness compression, dev volume flag testing, mock daemon virtual testing)
- Safety and protocol (motor test mitigations, mismatch gates, signal swallowing)
- LLM products (system prompt safety language, context injection gap, output filtering)

---

## The sync pipeline

This repo is auto-synced from my private `~/.claude` on a nightly cron. The script that does it (`sync-to-public.sh`) is in the repo — same script that produced what you're reading.

It pulls the remote, wipes the working tree (preserving `.git`), rsyncs the source while excluding sessions, memory, credentials, caches, and agent data, runs a mechanical redaction pass for personal identifiers and tokens, copies the allowlisted playbooks (explicit list, no grep heuristics), then commits and force-pushes if anything changed.

Point of the design: nothing to remember to export, sanitization is mechanical not manual, and what's here reflects the config as it actually ran last night.

The script also demonstrates a fail-closed trap pattern — any unexpected non-zero exit hits `fail()`, which logs and appends to an alert file before exiting, with the trap explicitly disarmed on clean exit so it doesn't fire twice. The exclude list (`claude-public-exclude.txt`) is in the repo too.

---

## Hook errata

Two things about Claude Code's PreToolUse hook model that the docs don't make obvious:

**Exit codes aren't symmetric.** `exit 2` blocks the tool call and surfaces stderr to the model. `exit 1` does not block — it's a non-blocking failure. If a hook is enforcing a constraint, it has to exit 2.

**Matchers cover tool names, not file operations.** `Write|Edit` won't catch `Bash` calls that write files (`cp`, `tee`, `>>`). Protecting a path means including `Bash` in the matcher and parsing the command string.

Both came from things that broke in production.

The fail-closed posture is deliberate even though a misconfigured hook blocks all tool use. Failing open would silently allow writes to protected files when the hook misbehaves. A hook that blocks everything is a visible problem; a hook that protects nothing is an invisible one. Visible problems get fixed.

---

## Background

MSEE from UVa Engineering, 30+ years in technical sales and marketing. Hardware and firmware focus — Betaflight, flight controllers, USB HID, serial protocols. I use Claude Code as a daily tool, not a platform I'm building products on. What's here is what accumulates when someone who reads and writes code, but isn't primarily a software developer, spends serious time getting this tool to work well.

The lessons-learned entries exist because the things they describe broke. That's the most honest indicator of what actually got built.

Some of this has since been productized — Anthropic and OpenAI shipped features in the past month covering patterns I was building manually. Not a surprise. Building it first is how you know the problem was real.

The companion system runs 6 named agents simultaneously across different models. Whether that's thorough or overkill depends on your perspective.

---

## OpenClaw

The companion system — multi-agent, Discord-connected, scheduled ops, named agents on different models. Not public yet. Separate repo when it lands. Several skills and commands here reference it directly.
