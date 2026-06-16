# Pulse Management Plan

Date: 2026-06-15

## Current Control Candidate

Source: `data/field_sim/femm_opt_opt_stator_inner_gap_plus1mm_period45_step1.csv`

This is the current best first-screen candidate:

- ASYM_B rotor geometry
- EML offset +12 degrees
- stator inner radius +1 mm
- 1.486 J/rev first-screen equivalent
- not mesh-converged

## Strategy

Use selective phased assist:

- pulse only inside positive torque windows,
- keep coils off inside lockout windows,
- apply a small phase advance to account for switching delay,
- regenerate windows after every geometry or offset change.

Generated files:

- `field_sim/femm/pulse_strategy.best_candidate.json`
- `reports/best_candidate_pulse_strategy.md`

## Current Assist Windows

For the best committed candidate, the 45 degree assist windows are:

- 0 to 2 degrees
- 14 to 25 degrees
- 37 to 45 degrees

The generated 360 degree schedule wraps the boundary window cleanly instead of using negative angles.

## Energy Accounting

The default placeholder budget assumes:

- 5 mH coil inductance
- 2 A pulse current
- 75 percent flyback recovery
- 64 pulse opportunities per revolution

That gives:

- stored energy per pulse: 0.010 J
- unrecovered input per pulse: 0.0025 J
- unrecovered pulse input: 0.160 J/rev

These are placeholders. Replace with measured or simulated coil values before making input/output claims.

## Next FEMM Work

For the best geometry candidate only:

1. Run coil-off baseline over the assist windows.
2. Run coil-on cases at small current densities.
3. Compare added mechanical work to added electrical input.
4. Reject any pulse strategy that only improves torque by injecting more energy than it returns mechanically.
5. Do not pulse in lockout windows unless energized FEMM shows a local torque sign reversal.

## Promotion Rule

Pulse assist is not a substitute for mesh convergence. A geometry/control candidate still needs medium/fine/very-fine mesh stability before build confidence improves.
