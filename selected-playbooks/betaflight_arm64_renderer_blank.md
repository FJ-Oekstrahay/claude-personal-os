---
name: BetaFlight Configurator ARM64 blank/white renderer issue
description: Electron app shows white/blank content area on ARM64 Mac; missing native renderer dependency, not a code issue
type: playbook
---

## Problem
BetaFlight Configurator (NW.js/Electron build) on Apple Silicon macOS displays a white or blank content area. The window opens, chrome (title bar, menus) render correctly, but the main application content is invisible or white.

This occurs with both Electron and NW.js builds.

## Why
ARM64 builds of Chromium-based runtimes (used by both Electron and NW.js) require native renderer dependencies that aren't always present in a freshly extracted binary or cross-compiled build.

The white screen typically indicates:
- V8 snapshot data corruption or mismatch
- Missing or incompatible ICU (International Components for Unicode) library
- Renderer process crash without console output
- Binary extracted without proper code signing / notarization on newer macOS

This is **not** a code issue (JavaScript, CSS, or application logic). The renderer layer itself can't initialize.

## How to apply

### For pre-built binaries
1. **Check macOS Gatekeeper status**: `codesign -v /path/to/app`
   - May need `sudo xattr -rd com.apple.quarantine /path/to/app` to remove quarantine flag
2. **Verify binary architecture**: `file /path/to/BetaFlight\ Configurator.app/Contents/MacOS/nwjs`
   - Should show `Mach-O 64-bit executable arm64`
3. **Try a fresh download** of the official ARM64 build (not cross-compiled from x86)
4. **Check for missing dylib dependencies**: `otool -L /path/to/binary`

### For rebuilds
1. **Ensure NW.js/Electron version is ARM64-native**, not x86 with Rosetta translation
2. **Rebuild locally** on ARM64 hardware if possible; cross-compilation can miss platform-specific dependencies
3. **Include ICU data** in the bundle — some builds require explicit ICU inclusion
4. **Test on a clean macOS install** (or in a VM) — development machines often have cached system libraries

### Debugging
1. Check app console via `open -a Console.app` — filter by app name
2. Run from terminal with `--verbose` flag if available (NW.js may support it)
3. Check system logs: `log stream --predicate 'process contains "betaflight"'`

### Workaround
If the binary can't be fixed, use the **web-based Configurator** via Cloudflare Pages or local proxy instead of the desktop app.

## Related
- `nw_builder_arm64_builds.md` — general ARM64 build patterns for NW.js
- `playwright_web_automation.md` — alternative: headless web automation if desktop app is unavailable
