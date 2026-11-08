# Illustrative release-cycle accounting study

## Status and objective

**Illustrative analytic reference; no hardware prediction or hardware validation.** The objective is sustained shaft output greater than all net external input over a repeatable full cycle. The results below compare externally powered commands at imposed speed. They establish no self-running or generator capability, self-starting, stable loaded rotation, or thermal/mechanical reliability.

**This is not an optimization or evaluation of the user's magnetic geometry.** The sinusoidal magnetic map and its amplitudes are assumed accounting examples. This grid provides no evidence about the real machine's output and cannot determine actual rated power or sustained net-power capability. It cannot assess the historical 350 W figure.

The configured grid contains **1,560 commands**: 3 speeds × 8 peak currents × 13 phase centers × 5 widths. **442 pass** the reference constraints; **1,118 are rejected**. No feasible command has positive shaft-minus-source power (0 cases). This energy-consistent model has no unaccounted external energy source. Its outcome is a consequence of its stated constitutive equations, not an experimental discovery or a universal search over hardware.

## Best feasible powered comparisons

Selections use only feasible grid commands at 4,096 intervals per encounter. Every global and per-speed selection is re-evaluated at 32,768 intervals; all selected commands must pass again. The table reports those verified values. Power and efficiency are separate objectives. Numerical ties (relative tolerance 1e-10 or absolute tolerance 1e-12) select lower net source input, then case ID.

| Selection | Speed (rpm) | Peak current (A) | Center / width (phase °) | Shaft power (W) | Net source input (W) | Source − shaft deficit (W) | Efficiency |
|---|---:|---:|---:|---:|---:|---:|---:|
| Maximum shaft power | 1000 | 0.15 | 90 / 36 | 0.998843 | 2.00349 | 1.00465 | 49.855% |
| Maximum shaft efficiency | 1000 | 0.1 | 90 / 36 | 0.665895 | 1.2513 | 0.5854 | 53.216% |

A positive deficit means the external source supplies more power than the shaft delivers. Net source input includes gross electrical draw, actual recovered bus energy and controller consumption. Mechanical drag and forward bridge losses are optimistically zero in this reference, so the deficit understates an equivalent real system's losses.

| Speed (rpm) | Sampled | Feasible | Best verified shaft power (W) | Best verified efficiency |
|---|---:|---:|---:|---:|
| 500 | 520 | 286 | 0.998843 | 36.255% |
| 1000 | 520 | 156 | 0.998843 | 53.216% |
| 3500 | 520 | 0 | — | — |

Feasibility uses a conservative analytical upper bound on required absolute terminal voltage over the entire encounter, including back EMF outside the pulse. Some rejected commands could pass a tighter voltage analysis; a conservative rejection is not proof of physical impossibility. The driver must support both voltage polarities and a receptive regenerative bus. Current cap, gate duty, release-only phase, cancellation cap, pulse resolution and energy closure are also checked. Rejection counts can overlap: `voltage_limit`: 1118.

## Full-cycle energy account

For each complete repeating cycle the model enforces:

```text
E_source = E_draw − eta_return × E_returned_terminal + E_controller
E_source − W_shaft = E_copper + E_unrecovered_return + E_controller
                   + E_mechanical_loss + ΔE_stored
```

`E_returned_terminal` integrates only negative terminal power. Recoverable inductive energy is not assumed to equal all peak coil storage, and recovery is not subtracted twice from signed terminal energy. The passive PM potential and coil current return to their starting states, so stored energy does not supply repeated net work. Electrical release reduces the braking part of this chosen potential profile; the added cycle work is paid for through the electrical port.

The energy/coenergy framework is supported by [1]; the parameter values and waveform are the stated reference assumptions.

| Numerical audit across all grid commands | Value |
|---|---:|
| Maximum absolute cycle balance residual | 3.33419e-09 J/rev |
| Maximum relative cycle residual | 5.37329e-08 |
| Maximum instantaneous residual per coil | 2.84217e-14 W |
| Maximum absolute stored-energy change | 0 J/rev |
| Maximum absolute passive work per coil encounter | 0 J |
| Smallest source-minus-shaft deficit among feasible commands | 0.26677 W |

