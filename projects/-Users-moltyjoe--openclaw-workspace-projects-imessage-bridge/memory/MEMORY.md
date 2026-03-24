# iMessage Bridge — Project Memory

## Architecture (V2, current)

**Flow:** chat.db → inbound_poller → queue/inbound.jsonl → router → queue/outbound.jsonl → listener → BlueBubbles

| File | Role |
|------|------|
| `imessage_bridge/router.py` | V2 router: routing rules, group addressing, commands, identity |
| `imessage_bridge/listener.py` | Polls outbound.jsonl, requires chat_guid (V2 strict) |
| `imessage_bridge/inbound_poller.py` | Polls chat.db every 2s → inbound.jsonl (is_from_me=0 only) |
| `imessage_bridge/sender.py` | BlueBubbles HTTP POST; skips ChatResolver if recipient has ";" |
| `imessage_bridge/autopilot.py` | V1 only — replaced by router in V2 |

**Start V2:** `./run_v2.sh` (or individual tmux windows with `python3 -m imessage_bridge.cli listen-inbound/router/listen`)

## Key Design Rules (non-negotiable)

- Outbound MUST have `chat_guid`. Listener hard-fails (log + reject) if missing.
- Outbound schema: `{"chat_guid":"...", "text":"...", "trace_id":"<uuid4>", "in_reply_to_rowid":<int>}`
- Group chats: reply ONLY when addressed. 1:1: always reply (unless muted).
- `sender.py`: if recipient contains `;`, it's a pre-resolved GUID — skip ChatResolver.

## State Files

```
state/people/identities.json    # Geoff (admin, +15053063104) + Anita (+15127714676)
state/chats/<safe_guid>.json    # per-chat: last_inbound_rowid, muted_until, cooldown ts
logs/decisions.jsonl            # router decision log
router_state.db                 # SQLite cursor for router (separate from autopilot_state.db)
```

## Admin Handles (hardcoded in router.py ADMIN_HANDLES)
+15053063104, geoffhoekstra@icloud.com, geoffhoekstra@mac.com, geoffhoekstra@me.com

## Group Addressing Triggers
`moltyjoe`, `molty joe`, `molty`, `mj` — any prefix or bare, or with @/-
`joe` — NOT a trigger in any form (removed to avoid false positives).
Regex boundary: uses `\b` (word boundary) — more robust than the old `[:\s,.!?]` set.

## Test Coverage
- `pytest` runs 219 tests (0.45s). Always passes.
- New tests: `imessage_bridge/tests/test_router.py` (76 tests), updated `test_listener.py`.
- RouterLoop tests use `tmp_path`-scoped `chats_dir` and `identities_path` to avoid cross-test state bleed.

## Cooldowns
- 1:1: 1.5s, Group: 2.5s. Tracked in `ChatState.last_response_ts`.

## Commands (admin-only)
`/help`, `/new`, `/mute <min>`, `/whois <handle> <Name>`, `/send <number_or_guid> <message>`
`/send` enqueues a direct outbound message to any phone number or GUID (ChatResolver resolves phone→GUID).
Non-admin in group: silent. Non-admin in 1:1: "Commands are restricted."
