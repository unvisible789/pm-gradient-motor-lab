# Best-So-Far Tracker

Date: 2026-06-15

## Current Best First-Screen

| Rank | Variant | Full-rev equivalent | Cancellation | Notes |
|---:|---------|--------------------:|-------------:|-------|
| 1 | ASYM_B + EML +12° + stator inner +1mm gap | 1.486 J/rev | 0.909 | new best; partial P2 screen |
| 2 | ASYM_B EML offset +12° | 1.159 J/rev | 0.934 | fine offset sweep peak |
| 3 | ASYM_B + EML +12° + EML arc −20% | 1.070 J/rev | 0.855 | lower cancellation |
| 4 | ASYM_B EML offset −6° | 1.112 J/rev | 0.937 | offset sweep |
| 5 | ASYM_B offset 0° | 0.952 J/rev | 0.946 | shape peak |

First screen only; not mesh-converged. None meet 3 J/rev promotion gate.

## Fine EML Offset Sweep (complete)

Peak at +12°. Past +12° net work falls: +15° 0.889, +18° 0.973, +21° 0.837, +9° 0.718 J/rev.

## Branch Status

- **ASYM shape search:** peaked at ASYM_B
- **TEB branch:** closed
- **EML offset sweep:** complete; peak +12°
- **P2/P3 optimization:** partial — gap+1mm promising; EML asymmetric pole and stator shunt FEMM failures need geometry fix

## Failed / Incomplete Runs

- `opt_eml_asym_mild`, `opt_eml_asym_moderate`: FEMM geometry failure (incomplete sweep)
- `opt_stator_shunt_center`, `opt_stator_shunt_leading`: FEMM geometry failure (incomplete sweep)
- `opt_stator_relief_2deg`: solved but net negative (−1.675 J/rev equivalent)

## Next Actions

1. Re-run/fix EML asymmetric pole and stator shunt geometry
2. Explore gap+1mm around +12° offset base (best partial result)
3. Re-extract pulse windows for best candidate
4. Do not mesh-refine until first-screen exceeds 3 J/rev gate