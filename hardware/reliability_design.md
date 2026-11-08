# Powered-motor comparison: hardware and reliability reference

**Scope update:** the user requires sustained net power production. The externally powered motor in this document does not meet that requirement. It is retained as a comparison architecture and reliability reference only; see the [net-power assessment](../reports/net_power_feasibility.md) for the project decision.

**Status: engineering comparison and test specification, not a validated construction release.** This document preserves the proposed timed reduction of trailing magnetic attraction as a research function and defines a practical powered motor baseline against which to measure it. None of the output, efficiency, temperature, or service targets below has been demonstrated by the existing design.

## 1. Conditional powered-motor alternative

If the objective were changed to an efficient powered motor, the practical comparison would be a brushless permanent magnet motor with a laminated stator, measured rotor position, closed-loop phase-current control, and a passive heat path into an aluminum housing. A nominal 48 V DC bus is a candidate for that comparison. The existing 24 V power-to-release magnet needs an instrumented test fixture before any full ring of release coils is justified.

The useful optimization is continuous shaft output per total electrical input, subject to thermal and life limits. A permanent magnet supplies a persistent magnetic field; it does not replenish the mechanical energy delivered to a load. In repeatable steady operation, input energy supplies shaft work and losses. Recovering a coil's remaining magnetic energy can reduce switching loss but cannot recover energy already dissipated as heat. The full system must be evaluated over cycles that return electrical, mechanical, and magnetic storage to the same state. See MIT's electromechanical energy treatment [1].

A practical product objective is a long, specified service interval in a defined environment. “Until the magnets expire” is not a sufficient life specification: lubricant, bearings, seals, insulation, electronics, corrosion protection, and magnet retention can set the limit earlier. The present design cannot support a claim of zero maintenance or suitability for every application.

## 2. Geometry and model corrections

The current geometry configuration identifies a **300 mm rotor**, not a complete 300 mm motor. Its stator outer radius is 205 mm, so the represented stator alone has a **410 mm outside diameter**, before the enclosure and supports. The 25 mm model depth is an electromagnetic-model parameter, not a released axial assembly dimension. The double-sided axial concept needs its own geometry and force analysis; the existing radial two-dimensional model does not validate it [2].

The configuration uses **“NdFeB 40 MGOe”**, while earlier hardware descriptions call for N52. These are not interchangeable material definitions. The local field, demagnetization margin, and torque prediction must use the actual purchased grade's temperature-dependent curves. The existing “EML” regions represented by steel and copper do not reproduce an actual holding magnet's internal permanent magnet and complete magnetic circuit [2].

Keep the 300 mm rotor only as a reference constraint until packaging, air gap, shaft supports, rotor retention, and application loads are resolved. Do not optimize pole count or final copper turns around an incomplete model.

## 3. Provisional baseline specification

All values labeled **target** are proposed acceptance goals for engineering development.

| Item | Proposed design basis | What remains to be established |
|---|---|---|
| Continuous output | **350 W at 1,000 rpm** | Dynamometer demonstration at thermal equilibrium |
| Continuous shaft torque | **3.34 N·m** at rated speed | Torque sensor calibration, ripple, bearing losses |
| Mechanical work per revolution | **21.0 J/rev** at the rated point | Complete electrical-to-mechanical energy balance |
| Supply | **48 V nominal DC** for the continuous motor | Minimum, maximum charge, transients, and regenerative sink capability |
| Control | Three-phase inverter; sensored field-oriented control | Actual pole count, electrical parameters, current sensors, tuning |
| Rated efficiency | **85% minimum development target; 90% stretch target**, measured from total DC input to useful shaft output | Includes inverter and controls; no simulated efficiency claim |
| Torque ripple | Initial target **≤10% peak-to-peak of mean torque** at the rated point | Measurement bandwidth, load inertia, relevant acoustic requirement |
| Cooling | Passive conduction and natural convection; no cooling fan in the initial baseline | Housing thermal resistance and mounting conditions |
| Initial operating context | Stationary, nonhazardous, indoor application; **0–40°C ambient** | Actual ingress, humidity, shock, shaft-load, acoustic, and safety requirements |
| Rotor | Existing **300 mm reference rotor** | Overall assembly dimensions and containment |
| Service objective | **50,000 operating hours** as a design-study objective | Bearing/grease calculations, component aging, testing, failure-rate evidence |

