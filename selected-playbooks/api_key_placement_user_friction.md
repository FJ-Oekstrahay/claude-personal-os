---
name: API Key Placement for User Friction
description: When to use server-side API keys via proxy vs BYOK; audience-based decision rule
type: feedback
---

For features targeting non-developer users (e.g., FPV pilots), **server-side API keys via proxy are always preferred over BYOK config**. Do NOT offer users the option to configure their own API keys.

**Why:** FPV pilots won't tolerate the friction of:
- Signing up for external services (Brave, OpenAI, etc.)
- Obtaining API keys
- Configuring them in droneteleo
- Managing billing/rate limits

The setup barrier is high enough to reduce adoption significantly. A $0.01–0.05/query cost absorbed into droneteleo pricing is better than 50% of users never setting it up.

**How to apply:**
- New external APIs (web search, LLM lookups, image generation): use Cloudflare Worker proxy with server-side keys
- Rate limits and audit trails: implement in the Worker (KV namespace), not CLI
- User-facing side effect: feature works transparently; no setup required
- Developer/testing mode exception: ANTHROPIC_API_KEY BYOK is fine for internal eval and testing

**Decision:** Brave Search for WEBSEARCH feature uses Cloudflare Worker with server-side key (Option B). No BYOK equivalent.

**Related:** proxy rate-limit + telemetry pattern (`proxy_rate_limit_worker_pattern.md`)
