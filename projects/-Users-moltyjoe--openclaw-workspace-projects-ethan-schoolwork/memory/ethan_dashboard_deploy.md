---
name: Ethan Dashboard Deploy Process
description: How to update and push Ethan's homework dashboard to GitHub Pages
type: project
---

Live URL: https://fj-oekstrahay.github.io/ethan-dashboard/

GitHub repo: https://github.com/FJ-Oekstrahay/ethan-dashboard

Source file: `/Users/moltyjoe/.openclaw/workspace/projects/ethan_schoolwork/ethan-dashboard.html`

Deploy dir: `/tmp/ethan-dashboard/` (index.html is the renamed copy)

**To push an update:**
```bash
cd /tmp/ethan-dashboard && cp ~/.openclaw/workspace/projects/ethan_schoolwork/ethan-dashboard.html index.html && git add index.html && git commit -m "update" && git push
```

Note: git remote URL has PAT embedded. If PAT expires, re-auth with new token:
```bash
cd /tmp/ethan-dashboard && git remote set-url origin https://FJ-Oekstrahay:<PAT>@github.com/FJ-Oekstrahay/ethan-dashboard.git
```

PAT is saved at `~/.openclaw/secrets/github_pat` (fine-grained, scoped to this repo, Contents + Pages R/W).

GitHub account: FJ-Oekstrahay (Geoff's GitHub)

**Why:** Pages auto-deploys from main branch root within ~90 seconds of a push.
