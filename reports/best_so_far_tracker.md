# Best-So-Far Tracker

Date: 2026-06-15

## Current Best First-Screen

| Rank | Variant | Full-rev equivalent | Cancellation | Notes |
|---:|---------|--------------------:|-------------:|-------|
| 1 | ASYM_B + EML +12° + gap 159.0 mm | **1.486 J/rev** | 0.909 | sharp gap optimum |
| 2 | gap 159 + Halbach 15° | 1.413 J/rev | 0.909 | combo worse than gap alone |
| 3 | ASYM_B + EML +12° (gap 158) | 1.159 J/rev | 0.934 | offset-only baseline |
| 4 | gap 159.5 mm | 0.834 J/rev | 0.948 | past optimum |

First screen only; not mesh-converged. None meet 3 J/rev promotion gate.

## Gap Sweep Conclusion

Optimum at **stator_inner_radius_mm = 159.0**. Inward (−0.5 mm) and outward (+0.5 mm and beyond) both reduce net work.

## Branch Status

- ASYM shape: peaked at ASYM_B
- EML offset: peaked at +12°
- Stator gap: peaked at 159.0 mm
- Gap combinations: none beat gap 159 alone
- TEB branch: closed

## Pulse Strategy

Best candidate windows: `field_sim/femm/pulse_strategy.gap159_eml12.json`

## Next Actions

1. Selective assist / energized EML pulse planning on gap 159 candidate
2. Do not mesh-refine until >3 J/rev or cancellation <0.85 with torque dominance
3. Fix shunt variant JSON radii if stator shunt branch is reopened

Build recommendation: **unchanged — no full motor build**.