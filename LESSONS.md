# Claude Code — Lessons Learned

Hard-won knowledge from running this config in production — things that broke, burned time, or silently failed until they didn't.

---

## Hooks

**Exit codes are not symmetric. `exit 2` blocks. `exit 1` does not.**
`exit 1` is treated as a non-blocking failure — the tool call goes through anyway. If your hook is meant to enforce a constraint, it must exit 2. Using exit 1 "just in case" gives you false confidence in a hook that does nothing.

**Block reason must go to stderr, not stdout.**
Claude only sees stderr when a hook blocks. If you write your message to stdout, the model gets no explanation and you get no feedback loop. Use `echo >&2` for any message you want surfaced.

**Hook matchers cover tool names, not file operations.**
A matcher of `Write|Edit` won't catch `Bash` calls that write files (`cp`, `tee`, `>>`). If you're protecting a path, include `Bash` in the matcher and inspect the command string in your hook logic. A hook that looks correct but misses the vector it was written for is worse than no hook — it creates false confidence.

**`tool_input` is the correct key in the PreToolUse JSON payload.**
Not `input`. If your hook parses the wrong key, it silently receives nothing and makes decisions on empty data.

**Fail closed.**
If a hook can't parse its input — missing python3, bad JSON, unexpected format — exit 2, not 0. A hook that blocks everything is a visible problem that gets fixed immediately. A broken hook that protects nothing is invisible until it matters.

---

## Permissions

**`Bash(git *)` auto-approves destructive git ops.**
A wildcard allow on `git` covers `git push --force`, `git reset --hard`, `git clean -f`, and everything else. Scope permissions to explicit safe subcommands if you need to allow git at all.

**Protect live processes with explicit deny rules for kill signals.**
Add deny rules for `kill`, `pkill`, `killall` when a running service must stay up. Without them, a process kill is just another allowed Bash call.

---

## File Safety

**Read files before staging, even when they look safe.**
`identity/device.json` looked like a non-secret device identifier. It contained a plaintext private key. The filename tells you nothing about the contents. Read it before `git add`.

---

## Skills and Tools

**If a skill writes to a directory, pre-create it or add `mkdir -p` to the skill.**
Directories don't create themselves. A skill that writes to a nonexistent path fails silently or noisily depending on the tool — either way it fails. The skill should be self-contained.

**When a skill needs data from a secrets-containing file, specify the exact `jq` path.**
Don't instruct reading the whole file. If a skill reads `openclaw.json` to get one API key, the entire file — including all other tokens — ends up in context. Extract what you need: `jq '.path.to.key' file.json`.
