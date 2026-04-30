# claude-personal-os

A personal Claude Code "OS" — skills, commands, hooks, and playbooks built up through daily use and published so others can learn from or adapt the patterns. Not a framework, not a template. One person's actual config, warts included.

There's a private `~/.claude` directory where this all actually lives. This repo is a sanitized mirror of the portable parts, auto-synced nightly via `sync-to-public.sh`. The sync is mechanical — automated redaction and an allowlist for playbooks — not a manual curated export. What you're reading reflects the config as it ran last night.

---

## What's in here

**`CLAUDE.md`** — the session-level instructions Claude Code loads on every startup. Sets behavioral constraints, tool permissions, and the context expected at the start of each session. The lessons-learned section at the bottom is the most honest part.

**`LESSONS.md`** — hard-won knowledge extracted from production use, kept standalone as a reference. Hook exit codes, matcher scope gotchas, git permission footguns, file staging risks, skill design constraints. These entries exist because the things they describe broke in production.

**`hooks/`** — shell scripts that fire at specific lifecycle points. `protect-sensitive-files.sh` blocks writes to live config and credentials on every `Write`, `Edit`, or `Bash` call. `discord-notify.sh` streams Claude's session activity to Discord in real time — tool call summaries and narrative blocks — so you can monitor a long session from your phone. See [`hooks/README.md`](hooks/README.md).

**`commands/`** — user-invoked slash commands. `review-sequence` runs adversarial reviewers in the correct order (Gadfly before CTO, or the CTO's plan anchors everything). `batchc` dispatches parallel subagent work with wave sizing and merge-before-parallelize enforcement. `session-handoff` writes a structured resumption document so the next session can pick up without re-reading the full transcript. See [`commands/README.md`](commands/README.md).

**`skills/`** — Claude-invoked tools triggered automatically by context, not explicit user commands. `critic` runs adversarial review before you commit to a plan. Several skills require the OpenClaw companion system — included as design examples, not drop-in tools. See [`skills/README.md`](skills/README.md).

**`selected-playbooks/`** — a representative subset of the full playbook library (~150 total), stripped of personal context. Playbooks are the long-term memory of the system: what broke, why it broke, and how to apply the lesson going forward. Format is consistent: fact, why it happened, how to apply. Categories: agent behavior, Claude Code/API quirks, hardware interfaces, macOS gotchas, build/CI patterns, safety and protocol, LLM product patterns.

---

## What's portable vs. what requires OpenClaw

OpenClaw is a separate multi-agent system — not in this repo. Several skills and commands here delegate to it or depend on its infrastructure (Discord bot, named agents, gateway).

**Portable — usable by anyone:**
- `critic` skill — adversarial pre-commit review
- `batchc` command — parallel subagent dispatch protocol
- `review-sequence` command — adversarial reviewer sequencing
- `protect-sensitive-files.sh` hook — blocks writes to protected paths
- `discord-notify.sh` hook — streams session activity to Discord (needs your own bot token)
- Most playbooks in `selected-playbooks/`
- `LESSONS.md` in its entirety

**Requires OpenClaw:**
- `deploy-task` skill — enforces the OpenClaw governance model
- `debug-agent` skill — reads OpenClaw agent sessions and identity files
- `gog` skill — delegates to a locally-installed CLI (`gog`) with a Google Workspace auth binding
- `new-discord-session` command — targets an OpenClaw Discord bot binding
- `personal-infrastructure/` skills — all OpenClaw-specific, included as delegation pattern examples

The OpenClaw-specific stuff is included because the patterns are worth seeing even if the infrastructure isn't public yet. When it is, it'll be in a separate repo.

---

## The sync pipeline

This repo is auto-synced from my private `~/.claude` directory on a nightly cron. The sync script is `sync-to-public.sh` — the same script that produced what you're reading.

What it does:

1. Pulls the latest from this remote
2. Wipes the working directory (preserving `.git`)
3. rsyncs the source, excluding sessions, memory, credentials, caches, and agent data
4. Does a redaction pass — personal identifiers and secret tokens replaced mechanically
5. Copies selected playbooks from the workspace memory library (explicit allowlist, no grep heuristics)
6. Commits and force-pushes if there are changes

The design goal: the repo stays current automatically, sanitization is mechanical rather than manual, and there's nothing to remember to export. The exclude list (`claude-public-exclude.txt`) is also in the repo if you want to see what gets stripped.

The script uses a fail-closed trap pattern: any unexpected non-zero exit hits a `fail()` function that logs the error before exiting. The trap is explicitly disarmed on clean exit so it doesn't fire twice.

---

## Hook errata

Two things about Claude Code's PreToolUse hook model that aren't obvious from the docs:

**Exit codes are not symmetric.** `exit 2` blocks the tool call and surfaces your stderr message to the model. `exit 1` does not block — it's treated as a non-blocking failure. If your hook is meant to enforce a constraint, it must exit 2, not 1.

**Hook matchers cover tool names, not file operations.** A matcher of `Write|Edit` won't catch `Bash` calls that write files (`cp`, `tee`, `>>`). If you're protecting a path, the matcher needs to include `Bash` and your hook logic needs to inspect the command string.

Both of these came from things that broke in production.

The fail-closed design of the hook is intentional even though it means a misconfigured hook blocks all tool use. The alternative — failing open — would silently allow writes to protected files if the hook misbehaves. A broken hook that blocks everything is a visible problem. A broken hook that protects nothing is an invisible one. Visible problems get fixed.

---

## Background

MSEE from UVa Engineering, 30+ years in technical sales and marketing. I use Claude Code as a daily tool, not as a platform I'm building products on. The config here is what happens when someone who can read and write code — but isn't primarily a software developer — spends serious time figuring out how to make this tool work well.

The config reflects genuine use over time, not a designed showcase. Some parts are cleaner than others. The lessons-learned section is the most honest indicator of what actually got built — those entries exist because the things they describe broke in production.

The companion system runs 6 named agents simultaneously on different models. Whether that's thorough or overkill probably depends on your perspective.
