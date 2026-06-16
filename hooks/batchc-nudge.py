#!/usr/bin/env python3
"""
UserPromptSubmit hook — batchc candidacy nudge.

Scores the submitted prompt for batchc-candidacy using cheap signals only.
Never blocks (always exit 0). No LLM calls. Target: <50ms.

Signals:
  - Prompt length (>= 200 chars adds weight)
  - Distinct imperative verbs (create, add, update, remove, fix, move, rename,
    refactor, migrate, audit, write, delete, change, replace, extract, split)
  - Keywords: refactor, migrate, audit, across, "and then", also, then
  - Bullet / numbered list item count
  - List hierarchy depth (nested indentation levels)

Above a conservative threshold, prints ONE line to stdout (injected as context).
Below threshold, prints nothing.

One-liners are explicitly suppressed (short prompt + no list = no nudge).
"""

import json
import re
import sys

# --- Tuning constants ---
LENGTH_THRESHOLD = 180        # chars; below this, very unlikely to be multi-step
SCORE_THRESHOLD = 4           # total score needed to fire the nudge

IMPERATIVE_VERBS = {
    "create", "add", "update", "remove", "fix", "move", "rename",
    "refactor", "migrate", "audit", "write", "delete", "change",
    "replace", "extract", "split", "implement", "build", "convert",
    "port", "merge", "inject", "wire", "deploy",
}

KEYWORDS = re.compile(
    r'\b(refactor|migrate|audit|across)\b|and then\b|\balso\b|\bthen\b',
    re.IGNORECASE
)

# Matches bullet list items: -, *, or numbered (1. / 1))
BULLET_RE = re.compile(r'^\s*[-*•]\s+|\s*\d+[.)]\s+', re.MULTILINE)

# Detect indented nested list items (2+ spaces or tab before bullet/number)
NESTED_RE = re.compile(r'^(\s{2,}|\t+)[-*•\d]', re.MULTILINE)


def count_list_items(text: str) -> int:
    return len(BULLET_RE.findall(text))


def max_nesting_depth(text: str) -> int:
    """Estimate nesting depth by looking at indentation levels of list items."""
    depths = set()
    for line in text.splitlines():
        m = re.match(r'^(\s+)[-*•\d]', line)
        if m:
            indent = len(m.group(1).expandtabs(4))
            depths.add(indent // 2)  # every 2-space indent = 1 level
    return max(depths) + 1 if depths else 0


def score_prompt(text: str) -> tuple[int, int]:
    """Return (score, step_count_estimate)."""
    score = 0

    # 1. Length signal
    if len(text) >= LENGTH_THRESHOLD:
        score += 1

    # 2. Imperative verb count (distinct)
    words = re.findall(r'\b[a-z]+\b', text.lower())
    verbs_hit = IMPERATIVE_VERBS.intersection(words)
    verb_count = len(verbs_hit)
    if verb_count >= 2:
        score += 1
    if verb_count >= 4:
        score += 1  # extra weight for many distinct actions

    # 3. Keyword hits
    kw_hits = len(KEYWORDS.findall(text))
    if kw_hits >= 1:
        score += 1
    if kw_hits >= 3:
        score += 1

    # 4. Bullet / numbered list items
    item_count = count_list_items(text)
    if item_count >= 3:
        score += 1
    if item_count >= 6:
        score += 1

    # 5. Nesting depth
    depth = max_nesting_depth(text)
    if depth >= 2:
        score += 1

    # Estimate step count: list items if present, else verb count
    step_estimate = item_count if item_count >= 2 else max(verb_count, 1)

    return score, step_estimate


def main():
    try:
        data = json.loads(sys.stdin.read())
    except Exception:
        sys.exit(0)

    prompt = data.get("prompt", "")

    # Hard suppress on one-liners (no newlines AND short)
    if "\n" not in prompt and len(prompt) < LENGTH_THRESHOLD:
        sys.exit(0)

    score, step_estimate = score_prompt(prompt)

    if score >= SCORE_THRESHOLD:
        print(
            f"This prompt looks like a batchc candidate ({step_estimate} steps). "
            "Consider prefixing 'batchc'."
        )

    sys.exit(0)


if __name__ == "__main__":
    main()
