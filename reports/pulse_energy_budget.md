# Pulse Energy Budget

First-order accounting only. Replace defaults with measured coil L/R/current and driver recovery data before making design claims.

## Assumptions

| Parameter | Value |
|---|---:|
| Pulse window file | `C:/Users/Owner/Documents/Codex/pm-gradient-motor-lab/field_sim/femm/pulse_strategy.asym_b.json` |
| Assist duty over 45.0 deg | 0.467 |
| EML count | 8 |
| Coil inductance | 5.000 mH |
| Pulse current | 2.000 A |
| Flyback/recovery efficiency | 0.750 |
| Pulses per EML per 45 deg period | 1.000 |
| Mechanical first-screen work | 1.159000 J/rev |

## Estimated Energy

| Metric | Value |
|---|---:|
| Stored magnetic energy per pulse, 0.5 L I^2 | 0.010000 J |
| Unrecovered input per pulse | 0.002500 J |
| Pulses per revolution | 64.000 |
| Unrecovered pulse input | 0.160000 J/rev |
| Mechanical work minus unrecovered pulse input | 0.999000 J/rev |

## Interpretation

This does not model energized torque yet. It only prevents pulse assist from being treated as free.
If FEMM later shows added mechanical work from coil current, compare only the added work against measured or simulated electrical input plus switching, copper, core, and recovery losses.
