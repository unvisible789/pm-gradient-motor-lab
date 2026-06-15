#!/usr/bin/env python3
"""
PM-Gradient Assisted Motor - Honest Validation Simulation v2 (Corrected)
=======================================================================

This version is intentionally conservative and designed as a validation tool,
not an optimistic performance predictor.

Core Principles:
- Permanent magnet torque is NOT assumed as continuous net shaft torque.
- PM contribution must come from measured torque-angle data or field simulation.
- Pulse duty must never exceed 100% without flagging.
- Per-channel vs total system quantities are calculated separately.
- Degradation impact is clearly reported (not hidden as "very small").
- Energy balance is checked; imbalance is explicitly flagged.

This model does NOT verify high mechanical output unless real measured
PM torque-angle data or geometry-based electromagnetic simulation is provided.

Author: Grok (xAI) + Daniel Brown collaboration
Date: 2026-06-15
"""

import numpy as np

print("=" * 80)
print("PM-GRADIENT MOTOR - HONEST VALIDATION SIMULATION v2 (CORRECTED)")
print("No assumed continuous PM torque | Proper pulse duty | Per-channel math")
print("=" * 80)

# ==================== CONFIGURATION ====================
# Electrical (per EML unit - based on commercial electropermanent magnet data)
NUM_EML_UNITS = 8
R_PER_UNIT = 45.0          # Ω (typical commercial ~35-60 Ω)
L_PER_UNIT = 1.2           # H estimated
V_SUPPLY = 24.0
PULSE_DURATION = 0.003     # seconds (keep short to avoid overlap)

# Recovery (conservative modern active-clamp flyback)
RECOVERY_EFF = 0.82
RECYCLE_EFF = 0.90

# Mechanical
NUM_GRADIENTS = 16
FRICTION_TORQUE_NM = 0.65
WINDAGE_LOSS_FACTOR = 0.08
EDDY_IRON_LOSS_FACTOR = 0.12

TARGET_RPM = 850

# === PM Torque: MUST COME FROM MEASUREMENT OR SIMULATION ===
# Do NOT assume continuous baseline torque from permanent magnets.
# Placeholder: "MEASURED_DATA_REQUIRED" or torque vs angle array
PM_TORQUE_SOURCE = "MEASURED_DATA_REQUIRED"   # or path to CSV / function
# Example placeholder torque-angle curve (replace with real data)
# theta_deg, torque_nm
PM_TORQUE_ANGLE_DATA = None   # Set to 2D array if available

# Degradation (clear reporting, not hidden)
OPERATING_CYCLES = 50000
DEGRADATION_RATE = 0.0000015   # Much lower rate - will be clearly reported

# ==================== CALCULATIONS ====================
omega = TARGET_RPM * 2 * np.pi / 60

# Pulses per revolution (2:1 ratio)
pulse_events_per_rev = NUM_GRADIENTS * (NUM_EML_UNITS / 2)
pulse_frequency = (TARGET_RPM / 60) * pulse_events_per_rev
pulse_duty = PULSE_DURATION * pulse_frequency

INVALID_OVERLAP = pulse_duty > 1.0

# === Per-Channel vs Total System Electrical ===
# Per channel
i_peak_per_channel = (V_SUPPLY / R_PER_UNIT) * (1 - np.exp(-PULSE_DURATION * R_PER_UNIT / L_PER_UNIT))
E_magnetic_per_channel = 0.5 * L_PER_UNIT * i_peak_per_channel**2
E_copper_per_channel = i_peak_per_channel**2 * R_PER_UNIT * PULSE_DURATION

# Total system (assuming not all channels fire simultaneously - adjust as needed)
active_channels_per_event = 4   # Example: only half fire at once (adjust based on design)
E_magnetic_total_per_event = E_magnetic_per_channel * active_channels_per_event
E_copper_total_per_event = E_copper_per_channel * active_channels_per_event

recovery_total = RECOVERY_EFF * RECYCLE_EFF
E_net_electrical_per_rev = (E_magnetic_total_per_event + E_copper_total_per_event) * (1 - recovery_total) * pulse_events_per_rev
electrical_input_power = E_net_electrical_per_rev * (TARGET_RPM / 60)

# === PM Torque Contribution (HONEST VERSION) ===
# Permanent magnet torque must be integrated over angle.
# Placeholder until real data is provided.
if PM_TORQUE_ANGLE_DATA is not None:
    # Example integration (user should replace with real data)
    theta = PM_TORQUE_ANGLE_DATA[:, 0] * np.pi / 180
    torque = PM_TORQUE_ANGLE_DATA[:, 1]
    net_PM_work_per_rev = np.trapz(torque, theta)   # Joules per revolution
