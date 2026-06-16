# Best-So-Far Tracker

Date: 2026-06-15

## Current Accepted Baseline

Mesh-refined current geometry is near-zero to slightly negative net work. Treat all auto-mesh positive values as untrusted until mesh convergence is shown.

## First-Screen Results

| Variant | Full-rev equivalent | Peak + | Peak - | Decision |
|---|---:|---:|---:|---|
| ASYM_B | 0.952 J/rev | 5.044 Nm | -3.994 Nm | weak positive, do not promote yet |
| TEB_B | 0.343 J/rev | 6.277 Nm | -6.175 Nm | weak positive, do not promote yet |

## What We Learned

ASYM_B is more promising than TEB_B because it improves peak-positive to peak-negative balance. TEB_B still has near-perfect cancellation.

Neither result is close to the 3 J/rev mesh-refinement gate, so the next efficient move is not mesh refinement. The next move is targeted shape search around ASYM_B.

## Next Variants To Run

Run these before any mesh refinement:

1. `asym_c_lead2p5_trail138`
2. `asym_d_lead3p0_trail137`
3. `asym_a_lead1p5_trail142`
4. `teb_c_4deg_130_145`
5. `teb_d_3deg_126_145`

Promote only if the first-screen result is clearly stronger than ASYM_B, preferably above 3 J/rev equivalent or showing much lower cancellation with stronger positive/negative imbalance.
