---
name: Xactly Download Scripts
description: How to download Xactly dashboard (Excel) and order detail reports (CSV) using Playwright via CDP
type: project
---

Scripts live in: `~/.openclaw/workspace/projects/ansys-agi-synopsys/xactly-ansys/`

- `download_xactly.py` — downloads BOTH reports in sequence
- `download_orders.py` — downloads just the Order Detail CSV

Output files:
- `xactly-dashboard-YYYY-MM-DD.xlsx` — MyIncentives dashboard Excel export
- `xactly-orders-YYYY-MM-DD-HH-MM-SS.csv` — Order Detail report, all months before current month

**Prerequisites (user must do this each time):**
1. Launch Chrome with remote debugging:
   ```
   /Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome \
     --remote-debugging-port=9222 \
     --user-data-dir=/tmp/chrome-automation
   ```
2. In that Chrome window, log in to login.xactlycorp.com with 2FA
3. Confirm authentication before running scripts

**Always verify Chrome is running on port 9222 first:**
```
lsof -i :9222
```

**Run:**
```
python3 ~/.openclaw/workspace/projects/ansys-agi-synopsys/xactly-ansys/download_orders.py
```

**Known quirks:**
- The dashboard Excel download: Chrome saves it as `report.xlsx` in the DOWNLOAD_DIR (Playwright's `expect_download` captures it empty). Script renames it automatically on subsequent clean runs — but if `report.xlsx` appears in the dir, manually rename it to `xactly-dashboard-YYYY-MM-DD.xlsx`.
- Order Detail CSV only shows months where Geoff has closed orders — Jan/Feb showing empty is normal if no orders booked those months.
- The Analytics app (xianalytics) is a separate domain from Incent (xicm) — both authenticate via the same SSO session.
- `dashboardframe` uses dynamic saw_ IDs that change each page load — scripts find them by label title, not by ID.

**Why:** Geoff wants to periodically pull Xactly data for his Ansys AGI/Synopsys compensation analysis project.
**How to apply:** When Geoff says "download my xactly dashboard/orders/reports", check if port 9222 is open, confirm auth, then run the appropriate script.
