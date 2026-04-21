---
name: Ask before working around web obstacles
description: When blocked by login, auth, or site issues during web automation, ask Geoff first — don't spiral into workarounds
type: feedback
---

When hitting a web obstacle (login wall, auth redirect, blocked page, Chrome conflict), ask Geoff before attempting workarounds. He can often solve it in one step (log in, quit Chrome, provide credentials).

**Why:** Geoff had to interrupt a multi-step curl/Node.js investigation that could have been solved by "can you quit Chrome?" — wasted tokens and time.

**How to apply:** Any time Playwright, WebFetch, or browser automation hits a blocker — one sentence to Geoff, then wait.
