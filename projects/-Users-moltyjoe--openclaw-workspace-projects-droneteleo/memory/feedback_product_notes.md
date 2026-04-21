---
name: Droneteleo product roadmap notes from debugging sessions
description: Features and content ideas that came up during real debugging/tuning sessions
type: project
originSessionId: 27695732-48ac-444c-b80c-0e55fc46264d
---
## Video content for marketing

- **Motor direction check videos** — Geoff wants to make Droneteleo-branded tutorial videos for motor direction verification (dollar bill method, prop A/B identification). These should be recorded during real debugging sessions.
  - Why: good SEO content + demonstrates the product in real use
  - How to apply: flag video-worthy moments during debugging sessions; add to content calendar

## Product feature gaps found during real sessions

- **Motor spin testing** — droneteleo CLI has no motor spin test command. Currently must use BF Configurator GUI Motors tab. This should be a first-class droneteleo feature.
  - Would need MSP commands (not CLI mode) to spin individual motors, OR use BF Motors tab via bf_bridge.py Playwright automation
  - Suggested: `droneteleo motors test` — interactive TUI with quad diagram, highlights active motor, keyboard to step through M1-M4 one at a time at low speed only
  - Safety: always display the BF Motors tab warning before spinning anything; require explicit confirmation
  - Low speed only: never spin motors fast during a test — just enough to visually confirm direction

- **GUI vs CLI question** — droneteleo is a CLI product, but interactive diagnostic flows (motor test, sensor check) would benefit from a Rich TUI rather than raw command invocation. Motor test is the first natural candidate for a Rich interactive subcommand.
  
- **Troubleshooting workflow** — When FC is connected, the product should be able to walk through a structured debug checklist (orientation check, motor direction check, prop direction check) rather than relying on the user knowing what to do.

- **Build memory** — The system should know which quad is connected and pull up build notes, last config changes, and known issues automatically. Currently requires reading from Geoff's memory files manually.
  - This is a key differentiator: "the AI that already knows your quad"
