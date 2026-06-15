# FEMM Actual Solve Summary

Run date: 2026-06-15

This run used FEMM 4.2 with the generated `geometry/pm_gradient_motor_base.fem` model and a 0-360 degree rotor sweep in 2 degree increments.

## Model

- Geometry type: 2D radial-flux approximation of the PM-gradient assisted motor
- Rotor diameter: 300 mm
- Rotor gradients: 16 NdFeB 40 MGOe magnet regions
- Stator/EML units: 8 steel stator regions with copper coil regions
- Active coil current: 0 A/mm^2 for this run
- Rotor group: 2
- Sweep points: 181

## Results

- Torque CSV: `data/field_sim/femm_torque_angle.csv`
- Integrated work per revolution: 0.921199 J/rev
- Average torque over revolution: 0.146613 Nm
- Peak torque: 18.124221 Nm at 186 degrees
- Minimum torque: -17.814651 Nm at 264 degrees
- First/last torque closure: 0.168210 Nm at 0 degrees, 0.162932 Nm at 360 degrees

## Convergence Checks

Additional FEMM sweeps were run to test whether the positive work result survives different sampling and symmetry checks.

| Sweep | Span | Step | Points | Integrated work | Full-rev equivalent | Average torque |
|---|---:|---:|---:|---:|---:|---:|
| `femm_torque_angle_step4.csv` | 360 deg | 4 deg | 91 | 0.953742 J | 0.953742 J/rev | 0.151793 Nm |
| `femm_torque_angle.csv` | 360 deg | 2 deg | 181 | 0.921199 J | 0.921199 J/rev | 0.146613 Nm |
| `femm_torque_angle_period45_step1.csv` | 45 deg | 1 deg | 46 | 0.112866 J | 0.902928 J/rev | 0.143705 Nm |
| `femm_torque_angle_period45_step0p5.csv` | 45 deg | 0.5 deg | 91 | 0.119591 J | 0.956725 J/rev | 0.152268 Nm |

The positive result stays in the rough range of 0.90-0.96 J/rev across these checks. That means the result is repeatable in this simplified FEMM setup, but it is still small relative to the torque ripple of about +/-18 Nm and must not be treated as a build-proven result.

## Interpretation

The simplified FEMM run produced a small positive closed-cycle work value. That is not yet proof of excess energy or a buildable motor effect. At this stage it should be treated as a source-accounting and numerical-model finding that needs harder validation.

Important limitations:

- This is a 2D radial approximation, not a true axial-flux/double-sided 3D solve.
- The EML boost coils were not energized in this run.
- The geometry is a first-pass generated model, not a CAD-imported manufacturable design.
- The 0/360 degree torque closure is close but not exact, so mesh motion/numerical error must be quantified.
- Mesh-refinement and true 3D axial-flux modeling are still required before a build decision.

## Build Decision

Do not build a full motor from this result yet.

The current result is strong enough to justify more simulation and possibly a low-cost single-period bench fixture, but not a full rotating prototype. Before building the full motor, the project needs:

- a mesh-refinement study proving the 0.90-0.96 J/rev signal is not a mesh/rotation artifact;
- a true axial-flux or double-sided 3D model, or a defensible equivalent magnetic-circuit reduction;
- energized EML pulse cases with electrical input and flyback recovery accounted for;
- a torque-angle bench fixture plan that can measure one 45 degree repeat period directly.
