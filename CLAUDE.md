# Claude Code — Personal OS Config

This is a personal Claude Code configuration — skills, commands, hooks, and a memory system built up through daily use. It's designed as a personal AI OS: the config layer that makes Claude Code act as an always-available engineering partner. See the `skills/` and `commands/` directories for what's available.

This config integrates with OpenClaw, a separate multi-agent system (separate repo, coming soon).

## Workflow

Default to **plan mode** (Shift+Tab twice) for anything non-trivial. Understand the plan before execution.

## Memory protocol

Before asking for clarification about any unfamiliar name, system, or concept relevant to the project — check the memory index first, then read relevant files. Only ask if memory doesn't resolve the question.

## Lessons Learned

### Claude Code hooks

- PreToolUse hook exit codes: **exit 2 blocks**, exit 0 allows, anything else is non-blocking. exit 1 does NOT block.
- Block reason must go to **stderr** (`echo >&2`), not stdout. Claude only sees stderr when a hook blocks.
- Hook matcher covers tool *names* (`Write`, `Edit`, `Bash`). A matcher of `Write|Edit` misses all Bash-based writes (`cp`, `tee`, `>>`). Always include `Bash` if protecting file paths.
- Fail closed: if a hook can't parse its input (missing python3, bad JSON), exit 2, don't exit 0.
- `tool_input` is the correct key in the PreToolUse JSON payload (not `input`).

### Permissions

- `Bash(git *)` auto-approves destructive git ops (`push --force`, `reset --hard`, `clean`). Use explicit safe subcommands instead.
- Always add deny rules for `kill`, `pkill`, `killall` when a live process must be protected.

### Files before staging

- Read files before staging in git, even if they look safe. `identity/device.json` appeared to be a non-secret device ID but contained a plaintext private key.

### Skills that reference files/directories

- If a skill writes to a directory, either pre-create it or add `mkdir -p` to the skill. Directories don't create themselves.
- If a skill needs data from a secrets-containing file, specify the exact `jq` path to extract — don't instruct reading the whole file. Tokens end up in context.
