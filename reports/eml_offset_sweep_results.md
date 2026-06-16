# ASYM_B EML Angular Offset Sweep

**Date/time:** 2026-06-15 20:38:45

**Protocol:** 45° period, 1° step, ASYM_B rotor geometry fixed, `eml_angular_offset_deg` varied.

First screen only; not mesh-converged. No performance claims.

## Results

| EML offset (deg) | Full-rev equiv (J/rev) | 45° work (J) | Peak + (Nm @ °) | Peak − (Nm @ °) | Cancellation | Decision |
|-----------------:|----------------------:|-------------:|----------------:|----------------:|-------------:|----------|
| +12 | 1.159 | 0.145 | 4.849 @ 18 | −3.954 @ 32 | 0.934 | hold for nearby offsets |
| −6 | 1.112 | 0.139 | 5.020 @ 45 | −3.991 @ 14 | 0.937 | hold for nearby offsets |
| −12 | 1.067 | 0.133 | 4.895 @ 16 | −3.888 @ 9 | 0.940 | hold for nearby offsets |
| 0 | 0.952 | 0.119 | 5.044 @ 7 | −3.994 @ 20 | 0.946 | weak positive |
| +6 | 0.898 | 0.112 | 4.954 @ 34 | −4.078 @ 2 | 0.949 | weak positive |

## Interpretation

EML phasing helps modestly. +12° offset improved full-rev equivalent from 0.952 to 1.159 J/rev (~22% relative to offset 0°), but still below the 3 J/rev promotion gate.

Peak positive and peak negative magnitudes remain similar; cancellation is slightly reduced but not broken.

## Recommended Next Step

If continuing EML phasing, test nearby offsets around +12° (e.g. +9°, +15°, +18°) before mesh refinement. Do not mesh-refine until a first-screen result clearly exceeds 3 J/rev or shows a strong cancellation improvement.