The 4 distinct selected commands remain feasible at the finer resolution. Maximum changes are 8.79749e-09 W shaft power and 8.79733e-09 W source input. This checks numerical integration of the assumed model, not agreement with hardware.

## Assumptions and limits

- **Magnetic map:** `U_pm = −0.002 cos(phase)` J per coil and `psi_pm = 0.005 cos(phase)` Wb-turn, with `phase = 16 × mechanical_angle`. Both amplitudes and the sinusoidal profiles are illustrative, not extracted from FEMM, holding force or measurements. The chosen ratio gives 0.4 A instantaneous cancellation; overcancellation is prohibited.
- **Coils and repetition:** 16 coils, 16 encounters per coil per revolution, 256 total coil encounters per revolution. This is the supplied double-face arrangement, not a 2:1 pulse-count shortcut. Summed cycle energy does not establish the actual instantaneous torque ripple or magnetic coupling.
- **Electrical parameters:** constant 5 mH inductance is an unmeasured assumption. The 55.9 Ω nominal resistance, 24 V, 0.43 A and 10% intermittent-duty figures come from APW actuator metadata [2], used only to define a reference scenario. They are not validated rotating-machine parameters, a certified peak pulse limit or a high-frequency operating envelope.
- **Losses and recovery:** 75% of actually returned terminal energy is assumed to reach the bus; controller draw is 0.25 W total. Return efficiency and controller draw are assumptions. Ideal forward conversion, zero switching/conduction losses, zero mechanical drag and no reserved voltage margin are optimistic. No demagnetization, saturation, hysteresis, eddy-current, heat-transfer or bus-storage model is supplied.
- **Thermal duty:** the copper-loss integral includes all modeled coil current over the entire encounter. Actual hold, freewheel, decay and release currents all contribute to `i²R`; the PWM switching fraction alone is not a thermal duty estimate. A published 10% intermittent actuator rating cannot certify continuous motor operation. The configured 80 °C sensitivity metadata is not executed here and is not an allowable winding temperature or an established equilibrium.
- **Evidence needed for a hardware result:** measured or validated current-dependent flux linkage, torque and inductance across the full angle cycle; complete source/return and controller energy measurements; actual thermal duty and losses; and a loaded dynamic test that returns all energy stores to the same state. Permanent holding without input [3] is not an energy source for repeatable net shaft work.

## Reproduce and inspect

```sh
python simulations/run_release_motor_study.py
```

Configuration: `configs/release_motor_reference.json`. All 1,560 sampled commands, including rejected ones and their reasons, are recorded in `data/release_motor_study.csv`; only feasible commands are selected. The full verified selected cases, energy balances, configuration provenance and source-file hashes are in `reports/release_motor_study.json`. The runner is deterministic and uses NumPy plus the repository's analytic model; it performs no fitting or external data download.

## Sources and provenance

Published sources support only the theory or metadata described below; none validates the illustrative magnetic amplitudes or this motor's output.

1. [MIT 6.061, Chapter 8: Electromagnetic forces and loss mechanisms](https://ocw.mit.edu/courses/6-061-introduction-to-electric-power-systems-spring-2011/c26f6204e05bd4c47875a96452982b6f_MIT6_061S11_ch8.pdf) — Energy/coenergy treatment of force, torque, electrical and mechanical energy ports.
2. [APW EML50mm-24 drawing 6681](https://apwcompany.com/cdn/shop/files/6681.pdf?v=16184353028769850943) — 24 VDC, 0.43 A, 55.9 ohm +/-10% at 20 C, 10.3 W energized and 10% intermittent duty.
3. [APW permanent electromagnets](https://apwcompany.com/collections/permanent-electromagnets) — Permanent holding without electrical power; applying electrical power releases. This does not establish a zero-power latched release state.
