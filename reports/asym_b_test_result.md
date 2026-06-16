# ASYM_B FEMM Test Result

**Date/time:** 2026-06-15 20:10:11 (local FEMM execution agent run)

## Configuration

- `verification_label`: ASYM_B
- `asymmetric_pole_enabled`: true
- `trailing_edge_barrier_enabled`: false
- `asymmetric_leading_extension_deg`: 2.0
- `asymmetric_trailing_pullback_deg`: 2.0
- `asymmetric_leading_outer_radius_mm`: 145.0
- `asymmetric_trailing_outer_radius_mm`: 140.0
- All other parameters: unchanged from baseline (`anti_cancellation_v1`)

## Sweep Parameters

- Period: 45°
- Step: 1°
- Points: 46
- Output CSV: `data/field_sim/femm_asym_b_period45_step1.csv`

## Results

| Metric | Value |
|--------|------:|
| 45° integrated work | 0.118962 J |
| Full-rev equivalent work (×8) | 0.951698 J/rev |
| Average torque | 0.151467 Nm |
| Peak positive torque | 5.044163 Nm at 7.0° |
| Peak negative torque | -3.994062 Nm at 20.0° |

## FEMM Status

No FEMM errors reported. Sweep completed in ~85 seconds (46 points).

## Note

This is a 45° / 1° first screen, not mesh-converged.