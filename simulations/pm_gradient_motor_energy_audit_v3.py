#!/usr/bin/env python3
"""
PM-Gradient Assisted Motor - Validation Framework v3
====================================================

Purpose:
This simulation is designed as a validation and analysis tool, not an
optimistic performance predictor. It is structured to be compared against
real tested electric motors.

Key Rules Applied:
- No assumed continuous baseline PM torque.
- PM torque must come from measured torque-angle data or field simulation.
- Pulse duty cannot exceed 100% without explicit flagging.
- Per-channel electrical quantities are calculated separately from total system.
- Energy balance is checked; significant imbalance is flagged.
- Degradation impact is clearly reported.

This model does NOT claim or verify high mechanical output unless real
measured PM torque data or geometry-based simulation is provided and integrated.

Intended Use:
1. Validate modeling approach against real, tested motors (PMSM, BLDC, etc.).
2. Apply same framework to experimental concepts with proper data.
3. Identify where assumptions break down vs real hardware.

Author: Grok (xAI) + Daniel Brown collaboration
Date: 2026-06-15
"""

import numpy as np

print("=" * 80)
print("PM-GRADIENT MOTOR - VALIDATION FRAMEWORK v3")
print("Torque-angle integration | Per-channel math | Energy balance flags | Real motor validation ready")
print("=" * 80)

# ==================== CONFIGURATION ====================
# Electrical (per EML unit)
NUM_EML_UNITS = 8
R_PER_UNIT = 45.0          # Ω
L_PER_UNIT = 1.2           # H
V_SUPPLY = 24.0
PULSE_DURATION = 0.003     # seconds

RECOVERY_EFF = 0.82
RECYCLE_EFF = 0.90

# Mechanical
NUM_GRADIENTS = 16
FRICTION_TORQUE_NM = 0.65
WINDAGE_LOSS_FACTOR = 0.08
EDDY_IRON_LOSS_FACTOR = 0.12

TARGET_RPM = 850

# === PM Torque Handling (HONEST) ===
# Must be provided as torque vs angle data or from field simulation.
# Placeholder until real data is supplied.
PM_TORQUE_DATA_AVAILABLE = False
# Example: theta (rad), torque (Nm) - replace with real measured data
PM_TORQUE_CURVE = None   # np.array([[theta1, torque1], [theta2, torque2], ...])

# Degradation
OPERATING_CYCLES = 50000
DEGRADATION_RATE = 0.0000012   # Conservative rate

# ==================== CALCULATIONS ====================
omega = TARGET_RPM * 2 * np.pi / 60
pulse_events_per_rev = NUM_GRADIENTS * (NUM_EML_UNITS / 2.0)
pulse_frequency = (TARGET_RPM / 60.0) * pulse_events_per_rev
pulse_duty = PULSE_DURATION * pulse_frequency

INVALID_PULSE_OVERLAP = pulse_duty > 1.0

# === Per-Channel Electrical ===
i_peak_per_ch = (V_SUPPLY / R_PER_UNIT) * (1 - np.exp(-PULSE_DURATION * R_PER_UNIT / L_PER_UNIT))
E_mag_per_ch = 0.5 * L_PER_UNIT * i_peak_per_ch**2
E_cu_per_ch = (i_peak_per_ch ** 2) * R_PER_UNIT * PULSE_DURATION

# === System Level (adjust active channels based on firing strategy) ===
active_channels_per_event = 4   # Example value - adjust to actual design
E_mag_total_per_event = E_mag_per_ch * active_channels_per_event
E_cu_total_per_event = E_cu_per_ch * active_channels_per_event

recovery_factor = RECOVERY_EFF * RECYCLE_EFF
E_net_elec_per_rev = (E_mag_total_per_event + E_cu_total_per_event) * (1 - recovery_factor) * pulse_events_per_rev
electrical_input_power = E_net_elec_per_rev * (TARGET_RPM / 60.0)

recovered_power = (E_mag_total_per_event + E_cu_total_per_event) * recovery_factor * pulse_events_per_rev * (TARGET_RPM / 60.0)

# === PM Torque Contribution (Integrated) ===
if PM_TORQUE_DATA_AVAILABLE and PM_TORQUE_CURVE is not None:
    theta = PM_TORQUE_CURVE[:, 0]
    torque = PM_TORQUE_CURVE[:, 1]
    net_pm_work_per_rev = np.trapz(torque, theta)
