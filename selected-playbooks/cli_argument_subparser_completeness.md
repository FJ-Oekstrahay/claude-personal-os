---
name: CLI argument subparser completeness
description: Missing args in subparsers causes silent failures; e.g., dt motor check --craft was missing
type: feedback
---

The `dt motor` subcommands (`check`, `health`, `map`) were missing CLI arguments that the command implementations expected (`--craft`, `--port`). This caused silent failures when users tried to use the documented flags.

**Why:** When subcommands and their argparse configuration drift, users get confusing "unrecognized arguments" errors or the arguments are silently ignored. Testing only the main command path doesn't catch missing subparser args.

**How to apply:**
- After adding new CLI arguments to a command implementation:
  1. Update both the main parser AND all subparsers that use those arguments
  2. If the argument is subcommand-specific, add it only to that subparser
  3. If it's shared across subcommands, add it to a parent group (if using subparsers with parents)
- Test each subcommand explicitly: `dt motor check --craft X`, `dt motor health --port Y`
- Use `-h` / `--help` on subcommands to verify args are listed
- This is especially important for droneteleo where hardware selection (--craft, --port) is critical across multiple commands
