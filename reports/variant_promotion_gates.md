# Design acceptance criteria

Updated 2026-11-08. These criteria supersede the earlier thresholds that rewarded a positive passive work residual or required shaft work to exceed electrical input. Historical raw runs remain in `data/field_sim`.

## 1. Define the intended machine

Record geometry, materials and temperature-dependent magnetic properties, actual coil turns and resistance, electrical supply, load, speed, thermal environment, current direction, and the complete switching sequence. A steel/copper surrogate is not a calibrated APW permanent electromagnet. A radial 2D model is not a verified double-sided axial motor.

## 2. Validate before ranking geometries

- A complete passive cycle with restored magnetic/material state must converge toward zero net work. Refine mesh, angle spacing and boundaries; cross-check torque against an energy derivative and measured curves. Do not optimize for the largest passive numerical residual.
- Check complete angular coverage and identical state at the endpoints. A partial sweep cannot be scaled to a full turn. An active-control sector cannot be repeated unless currents, magnetization and every channel's phase also repeat.
- Preserve raw curves. Subtracting the mean torque is not a repair of the physical model.
- Record model/configuration hashes, mesh settings, solver version and full-state periodicity with every run. Missing provenance limits comparisons.

## 3. Validate the complete energy balance

Integrate signed electrical power at every source boundary, including returned energy, auxiliary electronics and any external drive. Measure shaft work and the change in flywheel/capacitor/magnetic energy. With measured losses:

`net input = shaft output + losses + stored-energy increase`.

A positive unexplained energy residual is a measurement/model problem to investigate. Mechanical work below electrical input can be a valid motor result; it is not a failure merely because output does not exceed input. Placeholder inductance, assumed recovery and a guessed fraction for copper heating do not establish efficiency.

Passing a powered-motor accounting check does not satisfy the user's net-generation requirement. The proposed permanent-magnet-only closed cycle has no identified continuing energy source. Do not promote an unexplained surplus into a generation claim; identify omitted inputs, storage changes, numerical bias and measurement uncertainty. A practical generator requires an external input source and a complete conversion efficiency measurement.

## 4. Optimize only feasible candidates

Maximize useful continuous shaft power and efficiency subject to winding temperature, magnet demagnetization margin, voltage/current limits, torque ripple, mechanical stress, bearing/grease life, capacitor life, cost and packaging. Report tradeoffs and uncertainty, not a universal maximum.

The powered comparison uses 350 W at 1,000 RPM (3.342 Nm) from an external DC supply. This is only a comparison target, not an achieved rating or a solution to the net-generation requirement. No prototype or endurance data establish this rating yet.

## 5. Hardware qualification

First characterize one magnetic interaction and its real driver. Progress to a guarded full rotor only after electrical, magnetic and mechanical models agree within a documented uncertainty budget. Verify sustained loaded operation and thermal equilibrium; then qualify the required service life under its specified load/environment. A bench run or a bearing fatigue calculation alone does not establish maintenance-free lifetime.

Sources: [MIT energy conversion](https://ocw.mit.edu/courses/6-061-introduction-to-electric-power-systems-spring-2011/c26f6204e05bd4c47875a96452982b6f_MIT6_061S11_ch8.pdf), [FEMM accuracy guidance](https://femm.info/doku/doku.php?id=faq).