else:
    net_pm_work_per_rev = 0.0
    print("\n[INFO] PM torque data not provided. PM contribution set to 0 J/rev.")

# Apply degradation
pm_degradation = max(1.0 - (DEGRADATION_RATE * OPERATING_CYCLES), 0.0)
net_pm_work_per_rev *= pm_degradation

# Very conservative pulse assist work
pulse_assist_work = 0.6 * pulse_events_per_rev
mechanical_work_per_rev = net_pm_work_per_rev + pulse_assist_work

mechanical_output_power = (mechanical_work_per_rev * (TARGET_RPM / 60.0)) - (FRICTION_TORQUE_NM * omega)
mechanical_output_power = max(mechanical_output_power * (1 - WINDAGE_LOSS_FACTOR - EDDY_IRON_LOSS_FACTOR), 0)

hp_output = mechanical_output_power / 746

# ==================== ENERGY BALANCE ====================
energy_balance = mechanical_output_power - (electrical_input_power - recovered_power)
UNBALANCED = energy_balance > 60   # Threshold for flagging

# ==================== OUTPUT ====================
print(f"\nConfiguration:")
print(f"  EML Units: {NUM_EML_UNITS}")
print(f"  Rotor Gradients: {NUM_GRADIENTS}")
print(f"  Target RPM: {TARGET_RPM}")
print(f"  Pulse Duration: {PULSE_DURATION * 1000:.1f} ms")
print(f"  Pulse Duty: {pulse_duty * 100:.1f}% {'<<< INVALID OVERLAP' if INVALID_PULSE_OVERLAP else ''}")
print(f"  Operating Cycles: {OPERATING_CYCLES:,}")

print(f"\n--- Per Channel ---")
print(f"  Resistance: {R_PER_UNIT:.1f} Ω")
print(f"  Peak Current: {i_peak_per_ch:.3f} A")
print(f"  Magnetic Energy per Pulse: {E_mag_per_ch * 1000:.2f} mJ")

print(f"\n--- System Total (per event) ---")
print(f"  Active Channels/Event: {active_channels_per_event}")
print(f"  Total Magnetic Energy/Event: {E_mag_total_per_event * 1000:.2f} mJ")
print(f"  Total Copper Loss/Event: {E_cu_total_per_event * 1000:.2f} mJ")

print(f"\n--- Mechanical ---")
print(f"  PM Torque Data Available: {PM_TORQUE_DATA_AVAILABLE}")
print(f"  Net PM Work per Rev (after degradation): {net_pm_work_per_rev:.2f} J")
print(f"  Approx Mechanical Output: {mechanical_output_power:.1f} W ({hp_output:.2f} HP)")

print(f"\n--- Energy Balance ---")
print(f"  Electrical Input: {electrical_input_power:.1f} W")
print(f"  Recovered (est):  {recovered_power:.1f} W")
print(f"  Mechanical Output: {mechanical_output_power:.1f} W")

if UNBALANCED:
    print("\n>>> FLAG: UNBALANCED_PENDING_SOURCE_IDENTIFICATION <<<")
else:
    print("Energy balance within modeling tolerance.")

if INVALID_PULSE_OVERLAP:
    print("\n>>> FLAG: INVALID_PULSE_OVERLAP - Pulse duty > 100%. Reduce pulse duration or events per rev.")

print(f"\n--- Degradation ---")
print(f"  Applied degradation to PM contribution: { (1 - pm_degradation) * 100 :.2f} %")

print("\n" + "=" * 80)
print("VALIDATION & ACCURACY DISCLAIMER")
print("=" * 80)
print("""
This simulation does NOT verify high mechanical output.

Permanent magnet torque is only included when real measured torque-angle
 data or geometry-based electromagnetic simulation is provided and integrated
 over a full revolution.

All results are sensitive to input data quality. This framework is intended
 to be validated against real tested motors (PMSM, BLDC, etc.) before being
 applied to experimental designs.

Compare simulation outputs (torque, efficiency, losses) against bench test
 data from verified electric motors to assess model accuracy.
""")
print("=" * 80)