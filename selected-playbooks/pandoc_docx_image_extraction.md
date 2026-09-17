---
name: pandoc docx→HTML with image extraction
description: Extract images and convert Word docs to HTML using pandoc
type: reference
---

# Pandoc Word Doc to HTML with Image Extraction

**Use this when:**
- Converting `.docx` files to HTML for use in web workflows or embedded in Google Docs
- Extracting embedded images from Word documents for reuse
- Working with Word documents that contain both text and images

## The Right Way

```bash
pandoc file.docx -o out.html --extract-media=./media --standalone
```

**Flags:**
- `--extract-media=./media` — saves all embedded images to a subdirectory named `media/` (creates if needed)
- `--standalone` — produces clean, self-contained HTML (includes `<html>`, `<head>`, etc.)

**Output:**
- `out.html` — formatted HTML with image `<img>` tags pointing to `media/image1.png`, etc.
- `media/` — directory containing all extracted PNG/JPEG/etc. images

## What NOT to do

- **Don't use Python markdown module** — not installed on this system; throws ModuleNotFoundError
- **Don't save as RTF then convert** — RTF loses embedded images on save-as (they exist in memory during copy-paste but don't serialize)
- **Don't use Word → HTML export in Office** — less consistent than pandoc
- **Don't try to get clean HTML from .md that came from .docx** — the round-trip loses image references; work directly from the .docx source

## Why this matters

When a Word document has been edited multiple times, those edits live in the .docx file, not in Markdown versions. Always read the source `.docx` to see the current state.

**Example**: "Droneteleo Troubleshooting Article.docx" in Drive had multiple edits beyond what appeared in the markdown version. The .docx is authoritative once it's been edited.

## One-liner for Claude reading

To make a Word doc readable by Claude (preserving images):
```bash
pandoc file.docx -o /tmp/out.html --extract-media=/tmp/media --standalone
# Then ask user to upload /tmp/out.html
```

Images will display inline in the HTML and Claude will see them.
