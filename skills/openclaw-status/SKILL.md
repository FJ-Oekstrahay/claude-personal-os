Check and report the live state of the OpenClaw system.

Spawn a Seymour agent (subagent_type: "seymour", model: "haiku") with this task:

> Run these commands and return all output verbatim:
> 1. `launchctl list ai.openclaw.gateway`
> 2. `launchctl list com.bluebubbles.server`
> 3. `lsof -i :<gateway-port>`
> 4. `ls -lt ~/.openclaw/agents/*/sessions/ 2>/dev/null | head -20`
> 5. `jq '{channels: .channels | to_entries | map({key, enabled: .value.enabled})}' ~/.openclaw/openclaw.json`
>    (Do NOT read the full openclaw.json — it contains live tokens. This jq command extracts only safe fields.)
>
> Return all output verbatim, one section per command, labeled by command number.

Wait for Seymour to finish, then report to the user:
- Gateway status (PID, exit code, whether port <gateway-port> is listening)
- BlueBubbles status
- Which channels are enabled/disabled
- Recent agent session activity (who was active, when)
- Any anomalies
