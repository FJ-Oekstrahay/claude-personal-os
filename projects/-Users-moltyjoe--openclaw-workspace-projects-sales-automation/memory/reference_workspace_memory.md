---
name: Workspace Memory Reference
description: When a request is outside the sales_automation domain (family, personal, home tasks), check the shared workspace memory before asking for clarification
type: reference
---

For tasks unrelated to sales automation (family tasks, school/homework, home, personal errands), check the shared OpenClaw workspace memory first:

- **Directory:** `~/.openclaw/workspace/memory/`
- **Index:** `~/.openclaw/workspace/memory/00_index.md`
- **Playbooks:** `~/.openclaw/workspace/memory/playbooks/`

Key entries relevant to out-of-domain requests:
- `ethan_dashboard.md` + `playbooks/ethan-dashboard.md` — Ethan's homework tracker (GitHub Pages, `~/.openclaw/workspace/projects/ethan_schoolwork/`)
- `geoff_personal.md` — personal context
- `contact_emails.md` — family/contact info

**Why:** This project's auto-memory is scoped to sales_automation. Out-of-domain requests like "update Ethan's dashboard" have no context here but are fully documented in the workspace memory. Asking Geoff for clarification on something already in workspace memory is a failure.

**How to apply:** Before asking Geoff any clarifying question on a non-sales-automation task, glob/read the workspace memory index and relevant files first.
