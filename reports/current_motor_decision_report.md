# Current Motor Decision Report

This report uses the current PM-gradient motor assumptions already in
the repository. It does not include new bench measurements.

Baseline assumptions:

- 800 RPM
- 12 magnetic gradients per revolution
- 1 interaction channel
- 17.5 mJ net electrical input per pulse
- 0.8 Nm load/friction torque
- 1.8 Nm pulse-assist torque assumption

| Pulse window (deg) | Work/pulse (J) | Pulse balance ratio | Electrical input power (W) | Mechanical pulse power (W) | Load power (W) | Minimum extra energy/rev (J) | Status |
|---:|---:|---:|---:|---:|---:|---:|---|
| 2.0 | 0.062832 | 3.590 | 2.800000 | 10.053096 | 67.020643 | 4.816548 | UNBALANCED_PENDING_SOURCE_IDENTIFICATION |
| 4.0 | 0.125664 | 7.181 | 2.800000 | 20.106193 | 67.020643 | 4.816548 | UNBALANCED_PENDING_SOURCE_IDENTIFICATION |
| 8.0 | 0.251327 | 14.362 | 2.800000 | 40.212386 | 67.020643 | 4.816548 | UNBALANCED_PENDING_SOURCE_IDENTIFICATION |
| 12.0 | 0.376991 | 21.542 | 2.800000 | 60.318579 | 67.020643 | 4.816548 | UNBALANCED_PENDING_SOURCE_IDENTIFICATION |
| 20.0 | 0.628319 | 35.904 | 2.800000 | 100.530965 | 67.020643 | 7.329822 | UNBALANCED_PENDING_SOURCE_IDENTIFICATION |

Decision:

**The current motor model does not pass the conservative energy audit.**

The smallest tested pulse window, 2 degrees, still needs at least
0.045332 J of additional
identified energy per pulse before the pulse work is closed.

At the stated 0.8 Nm load, the design also needs at least
4.816548 J of additional
identified energy per revolution before load operation is closed.

What would change this result:

- measured torque-angle data showing net positive work over 360 degrees,
- measured electrical waveforms showing higher true input or recovered energy,
- lower load/friction torque,
- lower pulse torque,
- narrower pulse windows,
- more channels only if their energy input and mechanical work are both measured.
