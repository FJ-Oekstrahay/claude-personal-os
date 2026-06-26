Convert markdown (or any text content in context) to a shareable document format and save it to disk.

## Decision rules — pick format, then proceed immediately. Never ask which format.

**Signal → format mapping (first match wins):**
- Request mentions "word", "docx", "edit", "they need to edit" → **DOCX**
- Request mentions "pdf", "professional", "print" → **PDF**
- No format signal → **HTML** (default — most token-efficient)

## Always announce before running

One line, before any tool call:
> Converting to [FORMAT] → [output path] ([reason])

Example: "Converting to HTML → /tmp/report.html (default — no format specified)"
Example: "Converting to PDF → /tmp/report.pdf (PDF requested)"
Example: "Converting to DOCX → /tmp/report.docx (editing mentioned)"

## Commands

Determine the input: if a file path was given, use it. If markdown is in context, write it to a temp file first (`/tmp/cc_convert_input.md`), then convert.

**HTML (default):**
```
pandoc [input].md -o [output].html --standalone
```

**PDF (Chrome headless — no LaTeX required):**
```
pandoc [input].md -o /tmp/cc_convert_tmp.html --standalone
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --headless --print-to-pdf=[output].pdf --no-sandbox /tmp/cc_convert_tmp.html
```

**DOCX:**
```
pandoc [input].md -o [output].docx
```

## Output path

If the user specified a path, use it. Otherwise default to `/tmp/[input-basename].[ext]`.

## After converting

Report: "Done — [output path]" and offer to open or attach it. Do not narrate the commands you ran.
