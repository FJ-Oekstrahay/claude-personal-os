# Launchd Git Backup Cron Setup

## Context
The workspace nightly auto-commit job (`ai.openclaw.workspace-git-commit`) runs daily via launchd, but was silently failing every night because the git remote wasn't configured. The script uses `set -euo pipefail`, so `git push` failures cause a silent exit.

## Pattern
When setting up a launchd cron for git backup:
1. **Verify the remote exists first** — check `git remote -v`. If empty, the push will fail silently.
2. **Add the remote before testing the cron** — use `gh repo create --private --source=. --remote=origin --push` for GitHub repos (sets up remote AND pushes all history in one command).
3. **Don't modify the script** — `set -euo pipefail` is correct for safety. The issue is missing infrastructure, not the script.

## Related files
- Launchd job plist: Check `~/Library/LaunchAgents/ai.openclaw.workspace-git-commit.plist` (or similar pattern)
- Git script location: Usually in `~/.openclaw/workspace/` or `~/.openclaw/bin/`

## Common gotcha
A silent cron failure (no error email, just missing commits) usually means the push failed, not the commit. Run the job manually to test: `launchctl start ai.openclaw.workspace-git-commit` (if debugging) or run the script directly from the terminal to see the error.