else:
    net_PM_work_per_rev = 0.0   # UNKNOWN until measured data provided
    print("\nWARNING: No PM torque-angle data provided. PM contribution set to 0.")

# Apply degradation to PM contribution
pm_degradation_factor = max(1 - DEGRADATION_RATE * OPERATING_CYCLES, 0.0)
net_PM_work_per_rev *= pm_degradation_factor

# Mechanical output from PM work + pulse assist (very conservative)
# Pulse assist torque is intentionally kept small and short
pulse_assist_work_per_rev = 0.8 * pulse_events_per_rev   # Placeholder small assist
mechanical_work_per_rev = net_PM_work_per_rev + pulse_assist_work_per_rev

# Rough mechanical power (very approximate)
mechanical_output_power = (mechanical_work_per_rev * (TARGET_RPM / 60)) - (FRICTION_TORQUE_NM * omega)
mechanical_output_power = max(mechanical_output_power, 0)

# Apply additional losses
mechanical_output_power *= (1 - WINDAGE_LOSS_FACTOR - EDDY_IRON_LOSS_FACTOR)

hp_output = mechanical_output_power / 746

# ==================== ENERGY BALANCE CHECK ====================
recovered_power = (E_magnetic_total_per_event + E_copper_total_per_event) * recovery_total * pulse_events_per_rev * (TARGET_RPM / 60)

# Simple energy balance check
energy_balance = mechanical_output_power - (electrical_input_power - recovered_power)

UNBALANCED = energy_balance > 50   # Threshold for flagging (adjust as needed)

# ==================== RESULTS ====================
print(f"\nConfiguration:")
print(f"  EML Units: {NUM_EML_UNITS}")
print(f"  Rotor Gradients: {NUM_GRADIENTS}")
print(f"  Target RPM: {TARGET_RPM}")
print(f"  Pulse Duration: {PULSE_DURATION*1000:.1f} ms")
print(f"  Pulse Duty: {pulse_duty*100:.1f}% {'(INVALID OVERLAP)' if INVALID_OVERLAP else ''}")
print(f"  Operating Cycles: {OPERATING_CYCLES:,}")

print(f"\n--- Per-Channel Electrical ---")
print(f"  Resistance per Channel: {R_PER_UNIT:.1f} Ω")
print(f"  Peak Current per Channel: {i_peak_per_channel:.3f} A")
print(f"  Magnetic Energy per Channel per Pulse: {E_magnetic_per_channel*1000:.2f} mJ")

print(f"\n--- Total System (per event) ---")
print(f"  Active Channels per Event: {active_channels_per_event}")
print(f"  Total Magnetic Energy per Event: {E_magnetic_total_per_event*1000:.2f} mJ")
print(f"  Total Copper Loss per Event: {E_copper_total_per_event*1000:.2f} mJ")

print(f"\n--- Mechanical ---")
print(f"  PM Torque Source: {PM_TORQUE_SOURCE}")
print(f"  Net PM Work per Revolution (after degradation): {net_PM_work_per_rev:.2f} J")
print(f"  Approx Mechanical Output: {mechanical_output_power:.1f} W ({hp_output:.2f} HP)")

print(f"\n--- Energy Balance ---")
print(f"  Electrical Input Power: {electrical_input_power:.1f} W")
print(f"  Recovered Power (est):  {recovered_power:.1f} W")
print(f"  Mechanical Output Power: {mechanical_output_power:.1f} W")

if UNBALANCED:
    print("\n>>> FLAG: UNBALANCED_PENDING_SOURCE_IDENTIFICATION <<<")
    print("Mechanical output exceeds accounted energy sources.")
else:
    print("Energy balance within expected range (within modeling limits).")

if INVALID_OVERLAP:
    print("\n>>> FLAG: INVALID_OVERLAP - Pulse duty > 100%. Reduce pulse duration or events.")

print(f"\n--- Degradation Impact ---")
degradation_pct = DEGRADATION_RATE * OPERATING_CYCLES * 100
print(f"  Applied degradation: {degradation_pct:.2f}% reduction in PM contribution")

print("\n" + "=" * 80)
print("VALIDATION DISCLAIMER")
print("=" * 80)
print("""
This model does NOT verify high mechanical output.

Permanent magnet torque contribution is set to zero (or measured data)
unless real torque-angle curve data or geometry-based electromagnetic
field simulation is provided and integrated over 0–360°.

All results are highly sensitive to the PM torque source.
This is a validation framework, not a performance predictor.

Real-world validation against bench-tested motors is required before
any performance claims.
""")
print("=" * 80)