# Sales Automation v2

**Root:** `/Users/moltyjoe/.openclaw/workspace/projects/sales_automation`
**Venv:** `.venv` (Python 3.14) — activate: `.venv/bin/python`
**Model:** `claude-sonnet-4-20250514` (multimodal + text), configured in `config.yaml`

## Phase Status
- Phase 1: Core scaffolding + lib/llm.py ✅
- Phase 2: Screenshot extraction pipeline + run.py ✅
- HEIC support (pillow-heif 1.3.0) ✅
- Prompt broadened for POs, contracts, emails ✅
- Phase 3: Validation loop (lib/validate.py + retry in run.py) ✅

## Key Files
| File | Purpose |
|------|---------|
| `run.py` | CLI entrypoint — `screenshot` subcommand |
| `lib/llm.py` | `call_llm()` — Claude API, HEIC transcode, 1 transient retry |
| `lib/validate.py` | `validate_artifact()` — jsonschema Draft7, returns `(bool, list[str])` |
| `lib/util.py` | Config loading, `parse_json_response()`, path resolution |
| `lib/artifacts.py` | `save_artifact()`, `load_artifact()`, `list_artifacts()` |
| `prompts/screenshot_extract.md` | Extraction prompt (broadened: chats, POs, contracts, emails…) |
| `schemas/screenshot_artifact.json` | JSON Schema draft-07 for artifact validation |
| `config.yaml` | Paths, model names, known accounts (l3harris, saic, textron) |

## Artifact Schema (top-level required fields)
- `meta`: id, timestamp, source_file, account
- `source_type`: enum [screenshot, transcript, text, document]
- `content`: raw_text, source_app, participants[], programs[], signals[], key_facts[]
- `confidence`: overall (high/medium/low), flags[]

## Validation + Retry Logic (Phase 3)
- `lib/validate.py` uses jsonschema 4.26.0, Draft7Validator
- `run.py` loop: attempt 0 = vision call; on parse/schema failure, attempt 1 = text-only repair prompt (no image re-submit); still failing → warn and save anyway (don't block pipeline)
- Repair prompt sends bad JSON + error list, asks model to fix only invalid fields

## Inbox / Artifacts
- Input images: `inbox/images/` (HEIC + PNG accepted)
- Raw copies saved: `artifacts/raw/YYYY-MM-DD/`
- Processed JSON: `artifacts/processed/YYYY-MM-DD/<id>.json`
- Extraction quality on real POs/emails is high (tested on IMG_0007.HEIC — SAIC PO)

## Installed Packages (notable)
- anthropic, pillow (12.1.1), pillow-heif (1.3.0), jsonschema (4.26.0), pyyaml, pytesseract
