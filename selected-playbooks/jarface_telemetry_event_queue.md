---
name: JARFACE telemetry event queue and offline persistence
description: Async queue.Queue consumer pattern for session_complete; offline queue flushing; PII stripping in worker.js
type: feedback
---

Telemetry architecture (Tier 3 event system, Architect-reviewed, all 13 issues fixed):

**Event flow:**
1. Agent writes extracted data to `session_complete` endpoint (tuning_history, discoveries, session metadata)
2. Cloudflare worker (proxy/worker.js) receives payload, strips PII (substring match for identifying fields, handles arrays), queues event
3. Python telemetry consumer (cli/telemetry.py) runs as daemon thread with queue.Queue, 2s blocking session_complete, offline queue with flush
4. Offline queue persists unsent events to disk; daemon flushes on reconnect

**Key fixes (from Architect review):**
- Identity scheme conflict resolved: agent_id now sourced from `dt` config, not recomputed
- Session_complete daemon thread rewritten to avoid blocking FC serial access during upload
- Offline queue added with persistent storage (prevents data loss on network interruption)
- Extracted data now passed through `session_complete`, not just telemetry bucket
- PII strip in worker.js: substring match on guarded fields (callsign, location, etc.); correctly handles nested objects and arrays
- Schema migration 002 added for tuning_history schema changes

**Testing:** Evaluate with `dt agent` in bench + field scenarios. Offline queue behavior validated in unit tests.

**Known constraints:**
- Telemetry runs async; pilot sees "session complete" before data is uploaded (acceptable for UX, eventual consistency)
- PII stripping is field-name-driven (callsign, location, home_position, etc.); add new guarded fields to worker.js if data model expands

**Evidence:** telemetry.py fully rewritten with consumer pattern; agent.py, cli/skills.py updated to pass extracted data; worker.js fixed for nested object traversal.
