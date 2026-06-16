# ASYM_B Selective Assist Analysis

**Source CSV:** `C:/Users/Owner/Documents/Codex/pm-gradient-motor-lab/data/field_sim/femm_asym_b_period45_step1.csv`
**Pulse windows:** `C:/Users/Owner/Documents/Codex/pm-gradient-motor-lab/field_sim/femm/pulse_strategy.asym_b.json`

First screen only; not mesh-converged. No performance claims.

## Passive Torque Work Over 45°

| Region | Angle span (deg) | Integrated work (J) |
|--------|-----------------:|--------------------:|
| Assist windows | 21.0 | 1.152931 |
| Lockout windows | 24.0 | -1.033968 |
| Full 45° period | 45.0 | 0.118962 |

Full-revolution equivalent (×8): **0.951698 J/rev**

## Assist / Lockout Windows

**Assist:** 2.0–13.0°, 25.0–35.0°

**Lockout:** 0.0–2.0°, 13.0–25.0°, 35.0–45.0°

## Control Metrics

| Metric | Value |
|--------|------:|
| Negative-angle fraction (`f_neg`) | 0.533 |
| Gross positive work over 45° (J) | 1.162759 |
| Gross negative work over 45° (J) | 1.043797 |
| Assist work / gross work | 0.523 |
| Lockout work / gross work | -0.469 |

## Interpretation

Selective pulsing should fire only in assist windows and remain off during lockout windows.
Lockout regions still carry -1.033968 J of passive torque work over 45°; pulsing there would waste electrical input unless coil energization changes the local torque balance.

This analysis does not include energized EML coil effects or electrical pulse energy accounting.
