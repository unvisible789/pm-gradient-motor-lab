# Circuit Integration Notes

## Reference to Existing Circuit Work
This package builds on the circuit concepts already documented in the repository (Active Clamp / resonant recovery topologies discussed in Grok's earlier notes). Do not duplicate effort; integrate and extend.

## Critical Rule: Separate Circuit Validation from Motor Validation

**Never connect the driver circuit to a real EML until it has been validated on a dummy inductive load.**

Recommended dummy load: air-core inductor or power resistor + inductor combination with similar inductance and resistance to the target EML50mm-24 unit.

## Required Measurements (Minimum Set)

- Bus voltage (main supply rail)
- Bus current (into the driver)
- Coil voltage (directly across EML or dummy)
- Coil current (in series with coil)
- Recovery capacitor voltage (primary indicator of recovered energy)
- Gate drive signal(s) (timing and dead time verification)
- Rotor angle (for synchronized testing)
- Torque / force (via load cell)
- Temperature at multiple points (coils, MOSFETs, recovery caps)

## Energy Recovery Validation
Recovered energy must be quantified as **actual energy returned to usable storage**, calculated from capacitor voltage change:

E_recovered = 0.5 × C × (V_final² - V_initial²)

Do not count voltage spike suppression alone as "recovery."

## Grounding and Isolation Warnings
- Use differential probes or isolated measurement where high-side current or voltage sensing is performed.
- Avoid connecting oscilloscope ground to power ground when measuring high-side signals.
- Clearly document all ground references in lab notes and schematics.
- Consider isolated USB interface for PC-connected DAQ during early high-power testing.

## First-Time Power-Up Checklist
1. Visual inspection of all connections and polarity.
2. Continuity check (no shorts).
3. Power up control logic only (no power stage).
4. Verify gate drive signals with dummy load connected.
5. Apply low voltage to power stage and check for expected behavior.
6. Gradually increase voltage while monitoring current and temperature.
7. Confirm energy recovery capacitor charges as expected after each pulse.