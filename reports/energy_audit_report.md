# One-Channel PM-Gradient Assisted Motor Energy Audit

## Purpose

This validation simulation audits one stationary EML50mm-24 interaction channel over one full rotor revolution. It does **not** assume permanent magnets provide free continuous net torque. Any case where modeled mechanical pulse work exceeds the measured net electrical pulse input is flagged as **unbalanced pending source identification**.

## Model Inputs

- Rotor diameter: 300.0 mm
- Rotor radius: 150.0 mm
- Magnetic gradients per revolution: 12
- Stationary interaction channels: 1
- Target speed: 800.0 RPM
- Timing advance: 8.0 degrees
- Pulse assist torque assumption: 1.800 Nm
- Pulse windows tested: 2°, 4°, 8°, 12°, 20°
- Net electrical energy per pulse: 0.017500 J (17.5 mJ)
- Flyback recovery: 51.5%
- Friction/load torque: 0.800 Nm

## Equations

1. Angular speed: `omega = RPM * 2*pi / 60`
2. Gradient event frequency: `f_gradient = gradients_per_revolution * RPM / 60`
3. Pulse events per second, one channel: `f_pulse = f_gradient * channels`
4. Pulse window radians: `theta = pulse_window_deg * pi / 180`
5. Work per pulse: `W_pulse = torque * theta`
6. Mechanical pulse power: `P_mech_pulse = W_pulse * f_pulse`
7. Electrical input power: `P_elec = net_electrical_energy_per_pulse * f_pulse`
8. Energy balance ratio: `ratio = W_pulse / net_electrical_energy_per_pulse`
9. Required electrical pulse energy for 100% balance: `E_required_100pct = W_pulse`
10. Load energy per revolution: `E_load_rev = load_torque * 2*pi`

## Baseline Results

- Angular speed: **83.775804 rad/s**
- Gradient event frequency: **160.000000 Hz**
- Pulse events per second: **160.000000 pulses/s**
- Net electrical input power: **2.800000 W**
- Gross pulse energy before 51.5% flyback recovery, inferred from the stated net value: **0.036082 J/pulse**
- Recovered flyback energy, inferred: **0.018582 J/pulse**
- Friction/load power at target speed: **67.020643 W**
- Friction/load energy per revolution: **5.026548 J/rev**
- Net electrical pulse energy per revolution: **0.210000 J/rev**

## Numerical Results Table

| Pulse window (deg) | Work/pulse (J) | Mechanical pulse power (W) | Electrical input power (W) | Energy balance ratio | Required electrical energy/pulse for 100% (J) | Per-rev pulse mechanical energy (J) | Status |
|---:|---:|---:|---:|---:|---:|---:|---|
| 2.0 | 0.062832 | 10.053096 | 2.800000 | 3.590 | 0.062832 | 0.753982 | unbalanced pending source identification |
| 4.0 | 0.125664 | 20.106193 | 2.800000 | 7.181 | 0.125664 | 1.507964 | unbalanced pending source identification |
| 8.0 | 0.251327 | 40.212386 | 2.800000 | 14.362 | 0.251327 | 3.015929 | unbalanced pending source identification |
| 12.0 | 0.376991 | 60.318579 | 2.800000 | 21.542 | 0.376991 | 4.523893 | unbalanced pending source identification |
| 20.0 | 0.628319 | 100.530965 | 2.800000 | 35.904 | 0.628319 | 7.539822 | unbalanced pending source identification |

## Energy-Balance Decision

All tested pulse windows produce mechanical pulse work greater than the stated net electrical pulse input of 0.017500 J. Under this audit rule, none of the tested pulse windows can be called energy-balanced unless an additional measured source of energy is added to the model.

## Physical Interpretation

The pulse torque assumption creates mechanical work equal to torque integrated over angle. For the smallest tested pulse window, 2°, the modeled work is already above the stated net electrical input per pulse. Wider pulse windows increase the imbalance linearly because the torque assumption is held constant while the energized angular interval grows.

A permanent-magnet gradient can redistribute stored magnetic field energy and can exchange energy with the rotor and coil, but this simulation does not include a measured source capable of supplying the excess continuous net work. Therefore, any apparent output above electrical input is not treated as success; it is classified as **unbalanced pending source identification**.

The friction/load requirement is also significant: 0.800 Nm at 800.0 RPM corresponds to 67.020643 W. The stated net pulse electrical input is only 2.800000 W, so sustaining the specified load at speed requires either substantially more electrical energy, a verified external/mechanical energy source, or a corrected torque/window assumption.

## Next Data Needed From Prototype

- Direct torque-vs-angle measurements through each gradient, including attraction and exit/drag regions.
- Coil voltage and current waveforms at high sample rate for every pulse, including flyback path measurements.
- Rotor speed before and after each pulse to derive kinetic-energy change independently.
- Load torque calibration and bearing/friction characterization across speed.
- Magnetic force mapping over a full 360° revolution to prove that positive and negative gradient regions are balanced or to identify a real stored-energy source.
- Thermal measurements of coil, driver, magnets, bearings, and load to close the energy budget.
- Repeatability data across many revolutions to distinguish transient stored-energy release from continuous operation.

## Output Files

- `simulation_results.csv`
- `energy_audit_report.md`
- `torque_energy_audit.py`
