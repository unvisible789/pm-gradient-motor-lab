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

1. Create or import the motor geometry in FEMM.
2. Save the base model as `geometry/pm_gradient_motor_base.fem`.
3. Assign the complete rotating assembly to group `2`.
4. Keep the stator, coils, and boundary geometry out of group `2`.
5. Confirm the rotation center is `(0, 0)` or edit `config.example.json`.
6. Run `sweep_torque_angle.lua` inside FEMM.

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
