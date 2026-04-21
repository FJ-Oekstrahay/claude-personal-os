---
name: Eval harness serial port exclusivity
description: Serial port is exclusive — FC-connected eval tests and bench tests cannot run in parallel
type: feedback
originSessionId: c0884e37-2b6e-42e8-b9df-8527a068ad7c
---
Serial ports are exclusive: only one process can hold the port at a time.

Two FC-connected tests cannot run simultaneously. Running the eval harness and a bench test in parallel will cause one to fail with a port-busy or permission error.

**Why:** The OS grants exclusive access to `/dev/tty*` devices. A second process connecting to the same port while the first holds it will be refused.

**How to apply:** Always serialize FC-connected test runs. Run the eval harness first (or finish it), then run bench tests. Never launch both in parallel, even if they look independent.
