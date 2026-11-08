# Specification for a fresh assessment of the proposed magnetic machine

Status: model definition and missing-input record, not a completed simulation or construction release. The user has explicitly cautioned that older AI-produced simulation data may be flawed.

## Preserve the actual proposal

The intended mechanism is magnetic attraction during approach, an opposing field to weaken trailing attraction during escape, and restoration of the magnetic interaction for the next encounter. The goal is sustained useful net power and long operating life. A conventional powered motor does not fulfill that goal and must not be substituted for it in the assessment.

The old CSVs are unvalidated historical calculations. They can expose defects in the old analysis but cannot establish the actual design's performance. The sinusoidal release model added in this branch is only an accounting example. Its arbitrary magnetic amplitudes, assumed inductance and imposed speed must not be used to estimate this machine's rating or decide its geometry.

## Inputs that define a faithful model

| Item | Information currently available | Required before a design-specific prediction |
|---|---|---|
| Arrangement | Historical discussion includes a 300 mm rotor and a double-face arrangement with 16 gradient regions and 8 release units per face | Current authoritative drawing/CAD, orientation of both faces, axial/radial topology, gaps and tolerances |
| Rotor magnets | Earlier descriptions mention N52; the old radial model uses a different NdFeB material entry | Actual dimensions, magnetization vector for every piece, supplier grade and temperature-dependent demagnetization curves |
| Release unit | APW EML50mm-24 appears in the historical design | Confirmation of the actual device, internal magnetic circuit/materials or measured force/flux/current maps |
| Winding | Published APW voltage/resistance/current metadata; old FEMM regions use a one-turn surrogate | Physical turns, resistance versus temperature, incremental inductance and linked flux versus position/current |
| Control | Opposing pulse at trailing escape, followed by restoration | Per-channel angle/polarity/current command, rise/fall and decay paths, sensor phase, startup and stalled-rotor behavior |
| Energy/load boundary | Desired useful sustained net output | Output form, load torque/speed or electrical load, all supplies, startup energy, storage and any external shaft input |
| Reliability | Long life without routine maintenance is desired | Speed/load spectrum, ambient temperature, ingress, shaft forces and a finite service-life acceptance requirement |

The historical count and size values above are candidates to verify, not permission to silently replace a newer physical design. The present radial FEMM geometry has a 410 mm stator outside diameter; it is not a verified double-sided axial assembly.

## Simulation sequence

1. Build the actual geometry and magnetic materials from documented inputs. Use a three-dimensional model for the axial assembly, or justify any reduced representation against it. Represent the release unit's permanent magnet as well as its steel and copper.
2. Calculate or measure passive torque, field energy and linked flux across a full mechanical revolution. Preserve raw results. Compare stress-based torque with an independent energy-derivative calculation, refine mesh/boundaries/angle steps and record discrepancies. Do not remove the mean torque to hide a residual.
3. Calculate the same quantities at the actual permitted coil currents and polarities. Include saturation and local reverse-field/demagnetization limits where relevant. A static hold-force rating is not a torque-angle map.
4. Couple the winding voltage equation, current dynamics and rotor motion. Model the real bridge, bus limits, current decay and returned energy. An imposed-speed calculation has an external mechanical port; it cannot by itself establish self-starting or sustained loaded motion.
5. Model the entire approach, release, escape and restoration sequence for every channel. Use a smaller sector only after the magnetic, electrical and controller state is shown to repeat over it.
6. Compare the simulated waveforms against a one-interaction physical fixture before scaling the assembly. Then evaluate a loaded repeated cycle and thermal equilibrium with synchronized input/output measurements.

## Reporting rules

Publish the unadjusted torque integral, signed electrical exchange, all auxiliary/drive inputs, useful output and stored-energy changes separately. Record numerical sensitivity and measurement uncertainty. Positive and negative results receive the same reporting treatment. An unexplained surplus remains visible and triggers an audit; it is neither deleted nor promoted to a working-generator claim.

Energy conservation remains the governing relationship for a model using established electromagnetism. A model with independently assigned torque and switching cost can violate that relationship by construction. A consistently coupled reference model checks this mathematics; only a calibrated geometry and independent measurements can establish the specific machine's torque, input, losses and usable output.

Every new run should record input-file hashes, material sources, solver/version, mesh/boundary settings, angle/time step, current states, rotor state, bus/storage endpoints and any externally imposed motion. No fresh geometry-specific field solve or physical measurement has been performed in this branch.

## Sources

- [MIT electromechanical energy and coenergy](https://ocw.mit.edu/courses/6-061-introduction-to-electric-power-systems-spring-2011/c26f6204e05bd4c47875a96452982b6f_MIT6_061S11_ch8.pdf)
- [FEMM numerical accuracy guidance](https://femm.info/doku/doku.php?id=faq)
- [APW EML50mm-24 drawing](https://apwcompany.com/cdn/shop/files/6681.pdf?v=16184353028769850943)
