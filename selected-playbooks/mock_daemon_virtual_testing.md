---
name: Mock Daemon Pattern for Hardware-Dependent Project Testing
description: Building virtual test doubles for hardware-dependent AI projects; protocol mirroring and pyautogui integration for offline testing
type: reference
---

## Problem
Testing AI-driven automation projects that depend on external hardware (flight controllers, USB gadgets, serial devices) when hardware is unavailable, expensive, or risky. Need the AI loop to function without real hardware attached.

## Solution: Mock Daemon Pattern

Build a lightweight daemon that:
1. **Accepts the same protocol** as the real hardware (serial commands, API calls, network messages, etc.)
2. **Returns valid responses** that simulate hardware behavior
3. **Drives local automation** using `pyautogui` instead of real output devices
4. **Runs on localhost** alongside the AI code for testing

## Example
Real hardware: Betaflight flight controller via serial UART
Mock daemon:
- Accepts Betaflight CLI commands on a TCP port or named pipe
- Returns simulated flight state responses (attitude, battery voltage, etc.)
- Calls `pyautogui.moveMouse()` or `pyautogui.keyDown()` to simulate what would happen on real hardware

## Benefits
- **Full AI loop testing** without any hardware attached
- Reproducible, fast test runs
- Easy to inject failure modes (simulate hardware errors)
- Decouples AI development from hardware availability
- Can run on any machine (Mac, Linux, Windows)
- Works with CI/CD pipelines

## Why
Hardware-dependent projects block on physical availability and risk hardware damage during testing. A protocol-level mock that mimics hardware responses while driving `pyautogui` locally lets you develop and test the full AI loop—sensor reading, decision-making, actuation—completely offline.

## How to Apply
- Identify the hardware protocol (serial, REST API, WebSocket, etc.)
- Build a lightweight mock server accepting the same protocol
- Document expected request/response pairs
- Use mock in test code; swap to real hardware in production
- Keeps test suite fast and reproducible

## Anti-Pattern
Don't mock at the AI framework level (mocking OpenAI calls, Gemini API, etc.)—mock at the hardware interface level instead. The goal is testing the full loop: AI perception → decision → hardware control.

## Related
- [[virtual_hardware_patterns]] — extending this for complex multi-device scenarios
- [[betaflight_dji_msp]] — example: Betaflight serial protocol documentation for mock implementation
