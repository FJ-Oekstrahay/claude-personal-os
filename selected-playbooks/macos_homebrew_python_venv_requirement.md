---
name: macOS Homebrew Python venv Requirement
description: Homebrew Python 3.14+ blocks system-wide pip with externally-managed-environment error; must use venv to install packages
type: playbook
---

# macOS Homebrew Python venv Requirement

## The Problem

Homebrew Python 3.14+ (and some earlier versions) enforces PEP 668 external environment isolation. Direct `pip install` fails with:

```
ERROR: externally-managed-environment

× This environment was not created by this Python distribution,
  and thus cannot be safely used to install packages as requested.

× Use an isolated virtual environment instead.
```

This blocks project setup when requirements are installed to system Python.

## Root Cause

Homebrew packages Python with a marker file (`/usr/local/Cellar/python@3.14/*/lib/pythonX.Y/EXTERNALLY-MANAGED`) that prevents pip operations outside a virtual environment. This is intentional — to avoid conflicts with Homebrew's own package management.

## How to Apply

**Always use a venv for Homebrew Python projects:**

```bash
# In your project root
python3 -m venv .venv

# Activate the venv
source .venv/bin/activate

# Now pip install works
pip install -r requirements.txt

# Verify the path uses the venv
which python   # Should be /path/to/project/.venv/bin/python
```

## One-Time Setup for Projects

Add this to a project's initialization or CI/CD:

```bash
#!/bin/bash
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
fi
source .venv/bin/activate
pip install -r requirements.txt
```

## Development Workflow

After initial setup, always activate before developing:

```bash
# Before each session
source .venv/bin/activate

# Verify activation (prompt should show (.venv))
python -V

# Deactivate when done (optional)
deactivate
```

## Why Not System Python?

**Never attempt to bypass this with:**

```bash
# DON'T do this — will fail or cause issues
pip install --break-system-packages -r requirements.txt
```

The restriction exists for good reason: Homebrew package updates could conflict with user-installed pip packages.

## If Scripts or Shebangs Don't Work

If you have scripts that use `#!/usr/bin/env python3` or similar, they may ignore the venv. Ensure the venv is always activated before running scripts:

```bash
source .venv/bin/activate
python scripts/myapp.py
```

Alternatively, use the full venv path in shebangs:

```bash
#!/path/to/project/.venv/bin/python3
```

## Related

- Homebrew Python documentation (official): https://docs.brew.sh/Homebrew-and-Python
- PEP 668: https://peps.python.org/pep-0668/
