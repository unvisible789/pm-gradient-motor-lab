# Timed-release test driver and control requirements

Status: engineering specification; not a released PCB, wiring diagram or validated firmware. Updated 2026-11-08.

## Correct the existing circuit description

The earlier `circuit/Detailed_Schematic.md` is superseded. It inconsistently connected a 24 V rail and a 12–15 V supply to the gate-driver supply. It also described a clamp MOSFET directly between the capacitor-positive node and ground; switching that path would discharge the bus through the MOSFET rather than constitute a defined energy-recovery converter. Do not wire that description.

Infineon specifies a 10–20 V gate-drive supply for the IR2110. A bootstrap high-side output must be referenced to its actual switching node. These requirements cannot be satisfied by assigning arbitrary HO/VS connections. [Infineon IR2110](https://www.infineon.com/part/IR2110)

## One-channel APW characterization fixture

Use a 24 V current-limited laboratory source and a characterized current-controlled H-bridge. The coil must be between bridge outputs. Include current sensing, measured bus voltage, hardware overcurrent shutdown, overvoltage handling and temperature sensing. Retain the APW specified lead polarity until magnetic characterization establishes any permitted reverse-current operation. Applying the opposite field must not irreversibly demagnetize the permanent magnet.

The EML50mm-24 is nominally 24 V, 0.43 A, 55.9 ohm and 10% intermittent duty. The manufacturer describes release while energized. It is not established as a bistable, pulse-latched-off device. Do not connect it to the comparison motor's 48 V bus. The rated holding force is for a specified contacting steel plate, not tangential torque at a rotating air gap. [APW drawing](https://apwcompany.com/cdn/shop/files/6681.pdf?v=16184353028769850943), [operating principle](https://apwcompany.com/collections/permanent-electromagnets)

A DRV8876-class integrated bridge is a candidate for the low-power 24 V fixture, subject to current-sense accuracy, switching response, permitted coil polarity and transient margin. It provides a 4.5–37 V operating range and current regulation; its headline current rating does not qualify the motor or its thermal layout. It is not the 48 V motor inverter. [TI DRV8876](https://www.ti.com/product/DRV8876)

## Energy-return path

A bench supply must not be assumed able to absorb returned energy. Use a source explicitly able to sink it, or a sized bus capacitor and controlled dump/return path. Returned energy is counted at the source measurement once.

For a linear inductor at a fixed position, an initial estimate is `E = 0.5 L I^2`. To absorb that energy in a capacitor between two allowed voltages, `C >= 2 E / (V_max^2 - V_initial^2)`. Actual required energy includes rotor-induced effects and every simultaneously discharging channel; obtain it from measured waveforms. Set voltage limits from the selected device and measured transient overshoot. There is no defensible final capacitance, TVS or dump-resistor value until those quantities are known.

A freewheel diode can make current decay too slowly for a narrow angular release window. A regenerative decay circuit can reduce wasted magnetic energy, but winding heat remains lost. [TI inductive discharge recovery](https://www.ti.com/document-viewer/lit/html/snvaa45)

## Nonblocking angle-based controller

The old blocking 3 ms firmware example is superseded. With 16 encounters per revolution, each channel sees 266.7 encounters/s at 1,000 RPM. At 10% energized duty, the average on-time budget is only 0.375 ms per encounter. At 3,500 RPM it is 0.107 ms. Manufacturer duty-cycle timing restrictions must also be checked; duty percentage alone is not a thermal model.

Use encoder capture and timer compare/DMA or a bounded-time current-control interrupt. No `HAL_Delay`, sleeping or serial logging in the power-control path. Each channel's phase is its actual stator position relative to the rotor pattern; the 2:1 count ratio does not imply two encounters per revolution or smooth torque.

Required states:

| State | Required behavior |
|---|---|
| Disabled | Hardware power stage disabled; no automatic startup |
| Characterize | Operator-commanded bounded pulse with measured current and field/torque; rotor restrained |
| Armed | Supply, encoder, current zero-offset, timing table and temperature checks valid |
| Run | Enforce angle windows, polarity, cycle/current/temperature limits and voltage margin |
| Fault | Hardware gate inhibit; retain a defined safe inductive-discharge path; latch until deliberate reset |

Required fault inputs include lost/stale encoder, overspeed, current-limit violation, bus over/undervoltage, overtemperature, timer overrun and emergency stop. A stalled rotor must not leave a release pulse continuously energized. Firmware must enforce both a per-pulse timeout and a cumulative energized-time budget, independently of encoder movement.

Enforce manufacturer pulse and cooling restrictions, and calculate winding heating from measured `integral(i^2 R(T) dt)`, including recirculating and decaying current. A 10% PWM gate-on fraction alone does not establish compliance with the coil's 10% intermittent-duty rating.

Record bus voltage/current, coil voltage/current, rotor angle, torque, speed and temperature with synchronized timestamps. Account for a precharged capacitor or external drive; rotation alone is not evidence of useful output.

## Powered-motor comparison inverter

For the separate 48 V, 350 W powered-motor comparison, a three-phase brushless power stage with current regulation and position feedback provides a reference architecture. This is not a net-power-producing design and does not fulfill the user's generation requirement. A DRV8353-class gate driver supports external MOSFETs and current sensing, but semiconductor choice, thermal design, bus clamp, firmware and EMC validation remain part of the engineering work. [TI DRV8353](https://www.ti.com/product/DRV8353)

Use the same measured DC-input/shaft-output accounting when comparing conventional commutation with the experimental release strategy. No energy surplus or zero-maintenance claim is accepted from a controller simulation.
