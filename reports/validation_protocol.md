# Validation Protocol

This project validates motor claims in three layers.

## 1. Published Benchmark Layer

Use a real published permanent-magnet motor benchmark to prove the analysis
tools can reproduce known motor-envelope numbers. The selected baseline is the
2010 Toyota Prius MG2 PMSM benchmark from Oak Ridge National Laboratory.

Tracked published checks:

- 60 kW tested 18-second power rating.
- 205 Nm torque rating.
- 13,500 rpm speed rating.
- 36.7 kg motor mass.
- 12.5 L motor volume.
- 650 Vdc maximum dc link.

## 2. Field-Simulation Layer

Field simulation must export torque versus angle in the same shape as measured
bench data:

`angle_deg, torque_nm`

The project can compare field-simulated torque against bench-measured torque at
matching angle samples. Field simulation is treated as a hypothesis until bench
measurements agree within a stated tolerance.

## 3. Bench Layer

Bench runs must capture:

- voltage and current at the driver input
- voltage and current in the recovery path
- torque
- rpm
- temperature
- pulse timing

The audit integrates electrical and mechanical power over time and flags any
mechanical output above measured input as
`UNBALANCED_PENDING_SOURCE_IDENTIFICATION`.

## Acceptance Rule

A claim is only considered supported when:

1. torque-angle work is measured or field-simulated and then bench-confirmed,
2. electrical energy is measured at waveform level,
3. mechanical output does not exceed accounted input plus identified sources,
4. thermal/loss behavior is consistent across repeated runs.
