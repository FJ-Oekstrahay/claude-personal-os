Focused debugging workflow for a specific OpenClaw agent. Usage: `/debug-agent bob`

Spawn a Seymour agent (subagent_type: "seymour", model: "haiku") with this task:

> Investigate the OpenClaw agent named {agent-name}. Do the following and return all findings verbatim:
>
> 1. Read `~/.openclaw/agents/{agent-name}/agent/IDENTITY.md`
> 2. Run: `jq --arg id "{agent-name}" '.agents[] | select(.id == $id) | {id, model, workspace, tools}' ~/.openclaw/openclaw.json`
>    (Do NOT read the full openclaw.json — this jq command extracts only safe fields.)
> 3. Run: `ls -lt ~/.openclaw/agents/{agent-name}/sessions/ | head -10`
> 4. Read the most recent session JSONL file (full path from step 3). Scan for: errors, tool failures, unexpected exits, permission denials, any line with "error" or "failed" (case-insensitive).
>
> Return: identity summary, model + tool config, last 10 sessions list, and a digest of any errors/anomalies found in the most recent session.

Wait for Seymour to finish, then report:
- Agent identity and model
- Tool configuration
- Last session summary and any errors found
- Suggested fixes if issues were found
