# Selective Pulse Assist Comparison

**Status: insufficient data for motor performance or energy balance.**

Geometry: ASYM_B + EML +12° + gap 159.0 mm. The following values are raw magnetostatic 0–45° sector diagnostics.
The full electromagnetic and controller state has not been shown to repeat after 45°. No sector is extrapolated to 360°.
Mesh convergence, dynamic shaft output, electrical input and stored-energy changes remain unverified.

## Source Coverage

| Case | Status | Samples | Span (degrees) |
|---|---|---:|---:|
| coil-off | complete_sector_unverified | 46 | 45.0 |
| low | complete_sector_unverified | 46 | 45.0 |
| medium | complete_sector_unverified | 46 | 45.0 |
| high | complete_sector_unverified | 46 | 45.0 |

## Complete Sector Diagnostics

| Case | Raw 45° work (J) | Assist work (J) | Lockout work (J) | Peak + (Nm) | Peak − (Nm) | Cancellation | On-samples |
|---|---:|---:|---:|---:|---:|---:|---:|
| coil-off | 0.185689 | 1.108982 | -0.923294 | 4.934 | -3.739 | 0.910 | 0 |
| low | 0.180983 | 1.099832 | -0.918849 | 4.832 | -3.676 | 0.912 | 24 |
| medium | 0.180779 | 1.103532 | -0.922752 | 4.887 | -3.683 | 0.912 | 24 |
| high | 0.191553 | 1.106950 | -0.915397 | 4.825 | -3.676 | 0.907 | 24 |

## Raw Sector Differences from Coil-Off

| Case | 45° work difference (J) | Assist difference (J) | Lockout difference (J) |
|---|---:|---:|---:|
| low | -0.004705 | -0.009150 | 0.004445 |
| medium | -0.004909 | -0.005451 | 0.000541 |
| high | 0.005865 | -0.002032 | 0.007897 |

## Limits

Assist windows cover 21.0°; lockout windows cover 24.0°.
Incomplete sectors, missing samples, non-finite values, duplicate angles and reversed acquisition order cannot support a comparison.
An on-sample count is not a pulse-event count or a time duty cycle. Both legacy `coil_current_a` and `femm_single_turn_current_a` describe a one-turn FEMM surrogate; physical wire current requires the winding turn count.
Positive raw sector work or a small case difference is not evidence of sustained net output. A repeated operating cycle, signed electrical bus measurements, all auxiliary inputs, shaft work, losses, and stored-energy changes are required for an energy balance.
