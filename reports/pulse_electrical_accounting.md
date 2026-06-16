# Pulse Electrical Accounting

**Date:** 2026-06-15

First-order accounting with **placeholder** coil values. Not measured L/R.

## Placeholder Assumptions

| Parameter | Value | Note |
|---|---:|---|
| Coil inductance L | 5.000 mH | PLACEHOLDER |
| Flyback recovery | 0.750 | PLACEHOLDER |
| Copper loss fraction of 0.5 L I^2 | 0.050 | PLACEHOLDER |
| Switching loss per effective pulse | 0.000200 J | PLACEHOLDER |
| EML count | 8 | from geometry |
| Current levels (mA/mm^2) | low=5, medium=10, high=20 | mapped via coil area |

## Current Levels (from geometry)

| Level | Density (mA/mm^2) | Current (A) |
|---|---:|---:|
| low | 5.0 | 3.6689 |
| medium | 10.0 | 7.3377 |
| high | 20.0 | 14.6754 |

## Energy Balance vs Coil-Off Baseline (1.485508 J/rev)

| Case | Added mech (J/rev) | Unrecovered input (J/rev) | Copper loss (J/rev) | Switching loss (J/rev) | Total input (J/rev) | Net added after input (J/rev) | Closes? |
|---|---:|---:|---:|---:|---:|---:|---|
| low | -0.037641 | 0.287158 | 0.057432 | 0.006827 | 0.351416 | -0.389057 | no |
| medium | -0.039274 | 1.148630 | 0.229726 | 0.006827 | 1.385183 | -1.424457 | no |
| high | 0.046917 | 4.594520 | 0.918904 | 0.006827 | 5.520251 | -5.473334 | no |

## Interpretation

- Stored energy per pulse uses 0.5 L I^2 with placeholder L.
- Unrecovered input is stored energy times (1 - recovery efficiency), scaled by effective pulsed angles.
- Added mechanical work is coil-on full-rev equivalent minus coil-off baseline.
- **Do not claim improvement** unless net added work after input is positive and lockout braking did not worsen.

Replace placeholder L, R, recovery, and switching loss with measured values before design decisions.
