# claude-personal-os

My Claude Code configuration — the skills, commands, hooks, and settings that make up how I work with Claude day to day. Think of it as the OS layer sitting under every session: what the model is allowed to do, what it does automatically, how context moves between sessions, and what tools get invoked when I ask for a code review or a deployment check.

This isn't a framework or a library. It's a dotfiles repo. You're here because you're curious how someone who actually uses this tool has set it up.

---

## What's in here

**`skills/`** — named capabilities that Claude invokes via `/skill-name`. Each is a `SKILL.md` file that defines the behavior.

- `/critic` — adversarial code and plan review. Numbered findings, severity tags (BLOCKER / MAJOR / MINOR), and a verdict (SHIP / REWORK / SCRAP). No softening, no "on the other hand." Useful specifically because it's annoying.
- `/deploy-task` — before touching anything live, forces a task envelope (what, which agent, rollback plan), a dry-run description, and an explicit "go ahead" before execution. Governance as a skill.
- `/openclaw-status` — checks the live state of the multi-agent system (gateway, agents, recent logs). Session start ritual.

**`commands/`** — slash commands stored as `.md` files. Claude reads the file when invoked.

- `/session-handoff` — writes a structured handoff file at the end of a session: what was accomplished (with file paths and diffs, not summaries), what's pending and why, gotchas encountered, lessons worth capturing. A session without a handoff is a session that leaves no trace.
- `/review-sequence` — a decision tree for which adversarial reviewer to invoke and in what order. `/critic` for implementation quality, gadfly for product direction, architect for structural choices, CTO for roadmap. The sequencing rules matter — gadfly before CTO, not after, or the CTO plan anchors everything.

**`hooks/`**

- `protect-sensitive-files.sh` — a `PreToolUse` hook that runs on every `Write`, `Edit`, or `Bash` call. Parses the tool input JSON, checks the target path or command against a list of protected patterns (credentials, secrets, env files, the BlueBubbles launchd plist), and exits 2 to block if there's a match. Fails closed: if python3 isn't available or the JSON can't be parsed, it blocks rather than allows.

**`settings.json`** — permissions (explicit allow and deny lists for git subcommands, process management, destructive ops), hooks wired to those events, and plugin config.

**`CLAUDE.md`** — the session-level instructions. Workflow defaults, memory protocol, live system warnings, and a running list of lessons learned from real incidents (wrong hook exit codes, git permission gotchas, a private key found inside a file that looked like a device ID).

---

## The sync pipeline

This repo is auto-synced from my private `~/.claude` directory on a nightly cron. The sync script (`sync-claude-to-public.sh`):

1. Pulls the latest from this remote
2. Wipes the working directory (preserving `.git`)
3. rsyncs the source, excluding sessions, memory, credentials, caches, agent data, and anything else that shouldn't be public
4. Does a redaction pass — personal identifiers replaced, secrets tokens replaced with `<redacted>`
5. Commits and pushes if there are changes

The point of this pattern: the repo stays current automatically, I don't have to remember to update it, and the sanitization step is mechanical rather than manual. I don't export a snapshot when I think of it — the content here reflects the actual config as it ran last night.

---

## Background

MSEE from UVa Engineering, 20+ years in technical sales and marketing. I came to Claude Code from a practitioner angle — I use it as a daily tool, not as something I'm building products on top of. The config here reflects what happens when someone who can read and write code, but isn't primarily a software developer, spends serious time figuring out how to make this tool work well.

The lessons section in `CLAUDE.md` is the clearest signal of that. Those aren't things I read in a guide — they're things that broke in practice and got written down so they wouldn't break again.

---

## OpenClaw

There's a companion system — a multi-agent setup with Discord integration, scheduled ops, and a set of named agents running on different models. It's not public yet. When it is, it'll be in a separate repo. A few references to it show up here because the two systems are connected.
