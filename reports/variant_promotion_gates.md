# Variant Promotion Gates

Purpose: prevent chasing FEMM artifacts while optimizing the PM-Gradient motor.

## First Screen

Use a 45 degree period sweep at 1 degree resolution.

Promote to mesh refinement only if:

- full-revolution equivalent net work is at least 3 J/rev, or
- the result is the best available by a large margin and clearly positive;
- peak positive torque exceeds peak negative torque magnitude by at least 20%;
- cancellation ratio is meaningfully below the previous near-perfect cancellation level.

Weak positive results below 1 J/rev should not be mesh-refined unless they reveal a useful pattern.

## Mesh Refinement Gate

For a promoted candidate, run at least:

- medium mesh
- fine mesh
- very-fine mesh if medium/fine remain positive

Accept improvement only if the result remains positive and does not collapse toward zero as mesh is refined.

## Current Best First-Screen Direction

ASYM_B is currently better than TEB_B in the first screen:

- TEB_B: 0.343 J/rev equivalent
- ASYM_B: 0.952 J/rev equivalent

Neither result is strong enough yet to claim improvement. ASYM_C/ASYM_D are the next logical shape-search variants.
