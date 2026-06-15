# Priority 1 Screening Results

Date: 2026-06-15

Purpose: start the GitHub Priority 1 improvement plan by screening rotor flux-barrier and asymmetric/partial-Halbach variants. These are coarse 45 degree repeat-period screens at 5 degree angular spacing. They are not performance claims and are not accepted results.

## Screening Outcome

| Variant | FEMM status | 45 deg work | Full-rev equivalent | Peak positive | Peak negative | Decision |
|---|---|---:|---:|---:|---:|---|
| `p1_barrier_5deg_core` | solved | -0.032039 J | -0.256309 J/rev | 5.489 Nm | -5.515 Nm | reject for now |
| `p1_barrier_8deg_core` | solved | -0.020594 J | -0.164750 J/rev | 5.471 Nm | -5.543 Nm | reject for now |
| `p1_barrier_plus_halbach` | solved | -0.043130 J | -0.345042 J/rev | 6.587 Nm | -8.256 Nm | reject for now |
| `p1_partial_halbach_15deg` | solved | -0.029802 J | -0.238413 J/rev | 6.484 Nm | -8.300 Nm | reject for now |
| `p1_forward_biased_cap` | failed | n/a | n/a | n/a | n/a | fix geometry before retest |

## Interpretation

The first substantial rotor-core barrier and partial-Halbach variants did not improve net work in the coarse screen. They reduce or reshape torque in places but remain net negative over the 45 degree period.

The forward-biased outer pole cap still creates at least one FEMM region without material assignment, so it needs a more robust CAD-style construction before it can be tested.

## Next Improvement Direction

Do not claim improvement from this screen. The next useful design iteration should focus on:

- fixing the forward-biased cap geometry so FEMM can solve it;
- trying asymmetric magnet placement without creating separate outer cap regions;
- sweeping EML angular position with the mesh-converged near-zero baseline;
- keeping mesh convergence as the acceptance gate for any positive result.
