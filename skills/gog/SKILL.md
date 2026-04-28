---
name: gog
description: Google Workspace CLI (gogcli) for Gmail, Google Calendar, Drive, Docs, Sheets, and Contacts. Uses your already-authorized local gog install.
keywords:
  - gmail
  - email
  - calendar
  - drive
  - docs
  - sheets
meta
  openclaw:
    emoji: "📬"
    requires:
      bins: ["gog"]
    permissions:
      - read-mail
      - send-mail
      - read-calendar
      - write-calendar
      - read-drive
      - write-drive
      - write-sheets
---

# gog (Google Workspace)

## Global execution rules (always)

- Always use the full path to the binary: `/opt/homebrew/bin/gog`.
- Always include `--account your@email.com`.
- For automation, always include `--no-input`.
- Prefer `--json` for anything you need to parse; otherwise use `--plain` for stable TSV.
- Assume gog is already authenticated and authorized; do NOT say that capabilities are unavailable without trying the canonical commands below.
- Do not invent gog subcommands or flags that are not present in this file.

---

## Gmail (authoritative)

### What gog can do

- The installed gog CLI CAN retrieve full email bodies.
- Proven command (already tested):

  /opt/homebrew/bin/gog gmail messages search "newer_than:7d" \
    --max 1 \
    --include-body \
    --json \
    --account your@email.com \
    --no-input

  This returns JSON like:

  {
    "messages": [
      {
        "id": "...",
        "date": "...",
        "from": "...",
        "subject": "...",
        "body": "<full plain-text body with \\r\\n line breaks>"
      }
    ],
    "nextPageToken": "..."
  }

- Never say that reading or displaying the email body is impossible or unsupported.
- Never answer with any sentence that claims “I can list your messages but not their body content.”

### Text of my most recent email

When the user asks for the text/body of their most recent email:

1. Run:

   /opt/homebrew/bin/gog gmail messages search "in:inbox" \
     --max 1 \
     --include-body \
     --json \
     --account your@email.com \
     --no-input

2. From the JSON response, select messages[0].

3. Read the `body` field directly. It already contains the full plain-text email body (with \r\n line breaks).

4. Normalize line breaks by converting `\r\n` to `\n`, then split on `\n` into lines.

5. If the user asked for “the text of my most recent email”, return ALL lines.
   If they asked for “first N lines”, return the first N non-empty lines.

If `messages[0].body` is missing, explicitly report that field as missing instead of claiming the CLI cannot access email bodies.

### Other Gmail commands

- List recent emails (no bodies):

  /opt/homebrew/bin/gog gmail messages search "newer_than:7d" \
    --max {{max|default:10}} \
    --json \
    --account your@email.com \
    --no-input

- Search emails (no bodies):

  /opt/homebrew/bin/gog gmail messages search "{{query}}" \
    --max {{max|default:10}} \
    --json \
    --account your@email.com \
    --no-input

- Search emails and include bodies:

  /opt/homebrew/bin/gog gmail messages search "{{query}}" \
    --max {{max|default:5}} \
    --include-body \
    --json \
    --account your@email.com \
    --no-input

- Send an email (plain text):

  /opt/homebrew/bin/gog gmail send \
    --to "{{to}}" \
    --subject "{{subject}}" \
    --body "{{body}}" \
    --account your@email.com \
    --no-input

- Send an email (HTML):

  /opt/homebrew/bin/gog gmail send \
    --to "{{to}}" \
    --subject "{{subject}}" \
    --body-html "{{body_html}}" \
    --account your@email.com \
    --no-input

---

## Calendar

### Create a calendar event (primary calendar)

 /opt/homebrew/bin/gog calendar create primary \
   --summary "{{summary}}" \
   --from "{{from_iso}}" \
   --to "{{to_iso}}" \
   --account your@email.com \
   --no-input

### Create a calendar event with attendees

 /opt/homebrew/bin/gog calendar create primary \
   --summary "{{summary}}" \
   --from "{{from_iso}}" \
   --to "{{to_iso}}" \
   --attendees "{{attendees_csv}}" \
   --account your@email.com \
   --no-input

### List calendar events

 /opt/homebrew/bin/gog calendar events primary \
   --from "{{from_iso}}" \
   --to "{{to_iso}}" \
   --json \
   --account your@email.com \
   --no-input

---

## Drive

### Drive search

 /opt/homebrew/bin/gog drive search "{{query}}" \
   --max {{max|default:20}} \
   --json \
   --account your@email.com \
   --no-input

### Docs export (via Drive)

 /opt/homebrew/bin/gog docs export "{{doc_id}}" \
   --format {{format|default:pdf}} \
   --out "{{out_path}}" \
   --account your@email.com \
   --no-input

---

## Sheets

### Sheets create

 /opt/homebrew/bin/gog sheets create "{{title}}" \
   --json \
   --account your@email.com \
   --no-input

### Sheets update (values JSON)

 /opt/homebrew/bin/gog sheets update "{{spreadsheet_id}}" "{{range_a1}}" \
   --values-json '{{values_json}}' \
   --account your@email.com \
   --no-input

---

## Date/time normalization

- Convert user-specified times to ISO-8601 with timezone.
- Default timezone: America/New_York unless the user specifies otherwise.
- For calendar --from/--to, use full timestamps (for example: 2026-02-08T16:00:00-05:00).

---

## Safety guardrails

- Never delete calendar events or emails unless the user explicitly asks.
- For sending email, if the recipient is ambiguous, ask for clarification; otherwise send immediately.
- Do not create or use any gog subcommands that are not shown in this file.
