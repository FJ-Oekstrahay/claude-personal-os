---
name: Betaflight MSP Error Frame Parser Bug Pattern
description: Error frame consumption pattern; why truncated error frames cause cascading parse failures
type: playbook
---

# Betaflight MSP Error Frame Parser Bug Pattern

## The bug pattern

When Betaflight receives a malformed MSP request (e.g., wrong payload size for MSP_DATAFLASH_READ), it responds with an error frame: `$M!` prefix instead of `$M>`.

**Common mistake:** Reading only the 3-byte header (`$M!`) and discarding it, leaving the rest of the frame in the buffer. This causes the **next read** to start mid-frame, triggering cascading parse failures that look like timeouts.

## The correct pattern

An MSP error frame has the same structure as a normal response frame:

```
$M! <flags> <cmd> <data...> <checksum>
```

Total frame length: **header (3) + flags (1) + cmd (1) + data (N) + checksum (1)** = 6 + N bytes

**Correct consumption:**

```python
# Read error header
header = serial.read(3)  # Reads: b'$M!'

# Then read the FULL frame structure just like a normal response
flags = serial.read(1)
cmd = serial.read(1)
# Read length from flags (if encoded in flags byte)
# Read data payload based on length
# Read checksum

# Only after consuming the full frame is the buffer clean
```

## Example failure (anti-pattern)

```python
# WRONG: reads only 3 bytes, leaves garbage in buffer
if header == b'$M!':
    # Assumes error, discards and loops
    continue  # Next iteration reads: b'flags><cmd' — GARBAGE!
```

This cascades: the next command timeout fires, caller retries, and the garbage bytes are still there, causing every subsequent command to misalign.

## Debugging this

When you see:
- "Read timeout waiting for frame" after a malformed request
- Multiple timeout retries in quick succession
- Or random checksum failures on the next command

The likely cause is an error frame that was partially consumed.

**Debug pattern:**

```python
import struct

def read_frame_complete(serial_port):
    """Read full MSP frame, including error frames."""
    # Read header
    header = serial_port.read(3)
    if header not in (b'$M>', b'$M!'):
        print(f"Bad header: {header.hex()}")
        return None
    
    is_error = (header == b'$M!')
    
    # Read flags and command
    flags = serial_port.read(1)[0]
    cmd = serial_port.read(1)[0]
    
    # Length is encoded in flags (low 7 bits)
    length = flags & 0x7F
    
    # Read payload
    data = serial_port.read(length)
    
    # Read checksum
    checksum = serial_port.read(1)[0]
    
    # Validate checksum (if needed)
    calculated = flags ^ cmd
    for byte in data:
        calculated ^= byte
    
    if calculated != checksum:
        print(f"Checksum mismatch! Expected {checksum:02x}, got {calculated:02x}")
    
    return {
        'is_error': is_error,
        'cmd': cmd,
        'data': data,
        'valid': calculated == checksum
    }
```

## Prevention

When adding or fixing MSP command handlers:

1. Always read the **full frame**, not just the header
2. Consume the entire payload before returning or looping
3. After an error condition, do a **confirmatory read** (attempt to read the prompt or next expected frame) to verify the buffer is clean
4. If implementing a timeout retry: first drain the buffer, then retry

## Related

- `serial_delimiter_false_positives.md` — general serial protocol debugging patterns
- `betaflight_msp_dataflash_payload_format.md` — malformed requests that trigger error frames
- `playbooks/betaflight_blackbox_pull_modes.md` — blackbox retrieval (which uses MSP_DATAFLASH_READ)
