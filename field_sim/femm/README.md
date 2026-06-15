# FEMM Torque-Angle Workflow

This workflow is the pre-build electromagnetic simulation path for the motor
idea.

## Goal

Run a finite-element magnetic torque sweep:

`0-360 degrees -> torque(theta) -> integrate torque over angle -> net work/rev`

If the integrated cycle does not close, the result must be traced to a modeled
source term such as magnet field energy change, coil input, motion of an
external part, demagnetization, or another measured state change.

## FEMM Setup

1. Generate the parametric Lua files:

   ```bash
   python validation/femm_geometry_builder.py
   python validation/femm_workflow.py
   ```

2. In FEMM, run `build_pm_gradient_motor.lua`.
   This creates a first-pass radial-flux 2D approximation of the described
   motor and saves it as `geometry/pm_gradient_motor_base.fem`.
3. Inspect the generated model carefully:
   - 300 mm rotor diameter.
   - 16 alternating rotor gradient magnets.
   - 8 fixed EML stator units.
   - rotor assigned to group `2`.
   - fixed EML/stator geometry outside group `2`.
4. Adjust geometry, materials, magnetization directions, air gaps, and coil
   definitions as needed.
5. Run `sweep_torque_angle.lua` inside FEMM.

The generated Lua script uses FEMM's weighted stress tensor torque integral:

`mo_blockintegral(22)`

The output is:

`data/field_sim/femm_torque_angle.csv`

## Validate The Result

After FEMM exports the CSV, integrate it with the project validation tools:

```bash
python -m unittest discover -s tests
```

or from Python:

```python
from validation.femm_workflow import summarize_torque_angle_csv

summary = summarize_torque_angle_csv("data/field_sim/femm_torque_angle.csv")
print(summary)
```

## Interpretation Rule

This project treats the magnetic field as the candidate energy source being
tested. The pass/fail question is not whether the field is ignored; it is
whether the full modeled field state produces net work over a complete cycle
after all inputs and state changes are accounted for.

If the net integrated work is positive, the next task is to identify what
changed in the field/material/electrical system and whether that change can
repeat continuously.

## Current Approximation Limits

The builder creates a 2D radial-flux approximation because standard FEMM
magnetics is 2D. The physical concept can be axial/disc shaped and double
sided, but those details need either:

- a carefully equivalent 2D FEMM approximation,
- two mirrored FEMM models for the double-sided case,
- or a 3D solver such as Ansys Maxwell, COMSOL, JMAG, or Motor-CAD.

The generated model is a starting geometry, not final proof.
