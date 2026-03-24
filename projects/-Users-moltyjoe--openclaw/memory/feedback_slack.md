---
name: Slack is dead, stop flagging it
description: Don't raise Slack-related findings unless the user specifically asks about Slack
type: feedback
---

Don't worry about Slack unless the user asks. The migration to Discord is done, Slack remnants in config are known and low priority.

**Why:** the user explicitly said to stop flagging Slack issues. It's noise at this point.
**How to apply:** Skip Slack-related config inconsistencies, dead channel references, stale tokens in reviews and audits. Only raise if the user asks about Slack directly.
