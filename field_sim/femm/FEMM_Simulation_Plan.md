# Prioritized FEMM Simulation Plan - Reducing Negative Torque

**Goal**: Progress from current ~1.39 J/rev toward the 8–20 J target range by systematically reducing negative torque through geometry and control improvements.

**Current Baseline** (as of latest torque-angle solve):
- Net work per revolution: ~1.39 J
- Severe positive/negative torque cancellation still present

## Priority 1: Rotor Gradient Shape + Flux Barriers (Highest Impact)

**Objective**: Significantly reduce negative torque peaks by improving how flux flows through and between the permanent magnet gradients.

**Simulation Tasks** (in order):

1. **Baseline Geometry Audit**
   - Load current best geometry.
   - Run full 0–360° torque-angle sweep at 2° steps.
   - Document peak positive torque, peak negative torque, average torque, and net work per revolution.

2. **Add Flux Barriers Between Gradients**
   - Introduce non-magnetic gaps or low-permeability regions between each gradient.
   - Sweep barrier width (e.g. 2 mm, 4 mm, 6 mm) and radial depth.
   - Identify configuration that gives the largest reduction in negative torque with acceptable loss of positive torque.

3. **Concentrated / Shaped Pole Geometry**
   - Modify gradient shape from simple arcs to more concentrated poles.
   - Test leading-edge vs trailing-edge asymmetry.
   - Goal: Strengthen forward torque while weakening backward pull.

4. **Partial Halbach Arrangement**
   - Apply partial Halbach magnetization pattern on rotor gradients.
   - Compare field strength on active side vs back side.
   - Measure impact on negative torque regions.

**Success Criteria for Priority 1**:
- Negative torque peak reduced by at least 40–50% from baseline.
- Net work per revolution increased to minimum 3–4 J (ideally 5+ J).
- Positive torque peak maintained or only modestly reduced.

## Priority 2: Selective / Position-Based EML Pulsing Strategy

**Objective**: Maximize net positive work by only pulsing EMLs when they contribute useful torque.

**Simulation Tasks**:

1. **Define Positive Torque Windows**
   - Using the best geometry from Priority 1, identify angular ranges where each EML produces clearly positive torque.
   - Create a simple lookup table or rule set for "safe to pulse" windows.

2. **Implement Selective Pulsing**
   - Modify the pulsing model so EMLs are only energized inside positive torque windows.
   - Compare net work per revolution vs always-on or simple timed pulsing.

3. **Phased / Staggered Firing**
   - Test staggering the firing of the 8 (or 16) EMLs instead of firing them all at once.
   - Evaluate torque ripple and net work improvement.

4. **Pulse Skipping Logic**
   - Add simple load or RPM-based pulse skipping.
   - Measure efficiency gain (work per unit energy input).

**Success Criteria for Priority 2**:
- Net work per revolution increases by at least 30–50% compared to non-selective pulsing on the same geometry.
- Clear reduction in energy wasted during negative or marginal torque zones.

## Priority 3: EML Angular Positioning + Basic Stator Flux Control

**Objective**: Optimize where EMLs are placed and how flux is managed in the stator to minimize negative torque contributions.

**Simulation Tasks**:

1. **EML Angular Positioning Sweep**
   - Vary the angular position of the EML units relative to the rotor gradients.
   - Identify placements that maximize time spent in positive torque zones.
   - Avoid positions that create strong negative torque when energized.

2. **Add Basic Stator Flux Barriers**
   - Introduce flux barriers in the stator steel around the EML cores.
   - Test different barrier sizes and locations.
   - Goal: Reduce unwanted flux paths that contribute to pull-back torque.

3. **Magnetic Shunts / Shaped EML Cores**
   - Test simple magnetic shunts or modified EML core shapes that favor forward torque.
   - Measure impact on negative torque regions.

**Success Criteria for Priority 3**:
- Additional 15–30% improvement in net work per revolution when combined with Priorities 1 and 2.
- Clear reduction in negative torque events caused by EML energization.

## Overall Success Targets

| Milestone | Target Net Work per Revolution | Notes |
|-----------|--------------------------------|-------|
| Current (latest) | ~1.39 J | Baseline |
| After Priority 1 | 3–5+ J | Major geometry improvement |
| After Priority 1 + 2 | 5–8+ J | Geometry + smart pulsing |
| After All Three | 8–12+ J | Realistic target before hardware validation |
| Stretch Goal | 15–20+ J | Requires further iteration and possibly 3D effects |

## Integration with Physical Testing

- Use the upcoming single 45° passive torque-angle fixture to validate FEMM predictions at each major milestone.
- If measured data deviates significantly from simulation, pause geometry work and recalibrate the model using real measurements.
- Only proceed to powered EML testing on the fixture after passive data shows clear improvement in negative torque and net work.

## Recommended Workflow

1. Start with Priority 1 (rotor gradient + flux barriers) until negative torque is substantially reduced.
2. Layer Priority 2 (selective pulsing) on top of the improved geometry.
3. Use Priority 3 as refinement while running physical fixture tests.
4. Document every major geometry and pulsing change with torque-angle plots and net work numbers.
5. Feed physical measurement data back into FEMM for model improvement.

**Document Version**: 1.0
**Status**: Ready to begin implementation.
