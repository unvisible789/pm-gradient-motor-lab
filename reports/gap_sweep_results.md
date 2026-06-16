# Stator Gap Sweep Results

**Date:** 2026-06-15

**Base:** ASYM_B rotor + EML offset +12°. 45° period, 1° step. First screen only; not mesh-converged.

## Gap Sweep Ranking

| stator_inner_radius_mm | 45° work (J) | Full-rev equiv (J/rev) | Peak + (Nm) | Peak − (Nm) | Pos gross (J) | Neg gross (J) | Cancellation | Closure Δ (Nm) | Decision |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 159.0 | 0.186 | **1.486** | 4.934 | −3.739 | 1.118 | 0.933 | 0.909 | 0.039 | hold |
| 159.5 | 0.104 | 0.834 | 4.558 | −3.812 | 1.057 | 0.952 | 0.948 | 0.123 | weak |
| 160.0 | 0.033 | 0.261 | 4.335 | −3.917 | 0.947 | 0.914 | 0.982 | 0.067 | weak |
| 161.0 | 0.028 | 0.224 | 3.793 | −3.704 | 0.918 | 0.890 | 0.984 | 0.057 | weak |
| 158.5 | 0.013 | 0.101 | 5.920 | −4.300 | 1.152 | 1.139 | 0.994 | −0.002 | weak |

## Interpretation

The sweep shows a **sharp optimum at 159.0 mm**. Moving inward to 158.5 mm collapses net work. Moving outward beyond 159.0 mm degrades quickly.

This confirms the prior +1 mm gap result and does not beat 1.486 J/rev on this first screen.

## Full Ranking (gap sweep + baselines + combos)

| Variant | 45° work (J) | Full-rev equiv (J/rev) | Peak + (Nm) | Peak − (Nm) | Pos gross (J) | Neg gross (J) | Cancellation | Closure Δ (Nm) | Decision |
|---------|---:|---:|---:|---:|---:|---:|---:|---:|---|
| gap 159.0 | 0.186 | **1.486** | 4.934 | −3.739 | 1.118 | 0.933 | 0.909 | 0.039 | hold |
| gap+1mm legacy | 0.186 | 1.486 | 4.934 | −3.739 | 1.118 | 0.933 | 0.909 | 0.039 | hold |
| gap159 + Halbach15 | 0.177 | 1.413 | 6.386 | −5.166 | 1.062 | 0.886 | 0.909 | 0.041 | hold |
| ASYM_B +12° (gap 158) | 0.145 | 1.159 | 4.849 | −3.954 | 1.165 | 1.020 | 0.934 | −0.041 | hold |
| EML arc −20% (standalone) | 0.134 | 1.070 | 3.001 | −1.467 | 0.528 | 0.394 | 0.855 | 0.148 | hold |
| gap159 + arc −10% | 0.112 | 0.897 | 3.711 | −2.462 | 0.761 | 0.649 | 0.921 | 0.114 | weak |
| gap 159.5 | 0.104 | 0.834 | 4.558 | −3.812 | 1.057 | 0.952 | 0.948 | 0.123 | weak |
| gap159 + arc −20% | 0.067 | 0.537 | 2.479 | −1.317 | 0.459 | 0.391 | 0.921 | −0.001 | weak |

## Limited Combinations on Gap 159.0

| Variant | Full-rev equiv (J/rev) | Cancellation | vs gap 159 alone |
|---------|----------------------:|-------------:|------------------|
| gap 159 only | 1.486 | 0.909 | baseline |
| + Halbach 15° | 1.413 | 0.909 | worse |
| + EML arc −10% | 0.897 | 0.921 | worse |
| + EML arc −20% | 0.537 | 0.921 | worse |

No combination improved on gap 159.0 alone in this first screen.

## Mesh Refinement

Not promoted. Result is below 3 J/rev gate and cancellation remains ~0.909.

## Build Recommendation

Unchanged: do not build full motor from this first-screen result.