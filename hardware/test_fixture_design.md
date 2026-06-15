# Single-Period (45°) Torque-Angle Test Fixture Design

**Objective**: Validate FEMM torque-angle results with lowest possible cost and complexity before building anything larger.

## Minimum Test Article
- Partial rotor segment or simple disk representing **one 45° repeat period** (one PM gradient).
- One representative stator/EML position.
- Adjustable air gap (0.5 mm – 5 mm recommended).
- Rigid, bearing-supported shaft.
- Indexed angle scale from 0° to 45° (manual stepping first).
- Load cell or digital force gauge with fixed lever arm to measure tangential force.
- Mechanical guards and non-magnetic construction where possible.

## Mechanical Layout (Conceptual)

```
[Fixed Base Plate]
   |
   +-- [Bearing Block 1] -- [Shaft] -- [Rotor Disk/Segment] -- [Bearing Block 2]
   |                                              |
   |                                         [Lever Arm + Load Cell]
   |
   +-- [Adjustable Stator Mount] -- [EML50mm or test magnet assembly]
   |
   +-- [Angle Scale / Encoder]
```

## Key Features

- **Rotor**: Acrylic, polycarbonate, 3D printed PETG/ASA, or aluminum disk. Magnet pockets or surface mounting with epoxy/retaining compound.
- **Shaft**: Precision ground 12-16 mm steel or stainless, keyed or flat for encoder.
- **Bearings**: 608-2RS or 6001-2RS in pillow blocks or custom blocks.
- **Stator Mount**: Slotted plate or linear rail + carriage for repeatable air gap adjustment.
- **Angle Measurement**: High-quality printed degree wheel (0-45° with 1° or 0.5° marks) + pointer for manual tests; quadrature encoder for automated later.
- **Force/Torque Measurement**: Load cell (5-50 kg range) on a fixed lever arm of known length. Torque = Force × Arm Length.
- **Guards**: Clear acrylic or polycarbonate shields around rotating parts and pinch points.

## Measurement Protocol (Passive First)
1. Manually step rotor in 1° or 2° increments from 0° to 45°.
2. Record angle and tangential force at each step (at least 5 full sweeps for repeatability).
3. Calculate torque and integrated work over 45°.
4. Compare curve shape and net work to FEMM prediction.
5. Document measurement uncertainty (repeatability, sensor specs, lever arm tolerance).

## Acceptance Criteria
- Measured torque-angle curve shape must follow FEMM trend within reasonable tolerance (e.g., peak locations and relative magnitudes).
- Integrated work over 45° must be measured and reported with uncertainty.
- At least 5 repeatable manual sweeps with consistent results.
- If measured data deviates significantly from FEMM, stop and revise model before proceeding to powered tests.

## Later Upgrade Path
- Add motor/encoder for automated sweeping.
- Add powered EML pulsing (only after passive data validates FEMM).
- Expand to multiple periods or full motor only after Phase 0 success criteria are met.