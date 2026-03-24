Check and report the live state of the OpenClaw system:
1. `launchctl list ai.openclaw.gateway` — gateway launchd status (PID + exit code)
2. `launchctl list com.bluebubbles.server` — BlueBubbles status
3. `lsof -i :18789` — who's listening on the gateway port?
4. `ls -lt ~/.openclaw/agents/*/sessions/ 2>/dev/null | head -20` — recent agent activity
5. For channel status, extract only the non-sensitive fields from openclaw.json using:
   `jq '{channels: .channels | to_entries | map({key, enabled: .value.enabled})}' ~/.openclaw/openclaw.json`
   Do NOT read the full file — it contains live tokens.
6. Report: gateway status, BlueBubbles status, which channels are enabled, any anomalies
