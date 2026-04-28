---
name: Config diff completeness validation
description: Ensuring all section types (dicts and lists) are included in config diffs; catching invisible safety-critical changes
type: feedback
---

# Config Diff Completeness

## The problem

When diffing structured config files with mixed dict and list sections, it's easy to wire up comparison logic for one section type (e.g., key-value pairs) and forget another (e.g., feature lists). This leaves entire categories invisible to the diff, hiding safety-critical changes.

**Why this happened:** Built a Betaflight config differ that compared all dict-based sections (settings, parameters) but skipped list sections entirely (features, aux modes, serial assignments). A change to serial port assignments (safety-critical for MSP bridging) was completely invisible in the diff, nearly shipped a broken config.

## Solution: section inventory

Before writing diff logic, enumerate all section types in the config format. Diff each one explicitly.

**How to apply:**

### 1. Inventory all sections
For Betaflight config, the sections are:
- **Dicts:** `profile`, `set` (key-value pairs)
- **Lists:** `feature`, `aux`, `serial` (comma or colon-separated, one per line)

### 2. Diff each section type explicitly

```python
def diff_betaflight_config(old_config, new_config):
    """
    Diff a Betaflight CLI config, covering all section types.
    """
    diffs = {
        "profile": {},
        "set": {},
        "feature": {},
        "aux": {},
        "serial": {},
    }
    
    # Dict sections: simple key-value comparison
    for section in ["profile", "set"]:
        old_dict = parse_section_dict(old_config, section)
        new_dict = parse_section_dict(new_config, section)
        
        # Find added/changed/removed keys
        for key in set(old_dict.keys()) | set(new_dict.keys()):
            old_val = old_dict.get(key)
            new_val = new_dict.get(key)
            
            if old_val != new_val:
                diffs[section][key] = (old_val, new_val)
    
    # List sections: parse and compare
    for section in ["feature", "aux", "serial"]:
        old_list = parse_section_list(old_config, section)
        new_list = parse_section_list(new_config, section)
        
        # Find added/removed items
        old_set = set(old_list)
        new_set = set(new_list)
        
        if old_set != new_set:
            diffs[section] = {
                "removed": list(old_set - new_set),
                "added": list(new_set - old_set),
            }
    
    return diffs


def report_diffs(diffs):
    """Print a human-readable diff report."""
    has_changes = any(v for v in diffs.values())
    if not has_changes:
        print("No changes detected.")
        return
    
    for section, changes in diffs.items():
        if not changes:
            continue
        
        print(f"\n[{section.upper()}]")
        
        if isinstance(changes, dict):
            # Could be key-value pairs or list diffs
            if "removed" in changes:
                # List section
                if changes["removed"]:
                    print(f"  Removed: {changes['removed']}")
                if changes["added"]:
                    print(f"  Added: {changes['added']}")
            else:
                # Dict section
                for key, (old, new) in changes.items():
                    print(f"  {key}: {old} → {new}")
```

### 3. Validation checklist

Before considering a diff complete:

- [ ] All section types from the format spec are explicitly diffed
- [ ] Diff logic handles added, removed, and modified items
- [ ] Report includes all changed sections
- [ ] Safety-critical sections (e.g., serial assignments, feature flags) are explicitly listed in the report
- [ ] Unit tests cover at least one change in each section type

## Config formats covered

This pattern applies to:
- **Betaflight CLI** — profiles, settings, features, aux modes, serial assignments
- **EdgeTX models** — mixed YAML structure (scalars + list arrays)
- **Terraform/HCL** — resource attributes + nested blocks
- Any config with multiple structural section types

## Related playbooks
- `betaflight_dji_msp.md` — Betaflight CLI settings reference
- `radio_edgetx_config_generation.md` — EdgeTX model structure
