# Selective Pulse Assist Comparison

**Date:** 2026-06-15

**Geometry:** ASYM_B + EML +12° + gap 159.0 mm
**Pulse windows:** `C:/Users/Owner/Documents/Codex/pm-gradient-motor-lab/field_sim/femm/pulse_strategy.gap159_eml12.json`

Assist: 0–2°, 14–25°, 37–45°. Lockout: 2–14°, 25–37°.
First screen only; not mesh-converged. No performance claims unless net energy closes.

## Summary

| Case | 45° work (J) | Full-rev equiv (J/rev) | Assist work (J) | Lockout work (J) | Peak + (Nm) | Peak − (Nm) | Cancellation | Pulsed angles |
|------|---:|---:|---:|---:|---:|---:|---:|---:|
| coil-off | 0.185689 | 1.485508 | 1.108982 | -0.923294 | 4.934 | -3.739 | 0.909 | 0 |
| low | 0.180983 | 1.447867 | 1.099832 | -0.918849 | 4.832 | -3.676 | 0.911 | 24 |
| medium | 0.180779 | 1.446234 | 1.103532 | -0.922752 | 4.887 | -3.683 | 0.912 | 24 |
| high | 0.191553 | 1.532425 | 1.106950 | -0.915397 | 4.825 | -3.676 | 0.906 | 24 |

## Delta vs Coil-Off Baseline

| Case | Added 45° work (J) | Added full-rev (J/rev) | Assist Δ (J) | Lockout Δ (J) | Peak + Δ (Nm) | Peak − Δ (Nm) | Cancel Δ |
|------|---:|---:|---:|---:|---:|---:|---:|
| low | -0.004705 | -0.037641 | -0.009150 | 0.004445 | -0.102 | 0.063 | 0.002 |
| medium | -0.004909 | -0.039274 | -0.005451 | 0.000541 | -0.047 | 0.056 | 0.002 |
| high | 0.005865 | 0.046917 | -0.002032 | 0.007897 | -0.109 | 0.063 | -0.003 |

## Window Spans

- Assist span: 21.0°
- Lockout span: 24.0°

## Interpretation

Added mechanical work must exceed estimated electrical input before claiming pulse assist benefit.
Lockout-region work should not become more negative when coils are off outside assist windows.
