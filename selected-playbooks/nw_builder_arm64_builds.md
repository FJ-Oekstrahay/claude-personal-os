---
name: NW.js ARM64 builds (BF Configurator)
description: Building NW.js apps for ARM64 macOS; nw-builder API compatibility; Node version constraints
type: feedback
---

Building NW.js on ARM64 (Apple Silicon) requires careful version coordination:

**Breaking change:** nw-builder 3.x → 4.x has API changes. Version 4.x uses new `platform` and `arch` parameters instead of the older `platforms` structure.

**Node version constraint:** Node 18 LTS is required. Node 25+ breaks native modules like libxmljs2, which Betaflight Configurator depends on. Do not use newer Node versions for NW.js builds.

**How to apply:**
- When building Betaflight Configurator 10.10.0+ on ARM64 Mac, pin Node to 18 LTS (`nvm install 18 && nvm use 18`)
- Ensure `package.json` uses nw-builder 4.x or later
- Update build script to use the new platform/arch parameters if migrating from 3.x

**Why:** Configurator 10.10.0 was successfully rebuilt with this combination after earlier attempts failed due to Node 25 breaking libxmljs2 compilation. This is a known, reproducible pattern.
