---
name: Droneteleo deployment
description: How droneteleofpv.com gets deployed — Cloudflare Pages auto-deploy via GitHub push
type: project
---

## Deploy path

droneteleofpv.com is hosted on **Cloudflare Pages**, project name `droneteleo`.

Deploy = `git push` to `github.com/FJ-Oekstrahay/droneteleo` (main branch). CF Pages auto-builds and deploys on push. No manual step needed.

**Why:** Cloudflare detects the GitHub push via webhook and re-deploys automatically.
**How to apply:** Any time index.html or site assets change, commit + push to trigger deploy.

## Account info
- CF Account ID: `bc202e1557d5b71f8db42212bffbef50`
- CF subdomain: `geoff-k-hoekstra.workers.dev`
- Pages project: `droneteleo`
- Live URL: https://droneteleofpv.com
- GitHub repo: https://github.com/FJ-Oekstrahay/droneteleo (proprietary license, may be private)
