---
name: Hardware Isolation Testing
description: 4-test matrix for isolating faulty components when multiple hardware pieces interact
type: reference
---

# Hardware Isolation Testing — 4-Test Matrix

When a system with two or more hardware components fails and software/config has been ruled out, use a systematic swap matrix to isolate which component is defective.

## The Pattern

With two drones (A and B) and a component suspected of failure, create a 2×2 test matrix:

| Test | Component A | Component B | Result |
|------|-------------|-------------|--------|
| 1 | Drone A part | Drone A part | ❌ Fails |
| 2 | Drone B part | Drone A part | ✅ Works |
| 3 | Drone A part | Drone B part | ✅ Works |
| 4 | Drone B part | Drone B part | ✅ Works |

**Read the matrix:**
- If a single variable (the part from Drone A in all tests where it's used) correlates with failure in all test 1 and 4 but works in 2 and 3: that part is defective.

## Real Example: Seeker3 OSD Cable (April 6, 2026)

**Context:** Seeker3 drone had non-functional OSD despite:
- Firmware flashed 4+ times
- CLI settings verified against factory config
- Wiring tested with multimeter (continuity passed)
- All firmware versions updated

Reference drone: QAV-2 3" with DJI O4 (working OSD)

**Key fact:** O4 and O4 Pro air units use the same 6-pin FC connector — cables are bench-swappable.

| Test | Air Unit | Cable | FC | Result |
|------|----------|-------|----|--------|
| 1 | Seeker3 O4 Pro | DeepSpace cable | Seeker3 FC | ❌ No OSD, low power mode |
| 2 | QAV O4 | QAV cable | Seeker3 FC | ✅ OSD works |
| 3 | Seeker3 O4 Pro | QAV cable | QAV FC | ✅ OSD works |
| 4 | QAV O4 | DeepSpace cable | QAV FC | ❌ No OSD, low power mode |

**Isolation:** The DeepSpace cable is the single variable in all failures (tests 1 and 4) and absences in all successes (tests 2 and 3).

**Conclusion:** DeepSpace cable is defective. Multimeter continuity passed (wires intact), so the defect is a pin short or incorrect pin assignment not detectable with basic continuity.

## When to Use This

- Multiple interacting hardware pieces
- Software/config fully verified as correct
- Bench testing available (can physically swap components between systems)
- Need certainty before claiming warranty/DOA

## When NOT to Use This

- Only one test system available
- Can't safely swap the component
- The component is integrated/non-swappable
- Need faster turnaround than diagnostic rigor justifies

## Key Principle

A single test (even one that fails) doesn't isolate the problem. You need the *matrix* to see which variable is causative.
