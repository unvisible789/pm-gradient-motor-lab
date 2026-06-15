# Geometry

Place FEMM geometry files here.

Expected first model:

`pm_gradient_motor_base.fem`

Requirements for the generated FEMM torque sweep:

- The full rotating assembly is assigned to FEMM group `2`.
- The rotation center is `(0, 0)` unless changed in
  `field_sim/femm/config.example.json`.
- Stator, fixed coils, boundaries, and fixed fixtures are not in group `2`.
- Materials and magnetization directions are fully assigned before sweeping.
