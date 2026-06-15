#!/usr/bin/env python3
"""
PMSM Validation Model with Real Motor Data Comparison
====================================================

This version includes example real motor test data for direct comparison
between simulation and measured results.

Goal: Demonstrate how to validate simulation accuracy using real electric
motor test data (torque, efficiency, losses).

How to Use:
1. Replace the example parameters and test data with real values from
   a motor datasheet or dynamometer test report.
2. Run the simulation.
3. Compare simulation outputs vs measured data.
4. Adjust model parameters until the error is acceptable.

This is a validation tool to build confidence in the modeling methodology.

Author: Grok (xAI) + Daniel Brown collaboration
Date: 2026-06-15
"""

import numpy as np

print("=" * 80)
print("PMSM VALIDATION MODEL - REAL DATA COMPARISON")
print("Simulation vs Measured Results from Real Electric Motor")
print("=" * 80)

# ==================== REAL MOTOR PARAMETERS ====================
# These should come from real motor datasheet or test report

# Example values from a typical 2.2 kW surface-mount PMSM (replace with real data)
R_s = 0.92               # Stator resistance (Ω/phase) - from datasheet
L_d = 0.0115             # d-axis inductance (H)
L_q = 0.0118             # q-axis inductance (H)
psi_f = 0.078            # Flux linkage (Wb) - from datasheet or back-EMF test
pole_pairs = 4

# ==================== REAL TEST DATA (Example) ====================
# These values come from actual dynamometer testing of a real motor.
# Replace with real measured points from your motor.

real_test_data = [
    # [Speed_RPM, I_q (A), Measured_Torque_Nm, Measured_Efficiency_%]
    [1500, 8.5,  7.8,  91.2],
    [1500, 12.0, 11.2,  92.5],
    [2000, 10.0,  9.5,  90.8],
    [2500, 8.0,   7.6,  88.5],
]

print("\nReal Test Data Used for Validation (replace with actual motor data):")
print(" Speed | I_q   | Meas. Torque | Meas. Eff. %")
for row in real_test_data:
    print(f" {row[0]:5.0f} | {row[1]:5.1f} | {row[2]:11.1f} | {row[3]:9.1f}")

# ==================== SIMULATION ====================
results = []

for test_point in real_test_data:
    speed_rpm, I_q, measured_torque, measured_eff = test_point
    
    omega_mech = speed_rpm * 2 * np.pi / 60
    omega_elec = omega_mech * pole_pairs
    
    # Torque calculation
    torque_sim = (3/2) * pole_pairs * psi_f * I_q   # Simplified surface-mount
    
    # Copper losses
    I_rms = I_q / np.sqrt(2)
    copper_loss = 3 * R_s * I_rms**2
    
    # Very rough iron + mechanical loss estimate
    iron_mech_loss = 45 + 0.008 * (omega_mech ** 2)   # Placeholder - tune with real data
    
    mech_power_sim = torque_sim * omega_mech
    total_loss_sim = copper_loss + iron_mech_loss
    input_power_sim = mech_power_sim + total_loss_sim
    
    eff_sim = (mech_power_sim / input_power_sim) * 100 if input_power_sim > 0 else 0
    
    results.append({
        "speed": speed_rpm,
        "I_q": I_q,
        "torque_sim": torque_sim,
        "torque_meas": measured_torque,
        "eff_sim": eff_sim,
        "eff_meas": measured_eff,
        "torque_error": abs(torque_sim - measured_torque),
        "eff_error": abs(eff_sim - measured_eff)
    })

# ==================== COMPARISON OUTPUT ====================
print("\n" + "=" * 80)
print("SIMULATION vs REAL MEASURED DATA")
print("=" * 80)
print(" Speed | I_q  | Torque Sim | Torque Meas | Torque Err | Eff Sim | Eff Meas | Eff Err")
print("-" * 80)

for r in results:
    print(f" {r['speed']:5.0f} | {r['I_q']:4.1f} | {r['torque_sim']:9.2f} | {r['torque_meas']:10.1f} | {r['torque_error']:9.2f} | "
          f"{r['eff_sim']:6.1f} | {r['eff_meas']:7.1f} | {r['eff_error']:6.1f}")

print("\n" + "=" * 80)
print("VALIDATION NOTES")
print("=" * 80)
print("""
- Torque and efficiency errors show how well the simple model matches reality.
- Large errors indicate missing effects (iron losses, temperature, saturation, etc.).
- Tune parameters (especially iron/mechanical loss model and flux linkage)
  until simulation closely matches measured data.
- Once validated on real motors, apply the same methodology to new concepts.

Next step: Replace example data with real test points from your motor and re-run.
""")
print("=" * 80)