#!/bin/bash
# SessionStart tripwire: warn if a bare ANTHROPIC_API_KEY is present in session env.
#
# Why: ~/.zshrc deliberately does not export ANTHROPIC_API_KEY, but a tmux server
# started BEFORE the 2026-08-08 removal keeps the old value in its global environment
# and re-injects it into every new pane. That is invisible from .zshrc alone and made
# spawned sessions look clean while `env` still carried the key (found 2026-08-09).
#
# Anything that is not Claude Code (python anthropic SDK, curl, eval harnesses) will
# happily bill a bare ANTHROPIC_API_KEY. Claude Code itself ignores it only because the
# key tail sits in customApiKeyResponses.rejected in ~/.claude.json -- a *new* key would
# not be rejected and would silently take auth precedence over the Max subscription.
#
# NEVER print the value. A PostToolUse audit hook logs the first 120 chars of tool_input,
# and this output lands in the session transcript on disk. Presence and length only.
#
# Output goes to STDOUT, not stderr. A SessionStart hook that exits 0 has its stdout
# surfaced as session context; stderr is discarded on success. infra-health-check.sh does
# the same thing (plain `echo` + `exit 0`) and its ALERT is what reaches the transcript.
# Writing this to stderr would ship a tripwire that never fires visibly.

set -uo pipefail

if [ -n "${ANTHROPIC_API_KEY:-}" ]; then
  len=${#ANTHROPIC_API_KEY}
  cat <<EOF
[anthropic-key-tripwire] WARNING: ANTHROPIC_API_KEY is set in this session's environment (length ${len}).
  This should be empty. A bare Anthropic key can take auth precedence over the Claude Max
  subscription and will be billed per-token by any non-Claude-Code consumer.
  Most likely source: a tmux server started before the key was removed from ~/.zshrc.
  Fix (clears it for all NEW panes; existing processes keep it until restarted):
      tmux set-environment -g -r ANTHROPIC_API_KEY
      tmux set-environment -g -u ANTHROPIC_API_KEY
  Then verify:
      tmux new-session -d -s __t 'sh -c "env | grep -q ANTHROPIC_API_KEY && echo DIRTY || echo CLEAN"'
  See: memory/playbooks/cross_model_agent_coordination.md
EOF
fi

exit 0
