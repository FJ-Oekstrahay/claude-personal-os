# claude-personal-os

My Claude Code configuration — skills, commands, hooks, and settings. The OS layer under every session: what the model is allowed to do, what it does automatically, how context moves between sessions.

This is a dotfiles repo, not a framework. Most of the interesting parts of my AI setup live in a companion system (OpenClaw) that isn't public yet. What's here is the surface layer — and the pipeline that produces it.

---

## The sync pipeline

This repo is auto-synced from my private `~/.claude` directory on a nightly cron. The sync script:

1. Pulls the latest from this remote
2. Wipes the working directory (preserving `.git`)
3. rsyncs the source, excluding sessions, memory, credentials, caches, and agent data
4. Does a redaction pass — personal identifiers and secret tokens replaced mechanically
5. Commits and pushes if there are changes

The pattern: the repo stays current automatically, the sanitization is mechanical rather than manual, and I don't have to remember to export anything. What's here reflects the actual config as it ran last night.

The sync script itself isn't in this repo (it lives in the private side), but the exclude list is, and the CLAUDE.md has notes from the incident that prompted the fail-closed design.

---

## What's worth reading

Most skills and commands here reference a multi-agent system (OpenClaw) that isn't public yet — they're connected tissue, not standalone tools. Two exceptions:

**`commands/review-sequence.md`** — a decision tree for adversarial review ordering. Critic for implementation, gadfly for product direction, architect for structure, CTO for roadmap. The sequencing rules matter: gadfly before CTO, not after, or the CTO's plan anchors the gadfly instead of the other way around. That's not an obvious thing to write down.

**`commands/batchc.md`** — a smartbatch execution protocol for parallel subagent work. The cap rule (flag any batch hitting 6+ parallel agents, because at that count you've almost always missed a merge candidate) came from running this at scale.

**`hooks/protect-sensitive-files.sh`** — `PreToolUse` hook that fires on every `Write`, `Edit`, or `Bash` call. Checks the target path or command against protected patterns and exits 2 to block. Fails closed: if python3 isn't available or the JSON is malformed, it blocks rather than allows. The exit-code choice (`2` not `1`) is load-bearing — Claude Code's hook model treats them differently.

**`CLAUDE.md`** — the session-level instructions. The lessons-learned section at the bottom is the most honest part: `exit 2` vs `exit 1` in hooks, why `Write|Edit` as a hook matcher misses `Bash`-based writes (`cp`, `tee`, `>>`), a private key found inside a file that looked like a device ID. Things that broke, written down.

---

## Background

MSEE from UVa Engineering, 20+ years in technical sales and marketing. I use Claude Code as a daily tool, not as a platform I'm building products on. The config here is what happens when someone who can read and write code — but isn't primarily a software developer — spends serious time figuring out how to make this tool work well.

The lessons section is the clearest signal of actual use. Those aren't things I read in a guide.

---

## OpenClaw

The companion system — multi-agent, Discord-connected, scheduled ops, named agents on different models — is not public yet. When it is, it'll be in a separate repo. Several skills and commands here reference it directly.
