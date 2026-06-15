# Priority 1 Improvement Notes

The GitHub simulation plan now treats the previous positive net-work value as not numerically robust. The next design work is focused on falsifiable rotor changes that can survive mesh convergence.

## Implemented Variant Controls

- `rotor_flux_barrier_arc_deg`
- `rotor_flux_barrier_inner_radius_mm`
- `rotor_flux_barrier_outer_radius_mm`
- `rotor_outer_pole_cap_arc_deg`
- `rotor_outer_pole_cap_offset_deg`
- `rotor_magnet_leading_edge_bias_deg`
- `rotor_halbach_bias_deg`

## First Variant Matrix

Run `python validation/write_priority1_variants.py` to create JSON configs under `field_sim/femm/variants/` and a summary matrix at `field_sim/femm/priority1_variant_matrix.json`.

Initial candidates:

- `p1_barrier_5deg_core`
- `p1_barrier_8deg_core`
- `p1_forward_biased_cap`
- `p1_partial_halbach_15deg`
- `p1_barrier_plus_halbach`

## Required Acceptance Protocol

1. Run 45 degree, 1 degree sweeps first.
2. Reject FEMM geometry failures immediately and document them.
3. For any positive result, run mesh convergence before accepting.
4. Treat non-converged positive values as artifacts until proven otherwise.

## Runner

After FEMM is free, run:

```powershell
python validation\write_priority1_variants.py
powershell -ExecutionPolicy Bypass -File .\validation\run_priority1_matrix.ps1 -StepDeg 1
```

The runner writes raw torque-angle files named `data/field_sim/femm_p1_<variant>_step1.csv`.