The service objective is not a calculated life or a warranty. At continuous operation, 50,000 hours is about 5.7 years; intermittent operation changes calendar aging and starts/stops. It cannot be extended to another speed, temperature, load, or environment without requalification.

### Power and cooling budget

These numbers are calculated from the proposed output and efficiency targets, not obtained from a prototype:

| Assumed total efficiency | Required DC input | Total losses | Average 48 V bus current | Average 24 V bus current |
|---|---:|---:|---:|---:|
| 85% | 411.8 W | 61.8 W | 8.58 A | 17.16 A |
| 90% | 388.9 W | 38.9 W | 8.10 A | 16.20 A |

Bus current is not phase current. Phase current and copper size require a winding design and verified torque constant. Moving from 24 V to 48 V halves bus current for the same input power; it reduces loss in an unchanged supply harness to one quarter. It does not automatically produce the same reduction in winding loss.

With a provisional 40 K housing-rise budget, dissipating 61.8 W through one housing would require housing-to-ambient thermal resistance no greater than approximately **0.65 K/W**. This is a coarse enclosure requirement. Winding-to-stator, stator-to-case, transistor-to-case, and magnet temperatures need a separate thermal network. A case near 80°C at 40°C ambient also requires an application-specific touch-temperature assessment.

## 4. Existing release magnet versus a continuous motor stator

| Consideration | APW EML50mm-24 research module | Custom laminated stator baseline |
|---|---|---|
| Intended role | Characterize trailing attraction and power-to-release behavior | Produce continuous controlled shaft torque |
| Supply basis | Manufacturer's 24 V rating | Nominal 48 V bus, winding selected accordingly |
| Magnetic behavior | Permanent holding force reduced while its release winding is energized | Three-phase rotating field acting with rotor magnets |
| Documented limitation | 10% duty; no demonstrated motor-speed switching specification | Continuous-duty design must be calculated and tested |
| Core construction | Actual internal construction and dynamic-loss data must be obtained | Insulated electrical-steel laminations selected for frequency and flux |
| Scaling decision | Expand only after dynamic energy and thermal measurements | Optimize winding, pole/slot combination, cooling, and inverter jointly |

APW lists the EML50mm-24 at 24 V, 0.43 A, approximately 55.9 Ω and 10.3 W energized, with 10% duty. It is a power-to-release permanent holding electromagnet; the published information does not establish a bistable, pulse-latching electropermanent magnet or a fast motor commutation rating. Its approximately 112 lb holding-force rating concerns its specified contact arrangement and cannot be converted directly into shaft torque [3].

For 16 rotor encounters per revolution, **each release unit encounters 266.7 events/s at 1,000 rpm**. Equal use of a 10% duty allowance would provide only **0.375 ms energized per encounter**. At 3,500 rpm those values become 933.3 events/s and 0.107 ms. These are timing calculations, not evidence that the device can function at those rates. Coil inductance, mutual coupling, voltage available during current rise and fall, eddy currents, and the manufacturer's permitted duty-cycle period remain unknown. A two-unit-count ratio does not imply two pulses per coil per revolution.

Measure the APW module at its intended voltage and conservative manufacturer duty limit first. Do not apply the previous multiampere current assumptions to its 0.43 A winding without a separate winding design and verified electrical/thermal limits. A true bistable EPM is a different device with a measured switching energy, pulse requirement, magnetic state, and endurance specification; Knaian's work is relevant background, not a performance specification for this APW unit [4].

For the rotating motor, a laminated custom stator is the stronger continuous-duty development path because its copper window, flux path, inductance, heat path, and core losses can be designed together. Solid steel modeled with a static magnetic solution is not sufficient evidence for low dynamic loss. The final design needs measured or manufacturer core-loss data at its actual electrical frequency and flux waveform.

## 5. Rotor magnets and mechanical construction

**Use the highest useful coercivity and thermal margin, not the highest room-temperature grade number.** Select an appropriate high-coercivity NdFeB candidate, then validate the worst local reverse field at maximum magnet temperature, maximum current, short-circuit/braking conditions, and the proposed opposing release pulse. N42SH is an example candidate family to investigate; it is not a released part selection.

Arnold's published table illustrates the tradeoff: its N52 entry lists typical remanence of 1.450 T, minimum intrinsic coercivity of 876 kA/m, and a 60°C maximum-use entry. Its N42H entry lists 1.300 T, 1,353 kA/m, and 120°C. Those catalogue temperatures do not replace a load-line and hot demagnetization analysis. Arnold also identifies protective finishes for NdFeB in humid conditions [5]. Different suppliers' similarly named grades require their own curves.

