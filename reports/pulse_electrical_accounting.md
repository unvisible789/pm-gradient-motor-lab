# Pulse Electrical Accounting

**Status: insufficient data.**

Actual total input, shaft output per revolution, efficiency, net output and energy-balance closure are unknown.
The existing data are magnetostatic sector sweeps, without measured electrical waveforms or a verified repeated operating cycle.

## Winding Excitation

Homogenized current density multiplied by winding-region area gives ampere-turns. Both CSV current headers (`coil_current_a` and `femm_single_turn_current_a`) denote a one-turn FEMM surrogate. Neither establishes physical wire current.
A physical turn count gives nominal current as ampere-turns divided by turns; actual current still requires measurement.

| Level | Density (mA/mm²) | Winding ampere-turns | Nominal wire current (A) |
|---|---:|---:|---:|
| low | 5.0 | 3.669 | unknown |
| medium | 10.0 | 7.338 | unknown |
| high | 20.0 | 14.675 | unknown |

## Available Sector Diagnostics

These values are reported only for complete, ordered, finite 0–45° sweeps. Their numeric precision is not an uncertainty estimate. Full-state periodicity and mesh convergence remain unverified.

| Level | Raw 45° work (J) | Difference from coil-off (J/45°) | Total input | Efficiency | Net output | Energy closure |
|---|---:|---:|---|---|---|---|
| low | 0.180983 | -0.004705 | unknown | unknown | unknown | unknown |
| medium | 0.180779 | -0.004909 | unknown | unknown | unknown | unknown |
| high | 0.191553 | 0.005865 | unknown | unknown | unknown | unknown |

## Required Accounting

For one defined system boundary and the same interval:

`input energy = useful output energy + losses + change in stored energy`

Closure means that the residual of this balance is consistent with zero within measurement uncertainty. Output exceeding input is not the definition of closure.
For example, 100 J input, 80 J useful output, 20 J loss and zero stored-energy change close the balance with 80% efficiency and −20 J output minus input.

The quantity `0.5 L I²` describes magnetic energy storage. Multiplying it by an assumed unrecovered fraction and guessed losses does not establish total electrical input. No placeholder loss or recovery estimate is used here.
Count actual switching events from the controller schedule; an on-angle sample count is neither an event count nor a measured time duty cycle.

Required evidence includes a verified repeated full state, signed bus voltage/current measurements including recovery, all auxiliary and external mechanical inputs, loaded shaft output, losses, and changes in magnetic, electrical, mechanical and thermal energy.
A positive raw sector difference cannot demonstrate sustained net power exceeding all inputs.
