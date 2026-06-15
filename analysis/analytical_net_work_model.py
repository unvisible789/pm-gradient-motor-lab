#!/usr/bin/env python3
"""
Simplified Analytical Model for Net Work per Revolution
PM-Gradient Motor Concept

Purpose:
- Quick mathematical estimates of net mechanical work per revolution
- Sanity checking against FEMM results
- Rapid 'what-if' analysis on key parameters
- Guiding FEMM simulation priorities

This is a simplified energy-based model. It is NOT a replacement for FEMM,
but it is useful for understanding scaling and estimating what net work
should be if torque cancellation is reduced.

Core Equation (simplified):
    W_net ≈ W_PM + N_pulses * E_pulse_net * (1 - f_neg) - Losses

Where:
    W_PM          = Baseline work from permanent magnet gradients alone
    N_pulses      = Total EML pulses per revolution
    E_pulse_net   = Net energy delivered per pulse after recovery
    f_neg         = Fraction of rotation in negative/marginal torque zones
    Losses        = Total losses per revolution (mechanical + magnetic + electrical)

Author: Grok-assisted analysis
Date: 2026-06-15
"""

def calculate_net_work(
    W_PM=3.0,           # Baseline PM work per revolution (J)
    N_pulses=16,        # Total pulses per revolution (e.g. 16 for double-sided)
    E_pulse_net=0.010,  # Net energy per pulse after recovery (J) = 10 mJ
    f_neg=0.25,         # Fraction of rotation in negative torque zones
    losses_fraction=0.15  # Total losses as fraction of gross work
):
    """
    Calculate estimated net mechanical work per revolution.

    Returns:
        W_net (float): Estimated net work per revolution in Joules
    """
    gross_work = W_PM + N_pulses * E_pulse_net * (1 - f_neg)
    W_net = gross_work * (1 - losses_fraction)
    return W_net


def print_scenario(name, **kwargs):
    W_net = calculate_net_work(**kwargs)
    print(f"{name:30} -> Net Work: {W_net:.2f} J/rev")


if __name__ == "__main__":
    print("=== Analytical Net Work Estimates ===\n")

    # Current / near-baseline (high negative torque fraction)
    print_scenario("Current (high cancellation)", 
                   W_PM=2.5, N_pulses=16, E_pulse_net=0.010, f_neg=0.45, losses_fraction=0.20)

    # Moderate improvement
    print_scenario("Moderate improvement", 
                   W_PM=3.0, N_pulses=16, E_pulse_net=0.010, f_neg=0.25, losses_fraction=0.18)

    # Good improvement (target zone)
    print_scenario("Good improvement (target)", 
                   W_PM=3.5, N_pulses=16, E_pulse_net=0.011, f_neg=0.15, losses_fraction=0.15)

    # Strong improvement
    print_scenario("Strong improvement", 
                   W_PM=4.0, N_pulses=16, E_pulse_net=0.012, f_neg=0.08, losses_fraction=0.12)

    # Excellent / Stretch
    print_scenario("Excellent execution (stretch)", 
                   W_PM=4.5, N_pulses=16, E_pulse_net=0.013, f_neg=0.05, losses_fraction=0.10)

    print("\n=== Sensitivity Examples ===")

    # What if we halve the negative torque fraction?
    print_scenario("Halve negative fraction", 
                   W_PM=3.5, N_pulses=16, E_pulse_net=0.011, f_neg=0.075, losses_fraction=0.15)

    # What if we improve pulse energy by 20%?
    print_scenario("+20% pulse energy", 
                   W_PM=3.5, N_pulses=16, E_pulse_net=0.0132, f_neg=0.15, losses_fraction=0.15)

    print("\nNote: These are simplified estimates. Use FEMM for detailed geometry work.")
    print("Focus on reducing f_neg (negative torque fraction) for biggest gains.")