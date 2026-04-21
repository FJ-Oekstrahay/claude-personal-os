---
name: Email setup for droneteleofpv.com
description: Cloudflare Email Routing config for geoff@droneteleofpv.com
type: project
originSessionId: 97de6c60-bed0-447e-bc98-5f807a5fe2e5
---
`geoff@droneteleofpv.com` forwards to `geoff.k.hoekstra@gmail.com` via Cloudflare Email Routing (free tier). Set up 2026-04-10.

**Why:** Contact address for the droneteleo site.
**How to apply:** Inbound only. Gmail SMTP outbound alias (send-as) not configured — if that's ever needed, add via Gmail Settings → Accounts → Send mail as, using smtp.gmail.com port 587.
