# ASYM Family First-Screen Results

**Date/time:** 2026-06-15 20:21:17 (local FEMM execution agent)

**Protocol:** 45° period sweep at 1° resolution. First screen only; not mesh-converged.

## Summary

| Variant | Full-rev equiv (J/rev) | 45° work (J) | Peak + (Nm @ °) | Peak − (Nm @ °) | Cancellation | FEMM | Decision |
|---------|----------------------:|-------------:|----------------:|----------------:|-------------:|------|----------|
| ASYM_B | 0.952 | 0.119 | 5.044 @ 7 | −3.994 @ 20 | 0.946 | solved | weak positive, do not promote |
| ASYM_D | 0.465 | 0.058 | 4.249 @ 30 | −3.459 @ 42 | 0.969 | solved | weak positive, do not promote |
| ASYM_C | −0.127 | −0.016 | 4.455 @ 7 | −3.627 @ 20 | 0.992 | solved | reject |
| ASYM_A | −0.260 | −0.033 | 5.490 @ 6 | −5.093 @ 42 | 0.987 | solved | reject |

## Interpretation

ASYM_B remains the best first-screen direction in the asymmetric-magnet family. Milder (ASYM_A) and stronger (ASYM_C) asymmetry both went net negative. Aggressive ASYM_D stayed weakly positive but below ASYM_B.

No variant met the 3 J/rev promotion gate. The asymmetric shape search appears to have peaked near ASYM_B.

## ASYM_B Pulse Windows (Priority 2 prep)

Derived from `data/field_sim/femm_asym_b_period45_step1.csv`:

**Assist windows:**
- 2.0° → 13.0°
- 25.0° → 35.0°

**Lockout windows:**
- 0.0° → 2.0°
- 13.0° → 25.0°
- 35.0° → 45.0°

Saved to `field_sim/femm/pulse_strategy.asym_b.json`.

## Recommended Next Step

Do not mesh-refine ASYM_B yet. Next efficient moves:

1. EML angular offset sweep on ASYM_B geometry
2. Selective pulsing analysis using the ASYM_B windows
3. TEB family completion for comparison only

## Note

This is a 45° / 1° first screen, not mesh-converged. No performance claims.