SmCo deserves comparison when high temperature, temperature stability, or corrosive exposure dominates. Arnold describes its better preservation of magnetic performance at elevated temperature relative to NdFeB. Its cost, available geometry, brittleness, assembly difficulty, and room-temperature output must be evaluated in the actual motor [6].

For the preliminary thermal design, seek **at least a 20°C margin below the supplier-approved operating limit for the actual magnetic load line**, then verify local demagnetization margin directly. This is an engineering screening target, not a general magnet-life rule. A magnet's Curie temperature is not its permissible motor operating temperature.

Mechanically capture magnets with a retention feature appropriate to their location and speed. Adhesive can supplement retention and manage heat transfer, but should not be the sole unexamined barrier against release. Analyze rotor stress, fasteners, tolerance stack, air-gap closure, thermal expansion, and overspeed. Balance the assembled rotor. An axial double-rotor design also needs assessment of static axial attraction and imbalance between its two air gaps. Keep ferromagnetic debris away from the air gap and bearing regions.

## 6. Reliability architecture and derating targets

Choose direct drive where the load permits it, so that a gearbox does not add lubrication and wear requirements. Use a replaceable bearing cartridge, protected winding module, and separately replaceable inverter. Provide thermal conduction paths before selecting potting: encapsulation can impede heat removal and make a small failure irreparable. Sealing needs an actual ingress specification; enclosure breathing, condensation, and shaft-seal drag must be included.

SKF explains that bearing and grease life depend on operating load, speed, temperature, contamination, vibration, and lubrication conditions. “Sealed and greased for life” describes a bearing arrangement with a finite application life. More grease is not automatically better [7]. Select bearing type, clearance, preload, lubricant, and seals after calculating radial and axial loads. A bearing L10 calculation is a population fatigue-life measure under stated conditions, not a guarantee for every motor or a prediction of lubricant and seal life.

Use the following as **initial continuous-operation screening targets**, subject to lower limits imposed by the actual components and application:

| Location or quantity | Preliminary target | Reason and verification |
|---|---|---|
| Winding hot spot | ≤100°C at rated load and 40°C ambient | Validate the complete insulation system; embed a temperature sensor and correlate with winding resistance |
| Power-transistor junction | ≤110°C during continuous rating | Calculate from measured losses and thermal impedance; account for start/stop cycling |
| Bearing outer ring | ≤70°C during continuous rating | Confirm lubricant suitability and inner-ring temperature; external reading alone is incomplete |
| Magnet temperature | At least 20°C below validated supplier/application limit | Verify hot reverse-field margin, including release pulses |
| Housing temperature rise | ≤40 K under the specified mounting condition | Demonstrate passive cooling at worst ambient and load |
| DC bus and switches | Margin above maximum supply plus clamped transients | Select after measuring overshoot and regenerative behavior |

For a 48 V system, a 100 V transistor class is a reasonable starting investigation, not proof of adequate voltage margin. TI's TIDA-00281 demonstrates a 48 V, three-phase, 1 kW motor-drive reference architecture with phase feedback and 100 V MOSFET examples. It supports the feasibility of the voltage/power class; it does not validate this rotor, winding, control design, or service interval [8]. The gate supply must follow the selected driver and transistor specifications; never treat the motor bus as a gate-drive voltage.

DC-link electrolytic capacitors also require a life calculation. Nichicon identifies temperature, ripple current, and applied voltage as major life factors; electrolyte loss or material degradation changes capacitance and ESR [9]. Keep capacitors away from hot windings and switching devices, use their actual ripple rating and manufacturer life model, and consider film capacitors where size and capacitance requirements permit. A higher printed temperature rating alone is not evidence of 50,000 hours in this housing.

## 7. Driver requirements and energy recovery

The previous circuit descriptions are **conceptual only and must not be treated as wiring instructions**. The continuous design requires a reviewed inverter schematic, gate supply, current sensing, dead time, defined switch states, transient suppression, and PCB layout. Establish the exact input-voltage range before selecting devices.

Required protective behavior includes hardware current limiting, a properly rated DC fuse, winding and inverter overtemperature derating, stall timeout, rotor-position fault handling, overspeed detection, undervoltage response, and a controlled stop or safe de-energized condition. Prevent unintended restart after a fault where the application requires it. Fault response must cover a driven load that can regenerate even after commanded torque is removed.

