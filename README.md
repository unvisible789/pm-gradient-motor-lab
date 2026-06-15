# PM Gradient Motor Lab

Standalone project for the PM-gradient assisted motor concept, energy audits,
parameter sweeps, and validation scaffolds.

## Contents

- `simulations/`: Python models and audit scripts.
- `validation/`: Reusable validation math and benchmark runners.
- `data/`: Generated CSV outputs, measurement templates, and published benchmark data.
- `hardware/`: Test jig, sensor, and wiring notes for real bench validation.
- `reports/`: Markdown summaries generated from the audit scripts.
- `tests/`: Regression tests for the validation pipeline.

## Current Status

The latest audit direction is conservative. The project does not treat
permanent magnet gradient torque as continuous free shaft torque. Any claimed
mechanical work must be supported by measured torque-angle data, field
simulation, or bench test results.

Known findings:

- The early optimized model is optimistic and assumes continuous PM torque.
- The later validation models require measured PM torque-angle data.
- The v2 and v3 validation scripts flag invalid pulse overlap for their current
  default configuration.
- The `master-repository` sweep contains 12,000 cases, with 810 balanced and
  11,190 unbalanced under the 17.5 mJ per-pulse input rule.

## Suggested Next Data

- Torque vs angle across a full revolution.
- Coil voltage and current waveforms for every pulse.
- Rotor speed before and after pulses.
- Load torque and bearing/friction calibration.
- Thermal measurements for coil, driver, magnets, bearings, and load.

## Validation Workflow

The project now has a three-layer validation path:

1. Compare against a real published PMSM benchmark.
2. Import field-simulation torque-angle curves.
3. Import real bench measurements and audit energy balance.

The selected published benchmark is the 2010 Toyota Prius MG2 permanent-magnet
synchronous motor from Oak Ridge National Laboratory report ORNL/TM-2010/253.
It is similar enough to be useful because it is a real traction PMSM with
published teardown, test-cell, efficiency, torque, speed, and thermal results.

Run the benchmark check:

```bash
python validation/run_prius_benchmark.py
```

Run the current motor decision check:

```bash
python validation/current_motor_decision.py
```

Run tests:

```bash
python -m unittest discover -s tests
```

Key validation files:

- `reports/validation_protocol.md`
- `reports/prius_benchmark_validation_report.md`
- `reports/current_motor_decision_report.md`
- `data/published/ornl_2010_prius_mg2_reference.csv`
- `data/torque_angle/torque_angle_measurement_template.csv`
- `data/field_sim/field_simulation_torque_angle_template.csv`
- `data/bench/raw/bench_run_template.csv`
- `SOURCES.md`
