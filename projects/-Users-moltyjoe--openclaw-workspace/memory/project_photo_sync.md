---
name: photo_sync
description: Sales automation photo sync — gog Drive API setup, auth, scripts, cron
type: project
---

Photo sync pipeline moves iPhone photos from Google Drive to sales_automation inbox via gog API.

**Scripts:**
- `~/.openclaw/workspace/projects/sales_automation/scripts/photo-sync.sh` — core sync (gog API, tracks by Drive file ID)
- `~/.openclaw/workspace/projects/sales_automation/scripts/photo-sync-notify.sh` — wrapper with Discord webhook notification

**Cron:** `0 8-20 * * *` (top of hour, 8am–8pm local)

**Manual sync:** `bash ~/.openclaw/workspace/projects/sales_automation/scripts/photo-sync.sh`

**Source:** Google Drive `My Drive/Sales Automation/Photos-in/iPhone/Recents` (folder ID: `1rihG8BmIqg-Ja7wD0utFGhD6YvUveyo1`) via account `joe.moltson@gmail.com`

**Destination:** `~/.openclaw/workspace/projects/sales_automation/artifacts/raw/inbox`

**Why API not filesystem:** Google Drive is in Stream mode — files appear in the mount but `cp`/`rsync` time out (`mmap: Operation timed out`). gog API downloads reliably.

**Auth gotcha:** gog auth for `joe.moltson@gmail.com` is a refresh token in keychain. If it expires, re-run:
```
gog auth add joe.moltson@gmail.com --services drive,gmail
```
Choose joe.moltson account in the browser OAuth flow (not geoff.k.hoekstra).

**Discord notification:** Requires `DISCORD_WEBHOOK_URL` in `~/.openclaw/secrets/photo-sync.env`. Not yet configured — sync works, notifications skipped.
