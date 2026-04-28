---
name: Serial port contention pattern (FC access)
description: Handling multiple processes accessing the same flight controller UART; explicit serialization
type: feedback
---

When two processes need to access the same flight controller via serial port (e.g., Betaflight Configurator + Python automation agent), explicit serialization is required. Do not attempt concurrent access to the same UART.

**Pattern:** Disconnect BF Configurator from the port, perform the Python agent write, then reconnect BF Configurator. This avoids port conflicts and garbled data.

**How to apply:**
- Before running a Python agent that writes to an FC serial port, close the BF Configurator connection or unplug/replug the USB cable to release the port
- After the Python agent finishes, reconnect/reopen in BF Configurator
- If polling or repeated writes are needed, implement a simple lock or flag to ensure only one process touches the port at a time

**Why:** Flight controller UARTs are single-consumer. Two processes fighting for the same port can cause transmission errors, corrupted settings, or incomplete CLI commands. This was discovered during agent-FC interaction testing.
