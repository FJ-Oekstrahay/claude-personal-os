Focused debugging workflow for a specific OpenClaw agent. Usage: `/debug-agent bob`

1. Read `~/.openclaw/agents/{agent-name}/agent/IDENTITY.md`
2. Extract the agent's config block from openclaw.json using jq (do NOT read the full file — it contains live tokens):
   `jq --arg id "{agent-name}" '.agents[] | select(.id == $id) | {id, model, workspace, tools}' ~/.openclaw/openclaw.json`
3. List recent sessions: `ls -lt ~/.openclaw/agents/{agent-name}/sessions/ | head -10`
4. Read the most recent session JSONL and look for errors
5. Report: identity, model, tool config, last session summary, any errors found, suggested fixes
