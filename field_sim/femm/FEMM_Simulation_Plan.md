# Prioritized FEMM Simulation Plan - Reducing Negative Torque (Revised)

**Date of Revision**: 2026-06-15
**Key Finding from Mesh Study**: The previously reported ~1.39 J/rev net work was **not numerically robust**. Under mesh refinement, integrated net work collapses to near zero or slightly negative. This means the current geometry produces severe torque cancellation, and earlier positive values were mesh artifacts.

**New Baseline**: Treat current geometry as producing **near-zero to slightly negative net work per revolution** until proven otherwise with well-converged meshes.

**Goal**: Achieve stable, mesh-converged net work of **8+ J per revolution** (target range 8–20+ J) through systematic geometry and control improvements.

## Important Protocol: Mesh Convergence First

Before claiming any improvement:
- Always run mesh refinement studies (at least 2–3 successively finer meshes) on any new geometry or major change.
- Only accept results as real if net work remains stable (does not collapse) under refinement.
- Document mesh density and convergence behavior for every reported result.

## Revised Priority Order

### Priority 1: Rotor Gradient Shape + Flux Barriers (Most Critical)

**Objective**: Fundamentally redesign the rotor gradients to break the strong return flux paths causing near-total torque cancellation.

**Recommended Changes (in rough order of priority)**:

1. **Introduce substantial flux barriers** between gradients
   - Start with 5–8 mm wide non-magnetic gaps.
   - Extend barriers radially from near the shaft toward the air gap.
   - Test different widths and depths parametrically.

2. **Redesign gradient shape for asymmetry and concentration**
   - Move from simple curved magnets to more concentrated pole arcs.
   - Make leading edge stronger/more pronounced than trailing edge.
   - Test partial Halbach magnetization patterns.

3. **Run full mesh-converged torque-angle sweeps**
   - Use at least 1° or finer angular resolution.
   - Perform mesh refinement studies on promising geometries.
   - Target: Reduce negative torque peak by >50% and achieve stable positive net work >3 J.

**Success Criteria for Priority 1**:
- Mesh-converged net work reaches at least **3–5 J/rev**.
- Negative torque peaks are substantially reduced relative to positive peaks.
- Results remain stable under mesh refinement.

### Priority 2: Selective and Phased EML Pulsing Strategy

**Objective**: Stop wasting energy by pulsing EMLs during negative or marginal torque zones.

**Actions**:

1. Using the best geometry from Priority 1, map angular ranges where each EML produces clearly positive torque.
2. Implement position-based selective pulsing (only fire EMLs in strong positive windows).
3. Add phased/staggered firing across the EML set instead of simultaneous pulsing.
4. Introduce simple pulse-skipping logic based on load or RPM.

**Success Criteria for Priority 2**:
- Additional **30–50%+** improvement in net work on top of the improved geometry from Priority 1.
- Clear reduction in energy spent pulsing during low/negative torque periods.
- Results stable under mesh refinement.

### Priority 3: EML Angular Positioning + Stator Flux Control

**Objective**: Optimize where and how the EMLs interact with the rotor gradients.

**Actions**:

1. Sweep EML angular positions to maximize time spent in positive torque zones.
2. Add stator-side flux barriers around EML cores.
3. Test simple magnetic shunts or shaped EML cores that favor forward torque.

**Success Criteria for Priority 3**:
- Further improvement bringing mesh-converged net work into the **7–10+ J** range when combined with Priorities 1 and 2.

## Overall Milestone Targets

| Milestone | Target Net Work (mesh-converged) | Status |
|-----------|----------------------------------|--------|
| Current baseline (mesh refined) | ~0 to slightly negative         | Known  |
| After Priority 1                | 3–5+ J                         | Target |
| After Priority 1 + 2            | 5–8+ J                         | Target |
| After all three priorities      | 8–12+ J                        | Target |
| Stretch / highly optimized      | 15–20+ J                       | Stretch|

## Integration with Physical Validation

- Do **not** build the 45° torque-angle fixture until simulation shows **clear, mesh-stable positive net work** (minimum 3–4 J with good convergence).
- Once promising simulation results exist, build the fixture and compare measured vs simulated torque-angle curves and integrated work.
- Use physical data to calibrate and improve the FEMM model.
- If measured results deviate significantly from simulation, pause geometry work and refine the model before continuing.

## Recommended Immediate Next Steps

1. Complete the current angular resolution study (2°, 1°, 0.5°, 0.25°).
2. Establish a stable, well-meshed baseline with the current geometry (confirm near-zero/negative result is robust).
3. Begin aggressive Priority 1 work: flux barriers + concentrated/asymmetric gradient shapes.
4. Apply mesh convergence checks to every new geometry variant.
5. Only move to hardware once simulation shows clear, stable improvement.

**Document Version**: 2.0 (Revised after mesh study)
**Status**: Ready for implementation. Focus on establishing mesh-stable positive net work before hardware.