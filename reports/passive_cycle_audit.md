# Passive cycle audit

Date: 2026-11-08

This is a new calculation on the existing CSV files, not a new field solve or a bench test. Raw data are unchanged.

## Results

The last numeric column conditionally repeats a **complete** declared sector through 360 degrees. Sector symmetry and identical geometry/solver provenance are not independently established by these CSVs. These are residuals, not predicted shaft output.

| Stored run | Points | Recorded / declared span | Sampled work (J) | Conditional full-turn residual (J) | Status |
|---|---:|---:|---:|---:|---|
| original full turn | 181 | 360 / 360 deg | 0.92119902 | 0.92119902 | complete; diagnostic only |
| original shaped poles | 46 | 45 / 45 deg | 0.17454524 | 1.39636188 | complete; diagnostic only |
| mesh coarse | 46 | 45 / 45 deg | 0.01533361 | 0.12266888 | complete; diagnostic only |
| mesh medium | 46 | 45 / 45 deg | -0.00031881 | -0.00255051 | complete; diagnostic only |
| mesh fine | 46 | 45 / 45 deg | -0.00621453 | -0.04971628 | complete; diagnostic only |
| mesh very fine | 46 | 45 / 45 deg | -0.00152583 | -0.01220667 | complete; diagnostic only |
| angle 0.25 degrees | 67 | 16.5 / 45 deg | 0.51601244 | not computed | incomplete; cannot extrapolate |
| later coil-off baseline | 46 | 45 / 45 deg | 0.18568850 | 1.48550804 | complete; diagnostic only |

## Engineering interpretation

The mesh-labelled series is much closer to zero than the earlier +1.396 J/rev figure and changes sign. It does not establish a positive passive energy source. Because full run provenance is absent, this is not a certified convergence study and no statistical uncertainty is inferred by pooling unlike runs.

The 0.25-degree file ends at 16.5 degrees. Extrapolating this partial record to a full revolution would manufacture an apparent result. The audit explicitly withholds that number.

Before optimizing the machine or making a net-power claim, validate the passive model against its zero closed-cycle work requirement, torque-angle measurements, mesh/boundary refinement, and a full-state periodicity check. Do not subtract the mean torque and call that a corrected physical model.

## Reproduce

```sh
python validation/passive_cycle_audit.py
```

## Basis

- [MIT electromechanical energy balance](https://ocw.mit.edu/courses/6-061-introduction-to-electric-power-systems-spring-2011/c26f6204e05bd4c47875a96452982b6f_MIT6_061S11_ch8.pdf)
- [FEMM force and torque accuracy guidance](https://femm.info/doku/doku.php?id=faq)
