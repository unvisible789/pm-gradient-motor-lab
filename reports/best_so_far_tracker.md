# Best-So-Far Tracker

Date: 2026-06-15

## Current Accepted Baseline

Mesh-refined current geometry is near-zero to slightly negative net work. Treat all auto-mesh positive values as untrusted until mesh convergence is shown.

## ASYM Family First-Screen (complete)

| Variant | Full-rev equivalent | Peak + | Peak − | Decision |
|---|---:|---:|---:|---|
| ASYM_B | 0.952 J/rev | 5.044 Nm | -3.994 Nm | best in family; weak positive, do not promote |
| ASYM_D | 0.465 J/rev | 4.249 Nm | -3.459 Nm | weak positive, do not promote |
| ASYM_C | -0.127 J/rev | 4.455 Nm | -3.627 Nm | reject |
| ASYM_A | -0.260 J/rev | 5.490 Nm | -5.093 Nm | reject |
| TEB_B | 0.343 J/rev | 6.277 Nm | -6.175 Nm | weak positive, do not promote |

## What We Learned

ASYM_B is the peak of the first asymmetric-magnet shape search. More or less asymmetry does not improve net work. TEB_B remains weaker than ASYM_B.

None of the screened variants meet the 3 J/rev mesh-refinement gate.

## Next Variants To Run

1. EML angular offset sweep on ASYM_B (e.g. -12, -6, 0, +6, +12 deg)
2. `teb_a_2deg_134_145`, `teb_c_4deg_130_145`, `teb_d_3deg_126_145` for branch closure
3. Selective pulsing analysis using `field_sim/femm/pulse_strategy.asym_b.json`

Promote only if a first-screen result is clearly stronger than ASYM_B, preferably above 3 J/rev equivalent or showing much lower cancellation with stronger positive/negative imbalance.