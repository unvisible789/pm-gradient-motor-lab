# Sensor Plan

Recommended minimum sensors:

- Torque: calibrated rotary torque transducer or torque arm with load cell.
- Angle/speed: optical encoder, hall encoder, or high-resolution tachometer.
- Electrical input: differential voltage probe and current probe/shunt.
- Recovery path: separate voltage/current measurement on flyback/recovery branch.
- Temperature: coil, driver, magnets, bearing, and ambient.

Sampling:

- Torque-angle static mapping: one averaged reading per angle sample.
- Pulse waveform capture: at least 10x faster than the pulse rise/fall event.
- Continuous bench runs: enough rate to resolve rpm ripple and thermal drift.

Calibration:

- Torque sensor zero and span check before every session.
- Current probe/shunt calibration against a known load.
- Voltage probe ratio check.
- Temperature sensor sanity check at ambient and one warm reference point.
