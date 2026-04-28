---
name: Betaflight CLI get output parsing gotcha
description: get <param> returns all matching lines; must use line-start matching, not substring search
type: playbook
---

# Betaflight CLI `get` Command Output Parsing

## The problem

The Betaflight CLI `get` command returns **all parameters whose names contain the search string**, not just an exact match. Parsing with substring matching produces incorrect results.

**Example:**
```
> get d_roll
align_board_roll = 180
d_roll = 28
```

If your parser uses `"d_roll" in line`, it will match `align_board_roll` first and extract the value `180`, which is wrong.

## Why

The `get` command is a simple substring filter over the full parameter list. It doesn't distinguish between parameters that *start* with the search string vs. those that *contain* it anywhere in the name.

## How to apply

**Always use line-start matching when parsing `get` output:**

```python
def parse_get_output(serial_port, param_name, timeout=2.0):
    """
    Execute 'get <param>' and return the value.
    Uses line-start matching to avoid substring collisions.
    """
    serial_port.write(f"get {param_name}\r\n".encode())
    buffer = read_until_prompt(serial_port, timeout)
    
    for line in buffer.decode().split('\n'):
        line = line.strip()
        # Match only lines that START with the param name
        if line.startswith(f"{param_name} ="):
            # Parse: "param_name = value"
            parts = line.split('=', 1)
            if len(parts) == 2:
                return parts[1].strip()
    
    raise ValueError(f"Parameter {param_name} not found in get output")
```

**Wrong approach (substring matching):**
```python
# DON'T DO THIS
if "d_roll" in line:  # Matches "align_board_roll" first
    value = line.split('=')[1]
```

**Right approach (line-start matching):**
```python
# DO THIS
if line.startswith("d_roll ="):
    value = line.split('=')[1].strip()
```

## Common parameter prefix collisions

These real parameters are likely to collide if you use substring matching:

| Search | Also matches |
|--------|--------------|
| `roll` | `board_roll`, `yaw_roll_coupling`, `d_roll` |
| `pitch` | `pitch_roll_i`, `pitch_p`, `pitch_d`, etc. |
| `d_roll` | `align_board_roll` |
| `i_pitch` | `pitch_roll_i` |
| `aux` | `aux_channel`, `rc_aux` (also others) |

## Alternative: exact match with `get all` dump

If you need to parse many parameters, get the full `dump all` output once and build a dict:

```python
def parse_full_config(serial_port, timeout=5.0):
    """Parse all parameters from 'dump all' into a dict."""
    serial_port.write(b"dump all\r\n")
    buffer = read_until_prompt(serial_port, timeout)
    config = {}
    
    for line in buffer.decode().split('\n'):
        line = line.strip()
        if '=' in line and not line.startswith('#'):
            parts = line.split('=', 1)
            param_name = parts[0].strip()
            param_value = parts[1].strip()
            config[param_name] = param_value
    
    return config

# Usage: much faster for bulk reads
config = parse_full_config(port)
d_roll = config['d_roll']  # Exact match, no collision
```

## Related
- `betaflight_cli_gotchas_2025.md` — other CLI quirks (acc_calibration, save command reboot)
- `serial_delimiter_false_positives.md` — handling `diff all` output with comment lines
- `betaflight_dji_msp.md` — general Betaflight CLI reference
