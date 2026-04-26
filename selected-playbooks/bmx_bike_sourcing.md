---
type: playbook
title: BMX bike sourcing — sizing, markets, pricing
agents: [seymour, moltyjoe]
tags: [bmx, bikes, sourcing, classifieds, marketplace, ethan, used bikes, 20-inch]
created: 2026-04-02
updated: 2026-04-02
---

## Goal
Source used BMX bikes efficiently by targeting the right size, markets, and price points.

## When to Use
Before searching for used bikes on Craigslist, Facebook Marketplace, eBay, or local classifieds.

## Sizing Reference

### BMX Bike Wheel Sizes
- **16" wheels:** Very small, typically for riders 4–6 years old (toddler-level)
- **18" wheels:** Small, riders 6–8 years old
- **20" wheels:** Standard full-size BMX, riders 8–12+ years old (this is the primary market for used bikes, also common for tricks/stunt bikes)
- **24" wheels:** Larger BMX/cruiser, teenagers and adults

**For an 11-year-old with average build:** 20" is the correct target. If the rider is particularly small or tall, 18" or 24" may be worth testing, but 20" is the starting point.

## Market Research (Documented 2026-04-02)

### Richmond, VA / Henrico County / Glen Allen area
**Viable sourcing zones (by platform):**
- Craigslist Richmond: Usually has 3–8 used 20" BMX bikes listed at any time
- Facebook Marketplace (Richmond, Henrico, Glen Allen): Often 5–12 listings, good condition spread
- eBay (local pickup, ZIP 23233): Occasional listings, smaller pool
- Local bike shops: May have trade-in stock (usually $80–150)

**Price range (20" used BMX):** $30–$125
- Under $50: Beaters, needs repair, heavy patina
- $50–$80: Good condition, minor wear
- $80–$125: Nearly new, lightly used, may have upgrades

**Condition indicators to look for:**
- Frame integrity (no bends, cracks visible in photos)
- Rust: Surface (cosmetic, ok) vs. frame/spokes (structural, avoid)
- Tires: Flat is ok (easy fix); rotted sidewalls not ok
- Bearings/drivetrain: Should spin freely (ask seller in messages)
- Grips, seat, pedals: Easy to replace if worn

## Search Strategy

### Craigslist approach
1. Go to `craigslist.org/search/bik` (Richmond area)
2. Filter by price ($25–$150) and "bikes" category
3. Keywords: "20 inch", "20\"", "bmx", "mongoose", "sunday", "fit"
4. Check newest listings first (reposted daily)
5. Look for sellers with multiple photos (usually more honest condition reporting)

### Facebook Marketplace approach
**Note:** WebFetch returns raw JSON. Use headless Playwright to scrape listings.
1. Search: "20 inch BMX" or "BMX bike Richmond"
2. Filter by price ($25–$150) and distance (< 25 miles from home)
3. Check seller rating (multiple sales = more reliable)
4. Message sellers asking for more photos and condition details (brake function, drivetrain action)
5. **Critical:** Use headless Playwright with explicit geolocation (`latitude: 37.5407, longitude: -77.4360` for Richmond VA). FB Marketplace server enforces geography — URL city ID alone doesn't work. Always verify final listing locations match your target area after scraping.

### eBay approach
1. Search: "20 inch BMX" + location filter (local pickup)
2. Sort by newest or ending soon (creates urgency for sellers with real stock)
3. Note: eBay bikes often priced 10–20% higher than Craigslist
4. Consider shipping cost if not local pickup

## Contact and Inspection Protocol

### Initial Message (via Marketplace/Craigslist)
```
"Hi, interested in the 20\" BMX. Quick questions:
- Does the drivetrain shift smoothly? Any rust on the chain?
- Do the brakes work?
- Any frame damage or cracks?
- [Your availability for local pickup]"
```

### In-Person Inspection (if proceeding)
- Spin the wheels freely (check for cracks, wobbles)
- Test brakes (should engage without grinding)
- Rock the frame (check for flex/cracks)
- Sit on it (seat height okay? Reach comfortable?)
- Test pedal/drivetrain (smooth action, no skipping)

### Walk-away signals
- Deep rust on spokes or frame
- Twisted frame (common in crashes)
- Brakes that don't engage
- Missing parts (grips, seat, pedals is fine; missing cranks is not)

## Post-Purchase Setup
- Clean and degrease (hose + WD-40)
- Air up tires (should be 40–60 PSI for most BMX)
- Adjust seat height and seatpost angle
- Optional: new grips ($15–25) and pedal pads if worn

## Seasonal Notes
- Spring (March–May): Best selection as riders upgrade, more repair-oriented sellers active
- Summer (June–Aug): Fewer used bikes (people riding them), prices climb slightly
- Fall (Sept–Nov): Second peak as kids outgrow summer purchases
- Winter (Dec–Feb): Lowest selection, best deals on slow sales

## Related
- `playbooks/web_scraping_alternatives.md` — Playwright for Facebook Marketplace scraping
