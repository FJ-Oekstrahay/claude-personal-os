# Sales Automation Project Memory

## Project
- Root: /Users/moltyjoe/.openclaw/workspace/projects/sales_automation
- Venv: .venv (Python 3.14), run via `tools/run.sh` or `.venv/bin/python3`
- Installed: anthropic 0.84.0, Pillow 12.1.1, pytesseract 0.3.13, pyyaml 6.0.3

## Architecture
Two pipelines coexist:
1. **OLD (tools/)** — Tesseract OCR → regex extraction. Do NOT modify.
2. **NEW (lib/)** — LLM-first pipeline being built incrementally.

## New pipeline structure (Phase 2 complete)
- `config.yaml` — model names, paths, accounts (l3harris, saic, textron)
- `run.py` — CLI entry point: `python run.py screenshot <path> --account <name>`
- `lib/llm.py` — `call_llm(prompt, image_path=None, temperature=0.0)` → str
- `lib/util.py` — `load_config()`, `resolve_path(key)`, `now_utc_iso()`, `artifact_filename()`, `parse_json_response()`
- `lib/artifacts.py` — `save_artifact(data, source_path)`, `load_artifact(id)`, `list_artifacts(date, account)`
- `lib/validate.py` — Phase 3 placeholder
- `schemas/screenshot_artifact.json` — v2 schema (meta/source_type/content/confidence)
- `prompts/screenshot_extract.md` — extraction prompt with {{account_hint}} and {{schema}} placeholders
- Directories: artifacts/raw/, artifacts/processed/, logs/, summaries/, drafts/, prompts/

## Artifact storage
- Processed: artifacts/processed/YYYY-MM-DD/<id>.json
- Raw copies: artifacts/raw/YYYY-MM-DD/<original_filename>
- ID format set by LLM: screenshot-YYYY-MM-DD-NNN

## New pipeline structure (Phase 7 complete)
- `lib/llm.py` — `set_command_context(cmd)` sets tag for cost tracking; `_track_cost()` writes to `costs/YYYY-MM-DD.json`
- `costs/` — daily cost files with per-call breakdown and totals
- `prompts/query.md`, `prompts/strategy.md`, `prompts/role_message.md`, `prompts/debrief.md`

## New CLI commands (Phase 7)
- `query "question" [--account] [--from DATE --to DATE]` — LLM query across artifacts, temp 0.3
- `strategy --account <acct> [--from --to]` — strategic account assessment (6 sections), saves to summaries/
- `message <artifact_id> --role <role>` — role-tailored message (cto/program manager/chief engineer/procurement/executive), temp 0.4, saves to drafts/
- `debrief --from DATE --to DATE [--account]` — 7-section meeting debrief, loads by processed AND interaction date, saves to summaries/
- `costs [--date|--week|--month|--total]` — show token usage and cost summaries
- `summarize` and `actions` now support `--from/--to` (in addition to `--date`) and `--date-field processed|interaction`

## Bug fixes (Phase 7 session)
- BUG 1: account filtering was case-sensitive — fixed with .lower() on both sides in list_artifacts; new artifacts normalized to lowercase on save
- BUG 2: write_log_entry used UTC date for log filenames — added now_local_date() using zoneinfo America/New_York; all user-facing date bucketing uses local time
- BUG 3: save_artifact no longer copies raw files; cmd_batch moves files from inbox to artifacts/raw/processed/YYYY-MM-DD/ on success, leaves failures in inbox

## Raw file structure
- `artifacts/raw/inbox/` — drop zone (user puts files here before batch)
- `artifacts/raw/processed/YYYY-MM-DD/` — moved here after successful batch
- `artifacts/raw/test/` — permanent test corpus (batch ignores by convention)

## Key decisions
- Model: claude-sonnet-4-20250514 for both text and multimodal
- API key: ANTHROPIC_API_KEY env var
- Images capped at 1568px longest edge before sending
- Retry once on 500/529, then raise
- call_llm does NOT parse, validate, or manage history
- Pricing: $3/M input, $15/M output for claude-sonnet-4-20250514 (configurable in config.yaml)
- interaction_dates is an array (not single date) — one document can have multiple interaction dates
- debrief loads by processed date UNION interaction date to avoid missing cross-day artifacts

## Search index (Phase 8)
- `lib/search.py` — SQLite FTS5 index: `init_db()`, `index_artifact()`, `rebuild_index()`, `search_fts()`, `search_sql()`, `get_stats()`
- DB at `artifacts/search.db` (gitignored)
- `run.py index` rebuilds from scratch; `run.py search "query" [--account] [--from/--to] [--limit]`
- Incremental: `save_artifact()` auto-indexes new artifacts
- Tables: `artifacts` (structured), `artifact_dates` (interaction dates), `artifact_fts` (FTS5 full-text)

## User preferences
- Build incrementally, one phase at a time — stop after each for testing
- Show diffs when editing existing files
- Ask rather than guess on ambiguous things
- Run inline tests before reporting phase done
- No governance blocks, no formal docs, no screenshots of terminal

## Workflow preferences
- [feedback_use_sonnet_for_implementation.md](feedback_use_sonnet_for_implementation.md) — Remind Geoff to switch to Sonnet for implementation work; save Opus for planning/review

## User profile
- [user_employer.md](user_employer.md) — Geoff works for Synopsys (acquired Ansys), AGI division