Provide a verified path for regenerated energy. A bench supply or a battery with a disconnected BMS may not accept reverse current. Size the DC-link capacitor and braking/dump path from the worst stopping energy and overhauling-load case. TI's inductive-discharge discussion explains why simple freewheeling slows current decay and why higher-voltage clamping can accelerate it [10]. Energy returned to the bus must be measured as returned energy; it must not also be deducted a second time from reported electrical input.

## 8. Development gates

1. **Validate the magnetic representation.** Model the actual rotor materials and the release module's internal magnetic circuit. Demonstrate mesh and angular-step convergence and energy consistency over a full cycle before interpreting small net-work differences. Separate two-dimensional studies from a real three-dimensional axial assembly.
2. **Characterize one release module.** Measure resistance versus temperature, current rise/fall, inductance versus position/current, force or torque versus gap/angle, release delay, and temperature over the intended duty pattern. Determine whether useful release is possible within the available encounter window.
3. **Compare with the continuous baseline.** Test the powered brushless design at the same shaft speed and load. Compare total DC input, useful output, thermal rise, torque ripple, noise, and fault behavior. A release pulse earns its place only if it improves a measured system objective at acceptable cost and stress.
4. **Establish the continuous rating.** Measure electrical input and torque/speed simultaneously after temperatures stabilize at worst specified ambient. Include controls and auxiliary power. Verify startup, stall, braking, supply interruption, and load transients.
5. **Qualify the service claim.** Calculate bearing fatigue and grease life using actual loads; calculate capacitor and semiconductor thermal stress; test retention, insulation, ingress, vibration, and endurance. Track magnet flux or back-EMF changes at the same temperature. Release a finite service interval only after the evidence supports it.

A successful powered comparison would be a repeatable, efficient 350 W motor within a declared operating envelope, with the timed-release idea either demonstrated as a useful feature or retired based on measurements. That would still not fulfill the user's net-generation requirement. Presently, turns, current, air gap, pole/slot arrangement, core material, enclosure size, shaft loads, and dynamic release performance remain unresolved. A fabrication-ready motor cannot honestly be claimed until those parameters and the above tests are completed.

## Sources

[1] MIT OpenCourseWare, *Electromagnetic Forces and Loss Mechanisms*, 6.061 course material: https://ocw.mit.edu/courses/6-061-introduction-to-electric-power-systems-spring-2011/c26f6204e05bd4c47875a96452982b6f_MIT6_061S11_ch8.pdf

[2] Existing project, `geometry/pm_gradient_motor_config.json` and current magnetic model: https://github.com/unvisible789/pm-gradient-motor-lab . Geometry statements above were checked against the local configuration; they are project inputs, not validated dimensions.

[3] APW Company, *EML50mm-24 Round Permanent Electromagnet*, product and drawing: https://apwcompany.com/products/eml50mm-24-round-permanent-electromagnet-50-mm-dia-24-volts-dc-holding-112-lbs and https://apwcompany.com/cdn/shop/files/6681.pdf?v=16184353028769850943 . Manufacturer category description: https://apwcompany.com/collections/permanent-electromagnets

[4] Ara Nerses Knaian, MIT, *Electropermanent Magnetic Connectors and Actuators: Devices and Their Application in Programmable Matter* (2010): https://cba.mit.edu/docs/theses/10.06.knaian.pdf

[5] Arnold Magnetic Technologies, *Neodymium Iron Boron Magnets*, material property table and coating guidance: https://www.arnoldmagnetics.com/products/neodymium-iron-boron-magnets/

[6] Arnold Magnetic Technologies, *Samarium Cobalt vs. Neodymium Iron Boron*: https://www.arnoldmagnetics.com/resources/samarium-cobalt-vs-neodymium-iron-boron/

[7] SKF Evolution, *Improved grease life model for Y-bearings*: https://evolution.skf.com/improved-grease-life-model-for-y-bearings/ . Its product-specific equations must not be transferred indiscriminately to another bearing family.

[8] Texas Instruments, *TIDA-00281 Automotive 48-V, 1-kW Motor Drive Reference Design*: https://www.ti.com/tool/TIDA-00281

[9] Nichicon, *Lifetime Calculator*, component aging and operating-condition guidance: https://www.nichicon.com/en-us/design-support/lifetime-calculator/

[10] Texas Instruments, inductive-load discharge application note SNVAA45: https://www.ti.com/document-viewer/lit/html/snvaa45
