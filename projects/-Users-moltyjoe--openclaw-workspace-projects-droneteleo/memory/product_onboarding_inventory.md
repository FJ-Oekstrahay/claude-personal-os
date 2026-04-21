---
name: Product — inventory onboarding flow
description: Droneteleo should offer inventory setup on first run but never block on it
type: project
originSessionId: 0ffe1c8f-3e75-44df-b82b-e4880308157d
---
On first run (no profile exists), droneteleo should offer to walk the user through building their hardware inventory. It should be frictionless to skip — `detect`, `review`, `agent` and everything else works immediately with or without a profile.

**Why:** The AI gives better advice when it knows the frame, motors, props, FC, and video system. But blocking new users on a setup form kills adoption.

**Pattern:**
- First run: brief prompt — "Want to add your gear? Takes 2 minutes and helps the AI give better advice. (Skip with Enter)"
- After skip: never nag again unless user explicitly runs `droneteleo profile`
- `droneteleo profile show/add-drone/add-radio/add-goggles` always available
- Profile context is silently appended to system prompt when present

**Standard build data:** For popular quads (Seeker3, Nazgul, etc.), droneteleo could offer to auto-populate specs from a known-builds database — user just confirms rather than typing everything.
