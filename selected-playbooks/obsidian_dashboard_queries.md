---
name: Obsidian Dashboard with Dataview Queries
description: Dataview query patterns for vault dashboard; recently modified notes, project backlog, memory index
type: reference
---

# Obsidian Dashboard — Dataview Query Patterns

## Dashboard.md Structure

Create `DASHBOARD.md` at vault root (`~/.openclaw/workspace/DASHBOARD.md`) with Dataview queries to surface vault navigation.

## Query Patterns

### Recently Modified Notes

```dataview
LIST
FROM ""
WHERE file.mtime >= date(today) - dur(7 days)
SORT file.mtime DESC
LIMIT 10
```

### Project Board Status

```dataview
LIST status
FROM "projects"
WHERE status
SORT date DESC
```

### Memory Index

Direct link:
```
[[memory/00_index.md]]
```

Or embed the entire index:
```dataview
TABLE WITHOUT ID file.link as Note, file.mtime as "Last Modified"
FROM "memory"
SORT file.mtime DESC
```

### Daily Logs (Reverse Chronological)

```dataview
LIST file.ctime
FROM "memory"
WHERE file.name ~ /^\d{4}-\d{2}-\d{2}/
SORT file.ctime DESC
LIMIT 20
```

## Enable Dataview Per-Vault

After installing the Dataview plugin:
1. Open vault settings (bottom-left cog)
2. Go to **Community Plugins** → **Dataview**
3. Toggle **Enable**

Do NOT enable Dataview globally — enable only in the `.openclaw/workspace` vault.

## Wiki Link Syntax

All dashboard and index links should use wiki-link syntax:
```
[[memory/00_index.md]]  ← good
[[obsidian_sync_setup]] ← good (omit .md for readability)
[text](memory/00_index.md) ← avoid
```

This allows Obsidian to auto-update links when files are moved.

## See Also

- `[[obsidian_sync_setup]]` — setup and login items configuration
- `[[session-handoff]]` skill — updates MEMORY.md with wiki-links automatically
