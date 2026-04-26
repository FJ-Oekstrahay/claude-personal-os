---
name: Blackbox Multi-Log Auto-Analyze Last Segment
description: For multi-segment BBL files, auto-analyze the most recent segment and present findings first; offer alternative segments on request
type: feedback
---

## Pattern

When a `.bbl` file contains multiple segments (common with SD card FCs):
1. Auto-analyze the **last segment** (most recent flight data) in code before the agent's turn
2. Inject metrics into context with notation: `[Blackbox analysis — file.bbl [N segments; showing last (#N)]]`
3. Agent presents findings from the injected metrics **first**, then mentions which segment was analyzed
4. Agent offers to analyze a different segment if the pilot requests

**Why:** Asking "which segment do you want?" before presenting findings breaks the flow and forces pilots into UI-like interaction ("step 1: pick index, step 2: see results"). The better UX is: show the most useful data (last flight) immediately, mention what you showed, and defer to the pilot for alternatives.

## Code pattern

**In cli/blackbox.py:**

1. Add `count_logs()` function to detect multi-segment files:
   ```python
   def count_logs(bbl_path: str) -> int:
       """Return the number of flight logs in a BBL file."""
       # Uses blackbox_decode --stdout to count segments
   ```

2. In `decode_bbl()` or `analyze_to_metrics()`, auto-select the last segment:
   ```python
   num_logs = count_logs(bbl_path)
   if num_logs > 1:
       log_index = num_logs - 1  # 0-indexed, so N logs → index N-1
       cmd = [decoder, '--stdout', '--index', str(log_index), bbl_path]
   else:
       cmd = [decoder, '--stdout', bbl_path]
   ```

3. In the metrics output, include segment notation:
   ```python
   segment_note = f" [showing last segment #{log_index + 1}]" if num_logs > 1 else ""
   return f"[Blackbox analysis — {filename}{segment_note}]\n{metrics_text}"
   ```

**In AGENT_SYSTEM:**

Remove "which segment do you want" instructions. Instead:

```
When analyzing a multi-segment flight log (.bbl with multiple flights):
- I automatically analyze the most recent flight (last segment)
- The context shows which segment was analyzed: [segment #N of M]
- If the pilot wants to see a different flight, I can analyze any segment on request
You don't need to ask me or provide an index number — I show the latest flight by default.
```

## Eval case pattern

```yaml
id: bb-multiindex-disambiguation-YYYYMMDD
type: unit
tags: [no_hw]
prompt: "I haven't flown it yet. I want you to analyze the blackbox log"
context: |
  [Blackbox analysis — btfl_001.bbl [7 segments; showing last (#7)]]
  [metrics from segment 7...]
expected: |
  JARFACE presents findings first, mentions segment #7, offers alternatives.
scoring_criteria: |
  Pass if:
  - Findings presented immediately (not asking for segment choice)
  - Segment notation included ("showing last (#7)")
  - Offer to analyze other segments if desired
  Fail if:
  - Asks "which segment" before presenting findings
  - Ignores segment information
```

## Related

- [[betaflight_blackbox_pull_modes]] — SD card vs flash retrieval differences
- [[agent_third_person_language_removal]] — remove terminal command instructions
- [[playbook_blackbox_analysis_context_isolation]] — metrics output pattern
