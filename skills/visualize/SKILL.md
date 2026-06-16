---
name: visualize
description: Turn a data or visualization request into a chart delivered in-thread. Load when the user asks for a chart, plot, graph, histogram, heatmap, dashboard, or any visualization. Also triggers on "show me the data", "can you visualize", or "plot X vs Y". Default surface is Claude Code CLI — render to PNG and attach via Discord reply.
---

## Decision tree

1. **Static chart** (bar, line, scatter, hist, heatmap, distribution, a snapshot to glance at) → matplotlib. Render to PNG, attach via the Discord reply tool (`files: ["/abs/path.png"]`). This is the default and covers ~90% of requests.

2. **Interactive / exploratory** (hover tooltips, zoom, filter, sliders, large point clouds, anything you'd want to poke at) → build a self-contained HTML file (vanilla + a CDN lib like Chart.js / Plotly / D3, no build step).
   - To deliver in-thread: open it with Playwright, screenshot, attach the PNG.
   - To let the user actually interact: save the HTML to a tmp dir and tell him the path to open in a browser.
   - For genuinely interactive *exploration* (live filtering, what-if), recommend the Claude desktop app's Artifacts instead — no local equivalent worth building.

3. **Tabular / quick numbers** → don't make a chart. Markdown table in the reply.

## Procedure

1. Identify the data source: CSV, JSON, query output, log file, or inline numbers. If unclear, ask one tight question — don't guess the schema.
2. Load it (pandas if it's a file). Sanity-check shape, dtypes, nulls before plotting.
3. Pick the chart that answers the *question*, not just displays the data.
4. Render:
   - matplotlib: `fig.savefig(path, dpi=150, bbox_inches="tight")`. Dark-friendly palette, labeled axes, title, legend only if needed.
   - Save under `/tmp/` or a scratch dir; use an absolute path for the Discord attachment.
5. Reply in the thread with the PNG attached + one line on what it shows.
6. Never paste raw data dumps or secrets into the chart or the reply.

## Environment notes
- matplotlib + pandas: assume available; `pip install --user` if missing and say so.
- Playwright is already set up (MCP browser tools) for HTML→PNG screenshots.
- This is a **public repo** — write generated charts/HTML to `/tmp/` or a scratch dir, not into the repo, unless the user asks to keep them. Never commit data with PII.

## Model routing
- **Sonnet** by default — chart selection + matplotlib is well within it.
- **Opus** only when the request needs real analysis (deciding what the data means, multi-step stats) before the chart.
- **Haiku** for mechanical re-plots ("same chart but change X to Y").
