# Prebuild Decision Report

Date: 2026-06-15

## Decision

Do not build the full motor yet. Continue with higher-fidelity simulation and, if hardware is desired, build only a low-cost single-period torque-angle bench fixture.

## Why

The actual FEMM runs show a repeatable small positive work signal in the simplified 2D model:

- 360 degree sweep, 4 degree step: 0.953742 J/rev
- 360 degree sweep, 2 degree step: 0.921199 J/rev
- 45 degree symmetry sweep, 1 degree step, repeated 8x: 0.902928 J/rev
- 45 degree symmetry sweep, 0.5 degree step, repeated 8x: 0.956725 J/rev

This is interesting because the positive value did not disappear when the angle step and symmetry check changed. However, it is not build-proof. The average torque equivalent is only about 0.14-0.15 Nm while instantaneous torque swings are about +/-18 Nm. A small integration bias, mesh-motion artifact, boundary-condition issue, or unmodeled axial/fringing effect could explain the net value.

## What The Current FEMM Model Includes

- 16 rotor magnet/gradient regions
- 8 stator/EML units
- full 360 degree interaction, not a single-magnet test
- summed torque on the complete rotor group
- permanent magnets and passive steel/copper EML geometry

## What It Does Not Yet Prove

- It does not prove a self-running motor.
- It does not prove the double-sided axial-flux version.
- It does not include energized EML coil pulses.
- It does not yet separate useful mechanical work from magnetic-state change, coil input, hysteresis, eddy losses, or demagnetization effects.
- It does not yet have mesh convergence.

## Recommended Next Gate

Before spending money on a full build, pass these gates:

1. Mesh refinement: repeat the 45 degree symmetry sweep with tighter local mesh around magnets, air gaps, and stator teeth.
2. Boundary check: expand the air boundary and verify the full-rev equivalent stays near the same value.
3. 3D/axial check: model the actual disc geometry in a 3D solver, or create a validated axial-flux equivalent.
4. Coil pulse energy: energize the EML coils in FEMM and calculate mechanical work minus electrical pulse energy plus realistic recovery.
5. Bench fixture: measure torque-angle over one 45 degree repeat period before building a full rotor.

Current recommendation: proceed to better simulation and a small measurement fixture, not a full motor.
