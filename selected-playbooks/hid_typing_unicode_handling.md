---
name: HID Typing and Unicode Text Input
description: Handling text input via USB HID keyboard simulation; ASCII vs Unicode limitations and workarounds
type: reference
---

## Problem
Automating text input via USB HID keyboard (or `pyautogui` keyboard simulation) when the target system expects both ASCII text and Unicode characters (emojis, accents, non-Latin scripts).

## The Core Issue

**`pyautogui.typewrite()`**
- ASCII-only; sends one keystroke per character
- Cannot type emojis, accented characters, CJK, or any Unicode outside ASCII range
- Works: `typewrite("hello")`
- Fails: `typewrite("café")`, `typewrite("😀")`

**HID Keyboard Protocol**
- Native USB HID keyboard only sends individual key events (shift+a = A, ctrl+c = copy)
- No direct Unicode/Unicode codepoint support in the protocol
- Operating system converts key sequences → typed text

## Solution: Clipboard Paste

Use the system clipboard as an intermediary:
1. Place desired text in clipboard (handles any Unicode)
2. Send keyboard shortcut to paste (Cmd+V on macOS, Ctrl+V elsewhere)
3. OS pastes the Unicode text directly

**Implementation pattern:**
```python
import pyperclip

# Instead of:
# pyautogui.typewrite("café")  # FAILS — ASCII only

# Use:
pyperclip.copy("café")
pyautogui.hotkey('cmd', 'v')  # macOS
# or
pyautogui.hotkey('ctrl', 'v')  # Windows/Linux
```

## Why
Clipboard operations are handled by the OS and bypass HID keyboard limitations. The clipboard can hold any text encoding; paste operations are atomic and reliable.

## How to Apply
- **ASCII-only input:** `pyautogui.typewrite()` is fine
- **Any Unicode text:** Use `pyperclip.copy()` + `pyautogui.hotkey('cmd', 'v')` (macOS) or `hotkey('ctrl', 'v')` (Windows/Linux)
- **Fallback for no clipboard:** If target doesn't support clipboard paste (air-gapped systems), you must use a different input method or accept ASCII-only limitation
- **Turk project pattern:** Mock daemon uses clipboard paste for all text input

## Related
- [[hid_keyboard_vs_absolute_mouse]] — absolute vs relative HID positioning
- [[mock_daemon_virtual_testing]] — pyautogui integration in mock harnesses
