# PM Gradient Motor Lab

Standalone project for the PM-gradient assisted motor concept, energy audits,
parameter sweeps, and validation scaffolds.

## Contents

- `simulations/`: Python models and audit scripts.
- `data/`: Generated CSV outputs from the baseline audit and sweep.
- `reports/`: Markdown summaries generated from the audit scripts.

## Current Status

The latest audit direction is conservative. The project does not treat
permanent magnet gradient torque as continuous free shaft torque. Any claimed
mechanical work must be supported by measured torque-angle data, field
simulation, or bench test results.

Known findings:

- The early optimized model is optimistic and assumes continuous PM torque.
- The later validation models require measured PM torque-angle data.
- The v2 and v3 validation scripts flag invalid pulse overlap for their current
  default configuration.
- The `master-repository` sweep contains 12,000 cases, with 810 balanced and
  11,190 unbalanced under the 17.5 mJ per-pulse input rule.

## Suggested Next Data

- Torque vs angle across a full revolution.
- Coil voltage and current waveforms for every pulse.
- Rotor speed before and after pulses.
- Load torque and bearing/friction calibration.
- Thermal measurements for coil, driver, magnets, bearings, and load.
