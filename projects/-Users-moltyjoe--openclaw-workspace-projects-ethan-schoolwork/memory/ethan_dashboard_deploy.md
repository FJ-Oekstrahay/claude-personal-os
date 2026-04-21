---
name: Ethan Dashboard Deploy Process
description: How to update and push Ethan's homework dashboard to GitHub Pages
type: project
originSessionId: 6a8a26c2-2910-4e23-9387-ff04963e5849
---
Live URL: https://fj-oekstrahay.github.io/ethan-dashboard/

GitHub repo: https://github.com/FJ-Oekstrahay/ethan-dashboard

Source dir (IS the git repo): `/Users/moltyjoe/.openclaw/workspace/projects/ethan_schoolwork/`

Key files: `board.json` (assignment data), `index.html` (UI + logic), `images/` (static assets like planner photo)

**To push an update:**
```bash
cd /Users/moltyjoe/.openclaw/workspace/projects/ethan_schoolwork
git add <files> && git commit -m "description" && git push
```

GitHub Pages auto-deploys from main branch root within ~90 seconds.

**Note:** The old `/tmp/ethan-dashboard/` deploy flow is dead — the `ethan_schoolwork` dir is the live repo directly. Do not use the copy-to-tmp workflow.

**Why:** Pages auto-deploys from main branch root within ~90 seconds of a push.
