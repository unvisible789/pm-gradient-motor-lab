# Pulse Strategy: ASYM_B_plus12_stator_gap_plus1mm

First-screen control scaffold only. This is not a performance claim.

## Source

- CSV: `data/field_sim/femm_opt_opt_stator_inner_gap_plus1mm_period45_step1.csv`
- Strategy: `selective_phased_assist`
- Phase advance: 1.00 deg

## Assist Windows Per 45 Deg

- 0.00 to 2.00 deg
- 14.00 to 25.00 deg
- 37.00 to 45.00 deg

## Electrical Budget Placeholder

| Metric | Value |
|---|---:|
| Mechanical work | 1.485508 J/rev |
| Stored energy per pulse | 0.010000 J |
| Unrecovered energy per pulse | 0.002500 J |
| Pulse count per rev | 64.000 |
| Unrecovered pulse input | 0.160000 J/rev |
| Mechanical minus unrecovered input | 1.325508 J/rev |

## Control Rules

- Pulse only inside assist windows.
- Do not pulse in lockout windows unless energized FEMM shows a local sign reversal.
- Account for coil input, copper loss, switching loss, and imperfect flyback recovery.
- Regenerate this schedule after each geometry or EML offset change.

## Next Validation

Run energized FEMM for coil-on vs coil-off inside the scheduled windows, then compare added mechanical work against measured or simulated electrical input.
