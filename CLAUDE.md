# Claude Code — session instructions (public version)

This is a trimmed copy of the `CLAUDE.md` that Claude Code loads at the start of every one of my sessions. The private version adds standing orders tied to my machines, my projects, and the people I work with; those don't transfer and aren't here. What remains is the part that would apply to anyone running a similar setup.

## Workflow

Default to plan mode for anything non-trivial. Understand the plan before execution.

Commit completed work without waiting to be asked, then fetch, reconcile, and push. Getting work pushed is the goal. Stop and ask only for a genuine content conflict; resolve mechanical ones yourself. Force-push and other destructive git operations require an explicit request every time.

When you spot something worth doing that is outside the current task, write a prompt for it to `prompts/<name>.md` in the project instead of doing it now. Every prompt states a model recommendation, run order, whether it can run as a parallel workflow, and constraints.

Before writing a multi-step manual procedure or hand-composing shell steps for a recurring check, look for existing tooling first. A script that exists but that no session knows about gets bypassed every time it matters.

## Code-quality gate

Before creating or modifying any code file, declare in one line: **THROWAWAY** or **EXTENSION**.

- THROWAWAY is one-off code that answers a question. It lives under `scratch/` and is never imported, scheduled, or referenced.
- EXTENSION becomes part of the codebase. Read the source of truth for every constant before hardcoding it, reuse an existing module if one exists, and handle the failure modes that are reachable here.
- A non-trivial EXTENSION (new abstraction, schema or interface change, shared state, new dependency, three or more files) stops and presents two or three options with trade-offs. It does not choose silently.

## Parallel work

When a turn contains two or more independent tasks, dispatch them in parallel. Before firing more than one agent at once, read the session pressure state and size the wave accordingly. Parallel agents that write files get worktree isolation. Disclose what is being applied in one line; don't block on asking.

## Subagent output discipline

Subagents return files touched and a one-line summary per file. Never relay diffs, code blocks, or file contents into the main context.

## Subagent model routing

Haiku for fully enumerated single-file edits where a wrong result is obvious on inspection. Sonnet when the spec is ambiguous, cross-file consistency matters, or the output feeds further reasoning. Opus for synthesis and judgment.

## Memory protocol

Before asking for clarification about an unfamiliar name, system, or concept, search memory first and read what it surfaces. Ask only if memory doesn't resolve it. When writing memory, link related entries with `[[wiki-link]]` syntax.

## Claims of absence

"We don't have X" is a hypothesis to falsify, not a fact to state. Before writing that something is missing or blocked on someone supplying it, search the project index, memory, and git history, and cite what was searched.

## Currency of external facts

Never state from memory what an external interface (CLI flag, API parameter, model ID, config key) does or forbids. Run `--help`, curl it, test it. Negative claims most of all. Unverified is not the same as impossible; say what you could not check.

## Verification

A check that is invariant under the defect cannot detect it. Before trusting a passing test, state what transformations leave its result unchanged. When a root cause is a shared pattern, audit every other call site before declaring the fix done. Report outcomes faithfully: if a test fails, say so with the output.

## Lessons learned

### Hooks

- PreToolUse exit codes: exit 2 blocks, exit 0 allows, anything else is non-blocking. Exit 1 does not block.
- Block reasons go to stderr. The model only sees stderr when a hook blocks.
- Matchers cover tool names. `Write|Edit` misses every Bash-based write (`cp`, `tee`, `>>`). Include `Bash` when protecting paths.
- Fail closed on a protection hook: if it can't parse its input, exit 2. Fail open on a Stop hook, for the opposite reason.
- `tool_input` is the key in the PreToolUse payload, not `input`.

### Permissions

- `Bash(git *)` auto-approves destructive git operations. Allow explicit safe subcommands instead.
- Deny rules always beat allow rules, regardless of specificity or which settings file they live in.
- Add deny rules for `kill`, `pkill`, `killall` when a live process must be protected.

### Files

- Read a file before staging it, even when it looks safe. A file that presented as a device ID contained a plaintext private key.
- A git tag does not protect untracked or gitignored files. Take a filesystem snapshot before a destructive reorganization.

### Skills

- If a skill writes to a directory, pre-create it or add `mkdir -p`.
- If a skill needs one value from a file that also holds secrets, specify the exact `jq` path. Reading the whole file puts every token in context.
