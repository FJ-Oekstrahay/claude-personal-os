---
name: Cloudflare Workers User-Agent bypass
description: Avoid 403 blocks on Cloudflare Workers by setting non-bot User-Agent header
type: feedback
---

Cloudflare Workers blocks requests with `User-Agent: Python-urllib/3.x` by default and returns 403.

**Fix:** Set an explicit User-Agent header to something that doesn't identify as a bot.

```python
import urllib.request

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
}
req = urllib.request.Request(url, headers=headers)
response = urllib.request.urlopen(req)
```

**Why:** Cloudflare uses User-Agent as a first-pass filter for automated traffic. Python-urllib is a known bot signature that triggers the bot filter.

**How to apply:** When making HTTP calls to Cloudflare-protected endpoints (including Droneteleo's API proxy), set User-Agent to a browser string. Already patched in `cli/ai.py`.
