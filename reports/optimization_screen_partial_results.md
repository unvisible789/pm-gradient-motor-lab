# Optimization Screen Partial Results (P2/P3)

**Date:** 2026-06-15

**Base:** ASYM_B + EML offset +12°. 45° period, 1° step. First screen only; not mesh-converged.

## Completed Runs

| Variant | Change | Full-rev equiv (J/rev) | Cancellation | Decision |
|---------|--------|----------------------:|-------------:|----------|
| `opt_stator_inner_gap_plus1mm` | stator inner radius 159 mm | 1.486 | 0.909 | hold |
| `opt_eml_arc_minus20pct` | EML arc 11.2° | 1.070 | 0.855 | hold |
| `opt_eml_arc_minus10pct` | EML arc 12.6° | 0.952 | 0.925 | weak |
| `opt_eml_arc_minus30pct` | EML arc 9.8° | 0.543 | 0.872 | weak |
| `opt_stator_inner_gap_minus1mm` | stator inner radius 157 mm | 0.122 | 0.993 | weak |
| `opt_stator_relief_2deg` | trailing stator air relief 2° | −1.675 | 0.907 | reject |

## FEMM Failures (not completed)

- `opt_eml_asym_mild`, `opt_eml_asym_moderate` — asymmetric EML pole shoe geometry
- `opt_stator_shunt_center`, `opt_stator_shunt_leading` — stator back-iron shunt geometry

## Not Yet Run

- `opt_stator_relief_3deg`, `opt_stator_relief_4deg`

## Note

`opt_stator_inner_gap_plus1mm` is the best first-screen result so far (1.486 J/rev) but remains below the 3 J/rev gate and is not mesh-converged.