---
name: Betaflight FC serial prompt detection
description: Gotcha with detecting CLI prompt termination when comment lines contain delimiter
type: feedback
originSessionId: 27695732-48ac-444c-b80c-0e55fc46264d
---
## Prompt detection truncation bug in fc.py

**The problem:** When reading Betaflight CLI output, looking for the command prompt (`> `), you need to detect when a line ending with `# ` appears in the output. But comment lines from `diff all` output (like `# profile 0`) contain `# ` in the middle, which can cause a premature prompt match.

**Root cause:** A serial read can chunk in the middle of a comment. If a read chunk ends with `# ` (the end of the comment line), it falsely matches the prompt check. The next read would return the rest of the comment (e.g., `profile 0\n> `), which is treated as a prompt but actually contains data.

**Solution:** After a potential prompt match (`endswith(b'# ')`), always do one additional `read()`. If more bytes arrive, you matched a false positive (mid-comment line). Keep the data and keep reading. If the read times out (no new data), then it was the real prompt.

**Code pattern:**
```python
if data.endswith(b'# '):
    # Potential match — confirm with another read
    next_chunk = serial.read(1024)  # This will timeout if it's the real prompt
    if next_chunk:
        # False positive — was a comment line
        data += next_chunk
        # Keep reading for real prompt
    else:
        # Confirmed: real prompt
        break
```

**Why:** `diff all` output is verbose and unstructured. Comment lines, parameter values, and profiles all appear in the stream. This affects any droneteleo code that parses Betaflight serial output and needs to detect termination reliably.

**Applied fix:** fc.py `_wait_for_prompt()` method now does the confirmatory read.
