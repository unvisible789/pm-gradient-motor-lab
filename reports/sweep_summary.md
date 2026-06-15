# PM-Gradient Motor Parameter Sweep Energy Audit

## Purpose

This is simulation #2: a parameter sweep for the one-channel PM-gradient assisted motor audit. It is an audit tool only. It does **not** claim success, overunity, or a breakthrough.

Each case is flagged strictly by whether modeled mechanical work per pulse is less than or equal to the stated net electrical input per pulse of 0.017500 J.

## Sweep Inputs

- RPM sweep: 100 to 3000 RPM in 100 RPM steps
- Pulse window sweep: 1° to 20° in 1° steps
- Torque sweep: 0.1 Nm to 2.0 Nm in 0.1 Nm steps
- Gradients per revolution: 12
- Interaction channels: 1
- Net electrical energy per pulse: 0.017500 J (17.5 mJ)
- Friction/load torque: 0.800 Nm

## Equations

1. Angular speed: `omega = RPM * 2*pi / 60`
2. Pulse events per second: `f_pulse = RPM / 60 * gradients_per_revolution * channels`
3. Pulse window radians: `theta = pulse_window_deg * pi / 180`
4. Work per pulse: `W_pulse = torque * theta`
5. Electrical input power: `P_elec = net_electrical_energy_per_pulse * f_pulse`
6. Mechanical pulse power: `P_mech = W_pulse * f_pulse`
7. Load power: `P_load = load_torque * omega`
8. Net electrical energy per revolution: `E_elec_rev = net_electrical_energy_per_pulse * gradients_per_revolution`
9. Mechanical pulse energy per revolution: `E_mech_rev = W_pulse * gradients_per_revolution`
10. Load energy per revolution: `E_load_rev = load_torque * 2*pi`
11. Balance ratio: `ratio = W_pulse / net_electrical_energy_per_pulse`
12. Balance flag: `BALANCED if W_pulse <= net_electrical_energy_per_pulse else UNBALANCED`

## Sweep Summary

- Total cases: **12000**
- BALANCED cases: **810**
- UNBALANCED cases: **11190**
- Pulse events per second range: **20.000000 to 600.000000 pulses/s**
- Electrical input power range: **0.350000 to 10.500000 W**
- Load power range: **8.377580 to 251.327412 W**
- Net electrical energy per revolution: **0.210000 J/rev**
- Load energy per revolution: **5.026548 J/rev**

## Maximum Balanced Parameters With 17.5 mJ Net Electrical Input

Within this discrete sweep:

- Maximum torque that remains BALANCED: **1.0 Nm**
- That maximum torque is BALANCED only at pulse window(s): **1°**
- Maximum pulse window that remains BALANCED: **10°**
- That maximum pulse window is BALANCED only at torque value(s): **0.1 Nm**

Analytically, the balance boundary is `torque * radians(window_deg) <= 0.017500`. RPM changes power because it changes event rate, but it does not change the per-pulse balance ratio.

## Maximum BALANCED Torque by Pulse Window

| Pulse window (deg) | Maximum BALANCED torque in sweep (Nm) |
|---:|---:|
| 1 | 1.0 |
| 2 | 0.5 |
| 3 | 0.3 |
| 4 | 0.2 |
| 5 | 0.2 |
| 6 | 0.1 |
| 7 | 0.1 |
| 8 | 0.1 |
| 9 | 0.1 |
| 10 | 0.1 |
| 11 | none |
| 12 | none |
| 13 | none |
| 14 | none |
| 15 | none |
| 16 | none |
| 17 | none |
| 18 | none |
| 19 | none |
| 20 | none |

## Maximum BALANCED Pulse Window by Torque

| Torque (Nm) | Maximum BALANCED pulse window in sweep (deg) |
|---:|---:|
| 0.1 | 10 |
| 0.2 | 5 |
| 0.3 | 3 |
| 0.4 | 2 |
| 0.5 | 2 |
| 0.6 | 1 |
| 0.7 | 1 |
| 0.8 | 1 |
| 0.9 | 1 |
| 1.0 | 1 |
| 1.1 | none |
| 1.2 | none |
| 1.3 | none |
| 1.4 | none |
| 1.5 | none |
| 1.6 | none |
| 1.7 | none |
| 1.8 | none |
| 1.9 | none |
| 2.0 | none |

## Example BALANCED Combinations



| RPM | Torque (Nm) | Window (deg) | Work/pulse (J) | Balance ratio | Flag |
|---:|---:|---:|---:|---:|---|
| 800 | 0.1 | 1 | 0.001745 | 0.100 | BALANCED |
| 800 | 0.2 | 1 | 0.003491 | 0.199 | BALANCED |
| 800 | 0.3 | 1 | 0.005236 | 0.299 | BALANCED |
| 800 | 0.4 | 1 | 0.006981 | 0.399 | BALANCED |
| 800 | 0.5 | 1 | 0.008727 | 0.499 | BALANCED |
| 800 | 0.6 | 1 | 0.010472 | 0.598 | BALANCED |
| 800 | 0.7 | 1 | 0.012217 | 0.698 | BALANCED |
| 800 | 0.8 | 1 | 0.013963 | 0.798 | BALANCED |
| 800 | 0.9 | 1 | 0.015708 | 0.898 | BALANCED |
| 800 | 1.0 | 1 | 0.017453 | 0.997 | BALANCED |

## Example UNBALANCED Combinations



| RPM | Torque (Nm) | Window (deg) | Work/pulse (J) | Balance ratio | Flag |
|---:|---:|---:|---:|---:|---|
| 800 | 1.1 | 1 | 0.019199 | 1.097 | UNBALANCED |
| 800 | 1.2 | 1 | 0.020944 | 1.197 | UNBALANCED |
| 800 | 1.3 | 1 | 0.022689 | 1.297 | UNBALANCED |
| 800 | 1.4 | 1 | 0.024435 | 1.396 | UNBALANCED |
| 800 | 1.5 | 1 | 0.026180 | 1.496 | UNBALANCED |
| 800 | 1.6 | 1 | 0.027925 | 1.596 | UNBALANCED |
| 800 | 1.7 | 1 | 0.029671 | 1.695 | UNBALANCED |
| 800 | 1.8 | 1 | 0.031416 | 1.795 | UNBALANCED |
| 800 | 1.9 | 1 | 0.033161 | 1.895 | UNBALANCED |
| 800 | 2.0 | 1 | 0.034907 | 1.995 | UNBALANCED |

## Interpretation

The sweep stays conservative: a case is only BALANCED when the modeled mechanical pulse work does not exceed the stated net electrical pulse input. Cases above that threshold are marked UNBALANCED and require an identified, measured energy source before they can be interpreted as physically closed.

Because the electrical energy per pulse is fixed, wider windows require lower torque to remain balanced, and higher torque requires narrower windows. RPM scales both electrical input power and mechanical pulse power for a fixed torque/window pair, while the per-pulse balance ratio remains unchanged.

## Output Files

- `sweep_results.csv`
- `sweep_summary.md`
- `torque_energy_sweep.py`
