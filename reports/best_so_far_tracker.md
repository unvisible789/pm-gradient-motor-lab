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

## Selective Pulse Assist (2026-06-15)

Coil-off baseline: **1.486 J/rev** (matches passive gap 159 screen).

| Pulse level | Current (A) | Full-rev equiv | Δ vs coil-off | Net after placeholder input |
|---|---:|---:|---:|---:|
| low (5 mA/mm²) | 3.67 | 1.448 J/rev | −0.038 | −0.389 J/rev |
| medium (10 mA/mm²) | 7.34 | 1.446 J/rev | −0.039 | −1.424 J/rev |
| high (20 mA/mm²) | 14.68 | 1.532 J/rev | +0.047 | −5.473 J/rev |

**Conclusion:** Selective pulsing does **not** close energy on first screen. Low/medium reduce net work; high adds +0.047 J/rev mechanically but far below estimated electrical input. Assist-window work decreased at all levels. No mesh refinement.

Reports: `reports/pulse_assist_comparison.md`, `reports/pulse_electrical_accounting.md`

## Next Actions

1. Do not pursue higher pulse current without measured L/R and recovery data
2. Do not mesh-refine until >3 J/rev or cancellation <0.85 with torque dominance
3. Fix shunt variant JSON radii if stator shunt branch is reopened

Build recommendation: **unchanged — no full motor build**.