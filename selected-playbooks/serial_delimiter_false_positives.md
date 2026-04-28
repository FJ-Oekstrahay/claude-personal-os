---
name: Serial prompt detection and delimiter false positives
description: Handling delimiters that also appear in data streams; confirmatory reads to detect mid-stream matches
type: feedback
---

# Serial Delimiter False Positives

## The problem

When polling a serial port for a specific delimiter, false positives occur when the delimiter also appears naturally in the data stream. Classic example: Betaflight CLI uses `# ` (hash + space) as a prompt terminator, but `# ` also appears at the start of CLI comment lines (e.g., `# profile 0`, `# set debug_mode = 1`).

If the serial reader sees `# ` and immediately returns, assuming it's the prompt, it truncates responses mid-stream when the delimiter appears in output.

**Why this happened:** Built a Betaflight MSP sniffer that polled for `\r\n# ` as the CLI prompt delimiter. Large CLI outputs like `diff` contain comment lines starting with `# `, causing early termination and data loss.

## Solution: confirmatory read

After detecting a potential delimiter, perform an extra non-blocking read with a short timeout. If more bytes arrive, the delimiter was mid-stream, not a terminator.

**How to apply:**

```python
import time

def read_until_prompt(port, timeout=2.0, delimiter=b'\r\n# '):
    """
    Read from serial port until we see the prompt delimiter.
    Guard against false positives by checking if more data arrives.
    """
    start = time.time()
    buffer = b''
    
    while time.time() - start < timeout:
        byte = port.read(1)
        if not byte:
            continue
        
        buffer += byte
        
        # Check if we've seen the delimiter
        if delimiter in buffer:
            # Potential match found
            # Do a confirmatory read: wait 100ms and check if more data arrives
            time.sleep(0.1)
            extra = port.read(port.in_waiting or 1)
            
            if extra:
                # More data arrived = this was a false positive
                # Add it to buffer and keep reading
                buffer += extra
                continue
            else:
                # No more data = this is the real prompt
                return buffer
    
    raise TimeoutError(f"No prompt detected within {timeout}s")
```

## Why this works

- Most data bytes arrive in rapid bursts (microseconds apart)
- A 100ms sleep is much longer than the inter-byte latency of normal serial data
- If the delimiter is real (actual prompt), no more bytes will arrive in 100ms
- If the delimiter is false (mid-stream), the next chunk of data will arrive and be caught

## Timeout tuning

The confirmatory read uses 100ms by default, which is safe for:
- Serial baud rates >= 115200 (inter-byte times in microseconds)
- Typical serial port buffering (OS coalesces bytes)

For slower baud rates (9600), increase to 200-500ms.

## Alternative: state machine parsing

If the delimiter has context (e.g., Betaflight `# ` always follows a newline and precedes the cursor position), validate the context:

```python
def is_real_prompt(buffer, delimiter=b'\r\n# '):
    """Check if delimiter is likely a real prompt based on context."""
    idx = buffer.rfind(delimiter)
    if idx == -1:
        return False
    
    # After the prompt, expect nothing or just a cursor/ack
    after_prompt = buffer[idx + len(delimiter):]
    
    # Real prompts have at most a few bytes after (e.g., cursor position)
    if len(after_prompt) > 10:
        return False  # Looks like mid-stream, not prompt
    
    return True
```

## Related playbooks
- `serial_port_contention.md` — multi-process serial access
- `betaflight_dji_msp.md` — Betaflight CLI reference and firmware-specific quirks
