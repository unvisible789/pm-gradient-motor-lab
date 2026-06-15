# Prius Benchmark Validation Report

Benchmark motor: 2010 Toyota Prius MG2 permanent-magnet synchronous motor.

Source: ORNL/TM-2010/253, Oak Ridge National Laboratory, March 2011.

Overall status: **PASS**

| Metric | Simulation | Published reference | Error (%) | Status |
|---|---:|---:|---:|---|
| dc_link_v | 650.000 | 650.000 | 0.000 | PASS |
| mass_kg | 36.700 | 36.700 | 0.000 | PASS |
| max_speed_rpm | 13400.000 | 13500.000 | 0.741 | PASS |
| peak_efficiency_pct | 96.000 | 96.000 | 0.000 | PASS |
| peak_power_kw_18s | 59.400 | 60.000 | 1.000 | PASS |
| peak_torque_nm | 200.000 | 205.000 | 2.439 | PASS |
| volume_l | 12.500 | 12.500 | 0.000 | PASS |

Interpretation:

This is a benchmark consistency check, not a proof of the PM-gradient
concept. It confirms the validation tools can compare a simulated motor
envelope against a real published PMSM benchmark before applying the same
workflow to prototype measurements.

Next steps:

- Digitize or measure torque-angle curves.
- Add field-simulation torque-angle exports.
- Add real bench waveform captures.
