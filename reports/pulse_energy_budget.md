# Pulse Energy Budget

**Illustration only; insufficient data for electrical input, efficiency or net generation.** Defaults are assumed numbers, not a qualified APW drive waveform. One half L I squared measures stored magnetic energy, not complete pulse input.

## Assumptions

| Parameter | Value |
|---|---:|
| Pulse window file | `field_sim/femm/pulse_strategy.asym_b.json` |
| Legacy assist-window coverage over 45.0 deg | 0.467 |
| EML count | 8 |
| Coil inductance | 5.000 mH |
| Pulse current | 2.000 A |
| Flyback/recovery efficiency | 0.750 |
| Assumed pulses per EML per 45 deg sector | 1.000 |
| Unvalidated torque-integral diagnostic | 1.159000 J/rev |

## Illustrative magnetic storage

| Metric | Value |
|---|---:|
| Stored magnetic energy per pulse, 0.5 L I^2 | 0.010000 J |
| Assumed unrecovered storage per pulse | 0.002500 J |
| Pulses per revolution | 64.000 |
| Assumed unrecovered storage over all events | 0.160000 J/rev |
| Total electrical input | Unknown |
| Net generation / efficiency | Not evaluated |

## Interpretation

Neither a sampled angular fraction nor a magnet/coil count ratio determines a pulse count. The event count above is an explicit illustrative assumption and needs a complete per-channel switching schedule before use.

Measure signed source voltage times current, all auxiliary and drive inputs, useful output, and stored-energy changes over a complete repeat. Include motion-induced voltage and winding heating. If returned energy is already in the signed source integral, do not subtract recovery again. A positive passive torque residual must not be treated as available shaft energy.
