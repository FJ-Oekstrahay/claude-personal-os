---
name: Signal swallowing in interrupt handling
description: Ctrl-C during LLM calls was swallowed; ensure signal handlers propagate interrupts
type: feedback
---

Ctrl-C (SIGINT) was being swallowed during LLM calls, making the CLI unresponsive to user interrupts.

**Why:** If signal handlers are installed but don't re-raise or propagate the interrupt, the main loop continues waiting. Users expect Ctrl-C to kill the operation immediately.

**How to apply:**
- When installing signal handlers (e.g., `signal.signal(signal.SIGINT, handler)`), ensure the handler either:
  - Re-raises the signal after cleanup: `raise KeyboardInterrupt`
  - Propagates the exception to the event loop (for async code)
  - Sets a flag that the event loop checks and exits on
- Test interrupt behavior during blocking operations: LLM calls, serial port waits, file I/O
- This is especially important in agent.py where long-running operations are common
