You are executing the `/xlsx` command. Follow these instructions exactly.

## Purpose

Produce nicely formatted XLSX files from CSV analysis outputs, guided by a project-local report spec.

## Step 1 — Find the report spec

Search for `report-spec.md` in this order:
1. `./skills/*/report-spec.md` (any skills subdirectory)
2. `./report-spec.md`
3. `./reports/report-spec.md`

If not found in any of these locations, tell the user: "No report-spec.md found. Create one at ./report-spec.md or ./reports/report-spec.md and re-run /xlsx." Then stop.

## Step 2 — Read and parse the spec

Read the spec file. Look for two sections:

**CSV structure section**: defines what columns/rows each report has, filename patterns, and what data lives in which file.

**XLSX formatting section**: defines visual formatting — header colors, frozen rows, column widths, number formats, sheet names, output filename pattern. This section is optional.

If the XLSX formatting section is missing, proceed with built-in defaults (documented below) and tell the user which defaults were applied.

## Step 3 — Check for an existing generator script

Check whether `scripts/generate_xlsx.py` exists in the project root.

- **If it exists**: run it with `python3 scripts/generate_xlsx.py` from the project root. Skip to Step 5.
- **If it does not exist**: write it (Step 4), then run it.

## Step 4 — Write the generator script

Write `scripts/generate_xlsx.py`. The script must:

1. **Find input CSVs**: for each report defined in the spec, glob for CSV files matching that report's filename pattern (e.g. `reports/summary-*.csv`). Sort matches by the date string embedded in the filename (YYYY-MM-DD pattern) and take the most recent. If no CSV matches, skip that report and warn.

2. **Write XLSX output**: use `xlsxwriter`. One sheet per report. Apply formatting from the spec's XLSX section, or defaults if no section exists.

3. **Formatting defaults** (when no XLSX section in spec):
   - Font: Calibri 11pt
   - Header row: bold, background `#1F3864` (dark navy), white font
   - All other rows: no special background
   - Top row frozen (freeze_panes(1, 0))
   - Column widths: auto-approximate from max content length in each column (cap at 60)
   - Number format for columns that appear to contain dollar amounts (column name contains "amount", "total", "revenue", "cost", "balance", "value", "income", "expense", or similar): `#,##0`
   - Number format for columns that appear to contain percentages (column name contains "pct", "percent", "rate", "%"): `0.0%`
   - Text wrapping: off

4. **Output filename**: use the output filename pattern from the spec if provided. Default: same directory as the input CSV, with `-formatted.xlsx` suffix replacing the `.csv` extension. If multiple reports go into one XLSX, use the pattern from the spec's Global section or default to `reports/report-<YYYY-MM-DD>.xlsx` using today's date.

5. The script must be self-contained and runnable with `python3 scripts/generate_xlsx.py` from the project root with no arguments.

6. If `xlsxwriter` is not installed, the script should print a clear error: "xlsxwriter not installed. Run: pip install xlsxwriter" and exit 1.

**Optional argument support**: if `$ARGUMENTS` is provided (a specific CSV path), write the script so it also accepts a single CSV path as a command-line argument, processing only that file. When a path is given, apply the formatting spec for the report whose pattern matches that file, or fall back to defaults if no match.

## Step 5 — Report results

After running the script, report:
- The output XLSX file path(s)
- Which reports were included
- Any reports skipped (and why)
- Whether defaults were used (and which ones)

---

## XLSX section format reference

The XLSX formatting section in `report-spec.md` should follow this structure:

```
## XLSX Formatting

### Global
- Font: Calibri 11pt
- Header background: #1F3864 (dark navy)
- Header font: white, bold
- Frozen rows: 1
- Number format (dollar): #,##0
- Number format (percent): 0.0%

### Report 1: <name>
- Sheet name: <name>
- Output filename pattern: reports/<stem>-<YYYY-MM-DD>.xlsx
- Column widths: auto (or list specific widths like "A: 20, B: 35")

### Report 2: <name>
- Sheet name: <name>
- Output filename pattern: reports/<stem>-<YYYY-MM-DD>.xlsx
- Column widths: auto
```

Column widths can be `auto` (approximate from content) or explicit per-column overrides.
