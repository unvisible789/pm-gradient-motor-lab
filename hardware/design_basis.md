# Net-power objective and magnetic-machine design basis

Date: 2026-11-08. Status: design requirements and development decision, not a manufacturing release or a verified working prototype.

## Objective and physical boundary

The user's required outcome is sustained useful net power delivered to a load, with long operating life. A continuously powered motor does not meet a requirement to generate more energy than it receives. The proposed mechanism is timed cancellation of trailing-edge attraction followed by restoration of the field. That complete cycle, including its controls and stored-energy changes, is the subject of the assessment.

**Feasibility decision:** no physically supported energy source has been identified that would let this permanent-magnet-only arrangement supply sustained net power while returning to the same state. A permanent magnet supplies magnetic excitation; its long magnetic lifetime is not a fuel capacity or a runtime rating for the complete machine. Removing trailing attraction requires changing the magnetic interaction; the work and electrical exchange of that change cannot be omitted. Existing numerical residuals do not establish generation. See [net-power assessment](../reports/net_power_feasibility.md).

A generator can deliver net electrical power when supplied with mechanical work or another identified external energy source. No such source has been selected for this project. Energy amplification above unity and indefinite maintenance-free operation are not achievable specifications for the proposed closed repeating system. High torque at low speed, mechanical gearing and a low-power control signal are distinct from energy amplification.

The powered-motor option below is retained solely as an engineering comparison, not as fulfillment of the net-generation requirement. Its optimization objective would be useful continuous shaft output per net electrical input, subject to temperature, demagnetization, voltage, current, mechanical and service-life constraints.

The first reference operating point is 350 W at 1,000 RPM, requiring 3.342 Nm. This point comes from the earlier project discussion and makes comparisons concrete; it is not an achieved capability. The 300 mm dimension refers to the rotor only. The current radial surrogate has a 205 mm stator outer radius, so it does not fit inside a 300 mm complete-machine diameter. The actual axial layout and housing envelope remain unverified.

## Powered-motor comparison only

| Item | Development choice | Evidence/status |
|---|---|---|
| Comparison energy source | External DC supply; 48 V nominal for a powered-motor comparison | Does not meet the net-generation goal; not an instruction to run the 24 V EML at 48 V |
| Rated output | 350 W continuously at 1,000 RPM | Target only |
| Efficiency | 85% minimum development target; 90% stretch target at the rated point | Targets requiring measurement from net DC input to shaft, including control electronics |
| Practical comparison motor | Brushless permanent-magnet machine with laminated stator, regulated phase currents and position feedback | Proven architecture class; this custom geometry is not yet validated |
| Experimental mechanism | Opposing current during the measured trailing attraction interval, followed by controlled current decay and field restoration | Must be tested against ordinary commutation under the same load and temperature |
| APW EML50mm-24 | One-channel 24 V characterization fixture | 10% duty and unknown magnetic transient response do not justify selecting it for continuous 350 W service |
| Cooling | Passive cooling if the thermal budget permits; avoid a cooling fan as an additional wear item | Thermal model and loaded test required |
| Mechanical drive | Direct drive where torque/speed match the application | Gearboxes add losses and service requirements; no universal drive ratio |
| Lifetime | A specified service interval under specified loads/environment | No lifetime claim until bearing, lubricant, winding, electronics and magnet conditions are quantified |

## Powered comparison: reference power and thermal budget

These are arithmetic consequences of hypothetical system efficiencies, not simulated ratings:

| Assumed overall efficiency | Electrical input for 350 W shaft output | Total losses | Average 48 V source current |
|---:|---:|---:|---:|
| 85% | 411.76 W | 61.76 W | 8.58 A |
| 90% | 388.89 W | 38.89 W | 8.10 A |
| 95% | 368.42 W | 18.42 W | 7.68 A |

At 90%, the total heat budget is about 39 W. If a lumped case-to-ambient rise of 20 K were selected, its equivalent thermal resistance would need to be at most about 0.51 K/W. This simple budget does not resolve winding/magnet/semiconductor hot spots, heat splitting, or touch-temperature requirements; those need the actual thermal network and measurements.

