---
name: feedback_gdoc_markdown_conversion
description: Use pandoc (not python markdown module) for markdown-to-Google-Doc conversion
type: feedback
---

Always use `pandoc` to convert markdown to HTML before uploading to Google Drive as a Google Doc. The python `markdown` module is not installed — falling back to `<pre>` wrapping makes the doc look like raw plaintext.

**Why:** Pandoc is at `/opt/homebrew/bin/pandoc` and produces clean HTML. The python `markdown` module is not in the environment.

**How to apply:** In the Google Docs upload workflow, replace the python markdown conversion step with:
```bash
pandoc input.md -f markdown -t html -o /tmp/output.html
```
Then proceed with the multipart Drive API upload as normal.
