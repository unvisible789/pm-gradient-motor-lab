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

## Interpretation

The simplified FEMM run produced a small positive closed-cycle work value. That is not yet proof of excess energy or a buildable motor effect. At this stage it should be treated as a source-accounting and numerical-model finding that needs harder validation.

Important limitations:

- This is a 2D radial approximation, not a true axial-flux/double-sided 3D solve.
- The EML boost coils were not energized in this run.
- The geometry is a first-pass generated model, not a CAD-imported manufacturable design.
- The 0/360 degree torque closure is close but not exact, so mesh motion/numerical error must be quantified.
- The next validation step is a mesh-refinement sweep and a symmetry-period sweep to see whether the 0.921 J/rev survives numerical convergence.
