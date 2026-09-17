---
name: Cloudflare Workers KV Namespace Setup
description: Creating and configuring KV namespace IDs for Cloudflare Workers before deployment
type: project
---

## Namespace ID configuration is required before deploy

**The issue:** Placeholder text like `REPLACE_WITH_KV_NAMESPACE_ID` in `wrangler.toml` causes deployment failure with error code 10042.

**Why:** Cloudflare Workers validates bindings at deploy time. The KV namespace binding requires a real, registered namespace ID — placeholders are rejected.

**How to apply:** Before running `wrangler deploy`:

1. Create the namespace: `wrangler kv namespace create RATE_LIMIT` (or your namespace name)
2. Copy the returned namespace ID
3. Paste the ID into `wrangler.toml` under the `[[env.production.kv_namespaces]]` binding
4. Deploy: `wrangler deploy`

The namespace is created first, then referenced in the Worker config. Never deploy with placeholder text.
