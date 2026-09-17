# workflows/

Workflow scripts for Claude Code's `Workflow` tool: plain JavaScript that orchestrates `agent()`
calls deterministically (sequencing, parallel fan-out, and pipelines) rather than leaving that
control flow to a model's own judgment in a single turn. The script itself runs for free; only the
`agent()` calls inside it consume tokens.

| File | What it does |
|---|---|
| `deep-research.js` | Fan-out research harness: scopes a question into search angles, runs parallel web searches, fetches and dedupes sources, adversarially verifies extracted claims (three-vote majority per claim), and synthesizes a cited report. Hard-caps `MAX_FETCH` and `MAX_VERIFY_CLAIMS` at 5 each: 1 scope + ~6 search + 5 fetch + (5 claims × 3 votes) verify + 1 synth, about 28 agents total, well under the built-in workflow's much larger uncapped fan-out. |
| `feature-build.js` | Drains a `FEATURE_LIST.json` state-bus queue, routing each item to a model tier via a `ROUTE` table, resumable from disk if a worker dies mid-run. |

## Notes on `feature-build.js`

The script's header comments document two constraints it's built around, both verified by testing
rather than assumed:

- **Workflow scripts have no filesystem access.** The script body can't read `FEATURE_LIST.json`
  directly, so a reader `agent()` call reads it via Bash and returns the contents through a
  `schema:`, and the fan-out is built from that return value. The same applies to timestamps:
  `Date.now()`/`new Date()`/`Math.random()` throw inside a Workflow script, so every timestamp in
  the state bus is stamped by an external script, never by the workflow itself.
- **A Workflow agent can't switch providers via a `model:` parameter.** Agents spawned from a
  script authenticate through the session's own Claude auth, so cross-provider work (GLM, Kimi)
  goes through a thin Claude agent that shells out to an external wrapper script which rebuilds the
  environment for the target provider, rather than being requested with `model: 'glm'` directly.

Both scripts are parameterized via `args` rather than rewritten per run; see each file's own
header comment for its expected `args` shape.
