# Net-power feasibility assessment

Updated 2026-11-08 to reflect the user's explicit requirement: the design should deliver useful sustained power, not consume more energy than it produces.

## Decision

**Evidence limitation:** the user has specifically cautioned that older AI-produced simulations may be flawed. Treat the old data as unvalidated historical calculations. Their defects undermine earlier performance claims; they do not establish the physical design's actual output. The new analytic reference is not a faithful simulation of the user's geometry either. A [fresh model specification](../hardware/fresh_model_specification.md) records what is needed for that work.

**The existing design does not demonstrate sustained net energy generation. A permanent-magnet-only machine that returns to the same state every cycle cannot supply continuous net work without another energy source.** No winding, timing, magnet grade or geometric optimization removes that energy requirement.

The user's proposed action is specifically an opposing field during the trailing attraction interval, intended to let the rotor escape, followed by restoration of the interaction. That mechanism is retained in the investigation. It must be evaluated with the cost of creating, changing and restoring the field included; removing a negative portion of a passive torque curve without that cost is not a physical model of the complete device.

The 48 V brushless motor material elsewhere in this branch is a powered comparison and reliability reference. It does not meet the net-generation requirement. No alternate external energy source has been selected on the user's behalf.

## What positive output must mean

Positive shaft torque or electrical voltage alone does not establish generation. For a system with useful output, external inputs, losses and recoverable stored energy, use

`E_input_total - E_output_useful = E_loss + delta_E_storage`.

The accounting boundary must include the release supply, control supply, external shaft drive, generator/load, precharged capacitors, batteries and rotor inertia. Define thermal losses and thermal storage consistently so the same energy is not counted twice. Include any change in magnet state when claiming the magnets are the source.

| Observation | What it establishes |
|---|---|
| Positive torque over part of a turn | A local magnetic interaction; the remainder of the cycle is still required |
| Rotation after a push or charged-capacitor pulse | Conversion of stored/input energy; not sustained generation |
| Shaft output greater than control-electronics consumption | An incomplete gain ratio unless all drive energy is included |
| Electrical export from an externally driven PM generator | Conversion of external mechanical work into electrical output |
| Output exceeding all measured inputs, with unchanged stored state | An unresolved energy discrepancy requiring independently checked measurements, not a verified generator from a simulation residual |

For a repeating state, `delta_E_storage = 0`. Useful output then cannot exceed total input; losses make it smaller. With zero continuing input and no depletion of storage, sustained positive output is unavailable. A strong persistent field provides coupling and excitation, not a continuing fuel flow. MIT's treatment derives the electrical/mechanical power balance and separates reversible field storage from losses [1].

## What the stored project data actually show

The [passive-cycle audit](passive_cycle_audit.md) re-integrates the existing raw data. It does not run a new magnetic field solver or modify the data.

- The complete 360-degree historical curve has a nonzero work residual. A passive cycle residual is a numerical/model-validation problem until explained, not validated output.
- The 45-degree files labelled coarse, medium, fine and very-fine mesh have residuals that shrink and change sign. Their metadata do not establish a controlled convergence study, but they do not support treating a selected positive value as stable output.
- The purported 0.25-degree refinement contains only 67 points from 0 to 16.5 degrees, rather than the intended 45 degrees. It must not be extrapolated into a full-cycle output estimate.
- A passive 45-degree sector needs documented geometric and magnetic symmetry before its result is scaled. An actively switched sector additionally needs the complete controller and coil states to repeat.

The raw files are preserved. The audit reports the residuals and uncertainty about their interpretation; it does not force their average torque to zero to make the result look better.

The [active-sector comparison](pulse_assist_comparison.md) also preserves a positive result: the stored high-excitation case has raw 45-degree work about 0.005865 J above its coil-off case. Low and medium excitation produce negative differences. These are unvalidated calculations, not measurements; none includes the electrical exchange needed to infer net generation. The positive value is reported, not removed.

## Corrected modelling approach

The new reduced model links torque and terminal voltage through the same magnetic functions:

`tau = -dU_PM/dtheta + i*dpsi_PM/dtheta + 0.5*i^2*dL/dtheta`

`v = R*i + L*di/dt + (i*dL/dtheta + dpsi_PM/dtheta)*omega`.

Consequently, the coupling used to change torque also appears at the electrical port. The implementation uses constant inductance and explicitly illustrative periodic maps. It is not calibrated to the APW module or the user's rotor; its calculated watts and efficiencies are not hardware predictions. Its role is to exercise consistent accounting, release timing, voltage/current constraints, and energy recovery without an omitted energy source.

Returned coil energy reduces net electrical input only once. Copper heat, semiconductor loss and mechanical loss are not recovered by returning the remaining inductive energy to a capacitor. The input must be measured as signed voltage times current at a defined boundary [2].

The existing APW module is a power-to-release permanent holding electromagnet. Its published 24 V, 0.43 A and 10% duty data do not establish the fast, nearly cost-free, pulse-latched release assumed in earlier estimates [3].

## Decisive experimental check

Before building a full ring, characterize one actual rotor/stator interaction with known geometry. Record torque versus angle at zero current and during the allowed opposing-current waveform; record coil and source voltage/current on synchronized time bases. Measure a complete encounter including field restoration. A controlled external drive used to maintain speed is an input and must be metered.

Repeat at relevant speeds, gaps and temperatures. Include control power, current-decay intervals, winding heat, capacitive and kinetic energy changes, and measurement uncertainty. When adding an electrical generator/load, measure loaded output and the additional shaft input it requires. Open-circuit voltage and no-load rotation are insufficient.

These measurements can establish whether the proposed release mechanism improves the efficiency or torque characteristics of an externally powered machine. They cannot make a source-free closed cycle supply net energy. A practical generator design needs an identified input source such as shaft work from wind, flowing water or an engine; the source and application then determine the suitable magnet, winding and reliability design.

## Work status

Completed in this branch: corrected accounting and promotion criteria, reproducible passive-data checks, an energy-consistent illustrative release model, and characterization/driver/reliability specifications. Not completed or claimed: a net-power-producing device, calibrated field simulation of the actual assembly, fabrication-ready hardware, measured output, or a maintenance-free lifetime.

Software verification: 58 unit tests pass. The passive audit re-integrates eight existing files, and the illustrative accounting study evaluates 1,560 declared analytic commands. Neither count is evidence of physical machine performance. The tests include missing/incomplete data, whole pulse-event counting, correct winding units, conventional energy closure, storage depletion, recovery counted once, and rejection of pulses missed by the sampling grid.

## Primary sources

[1] MIT OpenCourseWare, *Electromagnetic Forces and Loss Mechanisms*: https://ocw.mit.edu/courses/6-061-introduction-to-electric-power-systems-spring-2011/c26f6204e05bd4c47875a96452982b6f_MIT6_061S11_ch8.pdf

[2] Texas Instruments, inductive-load discharge and energy recovery: https://www.ti.com/document-viewer/lit/html/snvaa45

[3] APW EML50mm-24 drawing: https://apwcompany.com/cdn/shop/files/6681.pdf?v=16184353028769850943 ; permanent electromagnet operating principle: https://apwcompany.com/collections/permanent-electromagnets
