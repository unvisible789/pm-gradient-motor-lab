# Prototype Readiness Review - PM Gradient Motor Lab

**Date**: 2026-06-15
**Reviewer**: Grok-assisted review

## Questions

### 1. Is the current FEMM result enough to build the full motor?

**No.**

The latest torque-angle sweep shows severe positive/negative torque cancellation, resulting in very low net average torque (~0.15 Nm) and low net work per revolution (~0.92 J). This is not a validated motor design; it is an early geometry that requires significant iteration.

### 2. Is it enough to build a low-cost torque-angle fixture?

**Yes - Reasonable next step.**

A single 45° repeat-period passive fixture is the lowest-risk, lowest-cost way to validate (or refute) the current FEMM prediction. It directly tests the core claim (torque-angle behavior) without committing to a full motor.

### 3. What exact data would justify full prototype construction?

- Passive torque-angle fixture reproduces FEMM curve shape within acceptable tolerance (peak locations, relative magnitudes, and overall trend).
- Measured integrated work over 45° is within ~20-30% of FEMM prediction (or better, depending on uncertainty budget).
- At least 5 repeatable manual sweeps with documented measurement uncertainty.
- Powered single-EML test on the fixture (after passive validation) shows net positive work contribution from pulsing without excessive negative torque or heating.
- Thermal behavior is characterized (temperature rise vs time at fixed pulse parameters).

### 4. What are the biggest failure risks?

- Torque cancellation remains severe even after geometry changes (most likely risk).
- Measurement uncertainty in the fixture masks true performance.
- Powered EML testing reveals thermal or recovery problems not visible in passive FEMM.
- Mechanical complexity and cost of full motor escalate before magnetic design is validated.
- Safety incident during early high-power testing.

### 5. What should be bought first?

Priority order:
1. Materials for single-period passive fixture (acrylic/polycarbonate rotor option, shaft, bearings, adjustable mount, lever arm, load cell + HX711, angle scale).
2. Basic safety equipment (emergency stop, fuses, current-limited power supply if not already owned).
3. One EML50mm-24 or equivalent test unit + representative N52 magnets matching FEMM geometry.
4. Simple DAQ / logging (Arduino/ESP32 + HX711 + USB scope) for angle + force.
5. Only after passive fixture success: gate driver ICs, MOSFETs, and components for single-channel driver circuit.

## Recommended Decision

- **Full motor construction**: NOT READY. Do not proceed.
- **Single-period bench fixture (passive torque-angle)**: READY. This is the correct, lowest-risk next step.
- **Powered EML circuit test**: READY only on dummy inductive load first. Never connect driver to real EML until circuit behavior is verified on dummy load.
- **Powered rotor test (synchronized pulsing)**: ONLY after passive torque-angle data matches FEMM within defined tolerance and circuit has been validated on dummy load.

## Acceptance Criteria for Phase 0 Fixture

- Measured torque-angle curve shape follows FEMM trend (peak locations and relative magnitudes).
- Integrated work over 45° is measured with documented uncertainty.
- Minimum 5 repeatable manual sweeps with consistent results.
- If measured data deviates significantly from FEMM prediction, stop full-build planning and return to model revision.

## Next Immediate Actions
1. Finalize and order materials for single 45° passive fixture.
2. Set up basic data logging (angle + force).
3. Perform first manual sweeps and compare to existing FEMM data.
4. Iterate geometry in FEMM based on measured vs predicted results.
5. Only after fixture validates FEMM trend: proceed to circuit validation on dummy load.

**Document Version**: 1.0
**Status**: Ready for implementation.