For the legacy 16-unit EML arrangement, if every channel is explicitly limited to 24 V, 0.43 A and 10% supply-energized duty, its gross source-energy rate is bounded by `16 * 24 * 0.43 * 0.10 = 16.51 W`, before losses. That is a conditional electrical bound, not a measured operating point or a prediction of achievable output. Briefly drawing down a precharged capacitor/flywheel does not change the continuous balance. This constrained hardware cannot support a sustained 350 W shaft target; the coil/driver architecture must change for that target.

## Preserve the release concept without assigning free torque

For a linear reduced model, use a consistent magnetic potential, linked flux and inductance map:

`torque = -dU_PM/dtheta + i*dpsi_PM/dtheta + 0.5*i^2*dL/dtheta`

`voltage = R*i + L*di/dt + (i*dL/dtheta + dpsi_PM/dtheta)*omega`

The linked-flux term that produces useful torque also appears in the electrical terminal voltage. Do not supply torque independently of that coupling or remove backward torque at no switching cost. Include saturation/hysteresis through measured or validated field maps when the linear model is insufficient.

The new reduced model is a software/physics reference using declared illustrative maps. It is not calibrated to APW internals, the custom N52 rotor, or a 3D field solution. Its sweep can reject infeasible commands and check accounting, but cannot select a final winding or certify shaft output.

## Required magnetic characterization before final geometry

1. Record magnet dimensions, magnetization direction, temperature-dependent demagnetization curves, air gap, pole/yoke geometry and mechanical tolerances.
2. Measure actual coil resistance versus temperature, turns and wire dimensions (or obtain a manufacturer model), and incremental inductance/flux linkage versus angle and current.
3. Measure torque through the entire interaction for zero current and both permitted current directions. The stator permanent magnet must be represented when testing an EML; the existing steel/copper surrogate omits that physical detail.
4. Check passive energy closure and state periodicity before using a curve for optimization. Missing/partial sweeps and passive bias cannot become positive shaft-energy assumptions.
5. Test dynamic voltage/current and actual cancellation at the intended speed. Current commands that cannot be reached within voltage/duty constraints are infeasible.

## Reliability and application limits

Lifetime is constrained by the weakest qualified subsystem, not just magnetic-field persistence. Bearings and grease, rotor retention/balance, insulation, adhesives, corrosion protection, power capacitors, semiconductors and connectors all require engineering. Use temperature and stress margins, seals appropriate to the environment, replaceable bearing/electronics modules and condition monitoring. Avoid extreme peak-output operation when continuous service life is the priority.

There is no universal motor for every application. Define a family after verifying a reference module: low-speed/high-torque, higher-speed, wet/corrosive, high-temperature and precision-motion duties have different requirements. Do not label an untested module suitable for vehicles, lifting loads, medical equipment or other safety-critical uses.

## What is complete and what remains

The repository now supplies corrected energy-accounting tools, a closed-cycle reference simulation, a passive-data audit, and a staged characterization specification. It does not contain a validated net-power-producing design, a calibrated magnetic map, released PCB/CAD, a physical prototype, dynamometer result or endurance qualification. A single-interaction fixture can test torque and switching-energy assumptions; it cannot supply a missing energy source. A buildable power generator requires an identified source of input energy before final geometry and hardware can be selected.

## Sources

- [MIT electromechanical conversion and losses](https://ocw.mit.edu/courses/6-061-introduction-to-electric-power-systems-spring-2011/c26f6204e05bd4c47875a96452982b6f_MIT6_061S11_ch8.pdf)
- [APW EML50mm-24 specification](https://apwcompany.com/cdn/shop/files/6681.pdf?v=16184353028769850943)
- [APW permanent electromagnet operating principle](https://apwcompany.com/collections/permanent-electromagnets)
- [FEMM numerical accuracy guidance](https://femm.info/doku/doku.php?id=faq)
- [TI three-phase current-controlled driver architecture](https://www.ti.com/product/DRV8353)
- [Driver and acquisition requirements](release_driver_requirements.md)
