# Best-So-Far Tracker

Date: 2026-06-15

## Current Best First-Screen

| Rank | Variant | Full-rev equivalent | Notes |
|---:|---------|--------------------:|-------|
| 1 | ASYM_B EML offset +12° | 1.159 J/rev | best overall; still below 3 J/rev gate |
| 2 | ASYM_B EML offset −6° | 1.112 J/rev | nearby hold candidate |
| 3 | ASYM_B EML offset −12° | 1.067 J/rev | nearby hold candidate |
| 4 | ASYM_B offset 0° | 0.952 J/rev | asymmetric shape peak |
| 5 | TEB_A | 0.766 J/rev | TEB branch closed |

## Branch Status

- **ASYM shape search:** peaked at ASYM_B
- **TEB branch:** closed (A/B/C/D screened)
- **EML phasing:** modest gain; best at +12°

## Selective Assist (ASYM_B offset 0°)

- Assist: 2–13°, 25–35°
- Lockout: 0–2°, 13–25°, 35–45°
- `f_neg` ≈ 0.533 over 45°
- See `reports/asym_b_selective_assist_analysis.md`

## Next Actions

1. Fine EML offset search around +12° (+9, +15, +18)
2. Re-extract pulse windows for best EML-offset candidate after sweep
3. Do not mesh-refine until first-screen result exceeds 3 J/rev gate

Promote only if clearly above 3 J/rev equivalent or showing much lower cancellation with stronger positive/negative imbalance.