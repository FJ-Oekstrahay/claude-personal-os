---
name: USPTO Trademark Filing
description: How to file a federal trademark application via USPTO Trademark Center using Playwright
type: feedback
---

Successfully filed DRONETELEO trademark (serial 99748276) on 2026-04-07. Full workflow documented below.

**Why:** Geoff wants to reuse this for OverVYou LLC and other marks. Save time by not re-researching the process.

**How to apply:** Any time Geoff asks to trademark a name or brand.

## System
- USPTO Trademark Center: https://trademarkcenter.uspto.gov/ (TEAS retired Jan 18, 2025)
- Payment site: https://fees.uspto.gov/ (redirected automatically)
- Serial number lookup: https://tsdr.uspto.gov/

## Pre-flight checklist (5 questions)
1. Existing USPTO account? (If no: create at my.uspto.gov + one-time ID.me identity verification ~15 min)
2. Owner: individual or LLC/Corp?
3. Use in commerce (1a) or Intent to Use (1b)?
4. Goods/services description (search ID Manual first — avoids $200 custom surcharge)
5. Payment method ready?

## Auth
- USPTO login requires MFA — Playwright cannot receive MFA codes
- Strategy: navigate to sign-in, pre-fill email, pause for Geoff to complete password+MFA, then Playwright takes over
- JWT stale role claim causes redirect loop — fix: sign out and log back in after ID.me verification

## ID Manual search tips
- Multi-word searches often return 0 results — search single keywords ("firmware", "software") then scan
- Class 9 (Goods) is correct for downloadable software
- Fill-in template used: "Downloadable computer software and firmware for [specify function]"
  - Filled with: "use in configuring, diagnosing, and managing unmanned aerial vehicle (UAV) flight controllers"
- Using an ID Manual fill-in entry avoids the $200 custom description surcharge

## CSS intercept pattern
- USPTO uses custom Angular CSS inputs — radio buttons and checkboxes require clicking the label text, not the `<input>` ref
- Click the sibling `<generic>` label element, not the radio/checkbox ref itself

## Fees
| Scenario | Cost |
|---|---|
| 1 class, ID Manual entry | $350 |
| 1 class, custom description | $550 (+$200 surcharge) |
| ITU Statement of Use (later) | +$100/class |
| ITU Extension Request | ~$125/class per 6-month extension |

## Intent to Use (1b) post-filing deadlines
- After Notice of Allowance: 6 months to file Statement of Use (with specimen)
- Can extend up to 5 times (6 months each, ~$125/class each)
- Total window: ~3 years from Notice of Allowance

## Receipt location
- USPTO receipt PDF downloads to Playwright working directory (`.playwright-mcp/`), NOT Mac ~/Downloads
- Copy to filing folder: `cp .playwright-mcp/receipt-*.pdf projects/publishing/[mark]-trademark/`

## Filing record template
Save to `projects/publishing/[mark]-trademark/filing-notes.md` with:
- Serial number
- Owner, address, email
- Class + description
- Filing basis
- Amount paid + date
- Next deadlines
