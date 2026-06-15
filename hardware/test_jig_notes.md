# Torque-Angle Test Jig Notes

Purpose: measure real torque versus rotor angle over a full revolution.

Minimum setup:

- Rigid rotor fixture with indexed angle marks or encoder feedback.
- Torque arm or rotary torque sensor mounted so the rotor can be held at known angles.
- Angle increments of 1 to 5 degrees for first-pass mapping.
- Separate clockwise and counterclockwise sweeps to expose hysteresis and drag.
- Multiple repeats at each angle.

Procedure:

1. Zero the torque sensor with the rotor installed.
2. Record torque at each angle from 0 to 360 degrees.
3. Repeat in the opposite direction.
4. Save the result using `data/torque_angle/torque_angle_measurement_template.csv`.
5. Integrate with `validation.integrate_torque_angle`.

Pass condition:

The integrated torque-angle work must close over 360 degrees unless a measured
external energy source is identified.
