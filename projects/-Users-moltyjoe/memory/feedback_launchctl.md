---
name: launchctl gateway commands
description: Correct launchctl commands for reloading the openclaw gateway plist
type: feedback
---

Use these exact commands to reload the openclaw gateway after plist edits:

```
launchctl unload ~/Library/LaunchAgents/ai.openclaw.gateway.plist
launchctl load ~/Library/LaunchAgents/ai.openclaw.gateway.plist
```

**Why:** Other launchctl approaches (`kickstart`, `bootout`) are unreliable for this service. `openclaw gateway restart` is also acceptable but these are the confirmed commands Geoff uses.

**How to apply:** Any time the gateway plist is edited (e.g., ThrottleInterval), use exactly these two commands in sequence.
