# PM Gradient Motor Lab

Investigation of a permanent-magnet gradient machine with timed cancellation
of trailing attraction. The user's objective is sustained useful net power
and long operating life.

**Current result: net generation is not demonstrated.** A permanent-magnet-only
machine cannot provide sustained net energy while returning to the same state
each cycle. The repository now distinguishes numerical residuals, illustrative
models, powered comparison designs, and measured performance. There is no
validated working generator or released manufacturing design.

Start with the [net-power feasibility assessment](reports/net_power_feasibility.md).

The user has flagged the older AI-produced simulations as potentially flawed.
They are unvalidated historical calculations, not evidence that the physical
design succeeds or fails. The [fresh model specification](hardware/fresh_model_specification.md)
preserves the actual release mechanism and lists the geometry and magnetic data
needed for a faithful new assessment.

## Contents

- `simulations/`: Python models and audit scripts.
- `validation/`: Reusable validation math and benchmark runners.
- `data/`: Generated CSV outputs, measurement templates, and published benchmark data.
- `hardware/`: Test jig, sensor, and wiring notes for real bench validation.
- `reports/`: Markdown summaries generated from the audit scripts.
- `tests/`: Regression tests for the validation pipeline.

## Current assessment and engineering work

- [Passive-cycle audit](reports/passive_cycle_audit.md): re-integrates eight
  historical files, rejects an incomplete angular sweep, and treats passive
  full-cycle work as a residual requiring explanation. Mesh-labelled results
  change sign; they are not validated power output.
- [Release model](simulations/release_motor_model.py): uses common magnetic
  functions for torque and electrical coupling. Its maps are illustrative,
  not calibrated to the physical design. It includes voltage/current/duty
  constraints, copper loss, controller power and returned energy counted once.
  Its [accounting study](reports/release_motor_study.md) tests the declared
  analytic assumptions; its wattages are not estimates of the user's design.
- [Promotion criteria](reports/variant_promotion_gates.md): complete-state
  accounting and demonstrated performance replace rewards for apparent
  energy gain or positive passive bias.
- [Design basis](hardware/design_basis.md): preserves the net-power objective
  and identifies the unresolved energy-source and geometry requirements.
- [Driver requirements](hardware/release_driver_requirements.md): supersede
  contradictory circuit instructions and blocking pulse firmware; specify a
  characterized current-controlled fixture and a defined discharge path.
- [Reliability reference](hardware/reliability_design.md): temperature,
  bearings, magnets, electronics and qualification requirements. Its 48 V,
  350 W powered-motor option is a comparison only and does not meet the user's
  net-generation goal. All ratings and lifetime numbers are targets, not results.

Earlier reports, sweeps and prototypes remain as historical material. An old
ranking or estimated amplification figure must not be treated as validated
performance. No new FEMM solve or physical experiment was performed for this
assessment.

## Reproduce the current checks

The reduced model requires NumPy; the audit and unit-test runner use Python.

```bash
python validation/passive_cycle_audit.py
python validation/analyze_pulse_assist_comparison.py
python validation/account_selective_pulse_energy.py
python simulations/run_release_motor_study.py
python -m unittest discover -s tests
```

The study reports calculated behavior of declared analytic maps. It cannot
determine a real motor's winding, rating, efficiency or service life without
characterization data.

## Suggested Next Data

- Torque vs angle across a full revolution.
- Coil voltage and current waveforms for every pulse.
- Rotor speed before and after pulses.
- Load torque and bearing/friction calibration.
- Thermal measurements for coil, driver, magnets, bearings, and load.

## Existing validation workflows

The project now has a three-layer validation path:

1. Compare against a real published PMSM benchmark.
2. Import field-simulation torque-angle curves.
3. Import real bench measurements and audit energy balance.

The published benchmark is the 2010 Toyota Prius MG2 permanent-magnet
synchronous motor from Oak Ridge National Laboratory report ORNL/TM-2010/253.
It exercises the reporting pipeline against a real motor. Passing that check
does not validate the custom rotor, release mechanism, or net-power claim.

Run the benchmark check:

```bash
python validation/run_prius_benchmark.py
```

Run the current motor decision check:

```bash
python validation/current_motor_decision.py
```

Generate the FEMM torque-angle workflow:

```bash
python validation/femm_geometry_builder.py
python validation/femm_workflow.py
```

Run tests:

```bash
python -m unittest discover -s tests
```

Key validation files:

- `reports/validation_protocol.md`
- `reports/prius_benchmark_validation_report.md`
- `reports/current_motor_decision_report.md`
- `field_sim/femm/README.md`
- `field_sim/femm/build_pm_gradient_motor.lua`
- `field_sim/femm/sweep_torque_angle.lua`
- `field_sim/femm/config.example.json`
- `geometry/pm_gradient_motor_config.json`
- `data/published/ornl_2010_prius_mg2_reference.csv`
- `data/torque_angle/torque_angle_measurement_template.csv`
- `data/field_sim/field_simulation_torque_angle_template.csv`
- `data/bench/raw/bench_run_template.csv`
- `SOURCES.md`
