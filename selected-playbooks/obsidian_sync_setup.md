---
name: Obsidian Sync Setup
description: Configuration and gotchas for Obsidian Sync on Mac Mini + iOS with persistent sync behavior
type: reference
---

# Obsidian Sync Setup — Mac Mini + iOS

## Core Setup

1. **Vault location on Mac Mini**: Create vault directly at `~/.openclaw/workspace/` (not as a subfolder). This allows Obsidian to open the git-tracked workspace as a native vault.

2. **Install Obsidian Sync**: Purchase and configure Obsidian Sync subscription for remote vault synchronization.

3. **iOS setup**: Install Obsidian on iOS device and connect it to the same Obsidian Sync account. The vault will sync automatically when the app is open.

## Critical Gotcha: Login Items

**Obsidian Sync is NOT a system daemon.** It only syncs while the Obsidian application is actively running.

**To keep sync current on Mac Mini:**
- Add Obsidian to Mac Mini login items (`System Settings → General → Login Items`)
- This ensures Obsidian launches at startup and stays synced without manual intervention
- Without this, sync will only occur when someone manually opens Obsidian

## Plugin Setup

**Dataview plugin:**
- Install via Community Plugins in Obsidian
- Enable per-vault (not globally) — enable it after plugin is installed by toggling in vault settings
- Required for dashboard queries (see: `[[obsidian_dashboard_queries]]`)

## .gitignore

Create `workspace/.gitignore` to exclude Obsidian's internal directory:

```
.obsidian/
```

This prevents Obsidian cache, settings, and plugin metadata from being committed.

## Dashboard and Wiki Links

After setup, migrate MEMORY.md and daily logs to use wiki-link syntax `[[filename]]` for cross-referencing. See: `[[obsidian_dashboard_queries]]` for dashboard structure.

## See Also

- `[[obsidian_dashboard_queries]]` — Dataview queries for vault dashboard
- `[[wiki_link_refactoring]]` — converting old markdown links to wiki-link syntax
