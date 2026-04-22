# claude-personal-os

My Claude Code configuration — skills, commands, hooks, and settings. The OS layer under every session: what the model is allowed to do, what it does automatically, how context moves between sessions.

This is a dotfiles repo, not a framework. It covers the Claude-side components of the system — the configuration layer, automation, and connective tissue. There's a companion multi-agent system (OpenClaw) that isn't public yet; references to it in the skills and commands will make more sense once it is.

---

## What's here

**`CLAUDE.md`** — the session-level instructions. The lessons-learned section at the bottom is the most honest part: `exit 2` vs `exit 1` in hooks, why `Write|Edit` as a hook matcher misses `Bash`-based writes (`cp`, `tee`, `>>`), a private key found inside a file that looked like a device ID. Things that broke, written down.

**`hooks/protect-sensitive-files.sh`** — `PreToolUse` hook that fires on every `Write`, `Edit`, or `Bash` call. Checks the target path or command against protected patterns and exits 2 to block. Fails closed: if python3 isn't available or the JSON is malformed, it blocks rather than allows. The exit-code choice (`2` not `1`) is load-bearing — Claude Code's hook model treats them differently.

**`commands/review-sequence.md`** — a decision tree for adversarial review ordering. Critic for implementation, gadfly for product direction, architect for structure, CTO for roadmap. The sequencing rules matter: gadfly before CTO, not after, or the CTO's plan anchors the gadfly instead of the other way around. That's not an obvious thing to write down.

**`commands/batchc.md`** — a smartbatch execution protocol for parallel subagent work. The cap rule (flag any batch hitting 6+ parallel agents, because at that count you've almost always missed a merge candidate) came from running this at scale.

The remaining skills and commands are the connective tissue between Claude Code and OpenClaw — routing, delegation, session management, agent ops. Several of them reference OpenClaw paths that don't exist in this public repo. They're not broken — they're incomplete without the companion system. That dependency is deliberate, not an oversight, but it's worth naming directly rather than leaving it implicit.

---

## The sync pipeline

This repo is auto-synced from my private `~/.claude` directory on a nightly cron. The sync script lives at `sync-to-public.sh` in this repo — the same script that produced what you're reading.

What it does:

1. Pulls the latest from this remote
2. Wipes the working directory (preserving `.git`)
3. rsyncs the source, excluding sessions, memory, credentials, caches, and agent data
4. Does a redaction pass — personal identifiers and secret tokens replaced mechanically
5. Commits and force-pushes if there are changes

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

MSEE from UVa Engineering, 20+ years in technical sales and marketing. I use Claude Code as a daily tool, not as a platform I'm building products on. The config here is what happens when someone who can read and write code — but isn't primarily a software developer — spends serious time figuring out how to make this tool work well.

The config reflects genuine use over time, not a designed showcase. Some parts are cleaner than others. The lessons-learned section is the most honest indicator of what actually got built — those entries exist because the things they describe broke in production.

Some of what's here has since been productized — Anthropic and OpenAI have shipped features in the past month that cover patterns I was building manually. That's not a surprise. Building it first is how you know the problem was real.

The lessons section is the clearest signal of actual use. Those aren't things I read in a guide.

<!-- TODO: add 680 context — Geoff to clarify what this refers to before publishing -->

---

## OpenClaw

The companion system — multi-agent, Discord-connected, scheduled ops, named agents on different models — is not public yet. When it is, it'll be in a separate repo. Several skills and commands here reference it directly.
