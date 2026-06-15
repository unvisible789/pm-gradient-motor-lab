#!/usr/bin/env python3
"""
One-channel validation simulation for a PM-gradient assisted motor.

The audit intentionally treats permanent-magnet gradient torque claims
conservatively: mechanical pulse work is only considered energy-balanced when
it is less than or equal to the modeled net electrical energy per pulse, unless
another measured energy source is explicitly provided.

Run:
    python3 torque_energy_audit.py

Outputs:
    simulation_results.csv
    energy_audit_report.md
"""

from __future__ import annotations

import csv
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


# -----------------------------
# Model inputs from the prompt
# -----------------------------
ROTOR_DIAMETER_MM = 300.0
ROTOR_RADIUS_MM = 150.0
GRADIENTS_PER_REVOLUTION = 12
INTERACTION_CHANNELS = 1
TARGET_RPM = 800.0
TIMING_ADVANCE_DEG = 8.0
PULSE_ASSIST_TORQUE_NM = 1.8
PULSE_WINDOWS_DEG = [2.0, 4.0, 8.0, 12.0, 20.0]
NET_ELECTRICAL_ENERGY_PER_PULSE_J = 17.5e-3
FLYBACK_RECOVERY_FRACTION = 0.515
FRICTION_LOAD_TORQUE_NM = 0.8

CSV_PATH = Path("simulation_results.csv")
REPORT_PATH = Path("energy_audit_report.md")


@dataclass(frozen=True)
class AuditRow:
    pulse_window_deg: float
    pulse_window_rad: float
    work_per_pulse_j: float
    mechanical_pulse_power_w: float
    electrical_input_power_w: float
    energy_balance_ratio: float
    required_electrical_energy_per_pulse_j: float
    mechanical_energy_per_revolution_j: float
    net_electrical_energy_per_revolution_j: float
    load_energy_per_revolution_j: float
    status: str


def angular_speed_rad_per_sec(rpm: float) -> float:
    """Convert revolutions per minute to radians per second."""
    return rpm * 2.0 * math.pi / 60.0


def event_frequency_hz(rpm: float, gradients_per_revolution: int) -> float:
    """Gradient encounters per second for one stationary interaction channel."""
    revolutions_per_second = rpm / 60.0
    return revolutions_per_second * gradients_per_revolution * INTERACTION_CHANNELS


def work_per_pulse_j(torque_nm: float, pulse_window_deg: float) -> float:
    """Mechanical work from assumed constant torque over the pulse window."""
    return torque_nm * math.radians(pulse_window_deg)


def classify_balance(work_j: float, electrical_energy_j: float) -> str:
    """Return the conservative audit status for one pulse window."""
    if work_j <= electrical_energy_j:
        return "energy-balanced by modeled electrical input"
    return "unbalanced pending source identification"


def build_rows() -> list[AuditRow]:
    events_per_second = event_frequency_hz(TARGET_RPM, GRADIENTS_PER_REVOLUTION)
    load_energy_per_revolution_j = FRICTION_LOAD_TORQUE_NM * 2.0 * math.pi
    net_electrical_energy_per_revolution_j = (
        NET_ELECTRICAL_ENERGY_PER_PULSE_J * GRADIENTS_PER_REVOLUTION
    )

    rows: list[AuditRow] = []
    for window_deg in PULSE_WINDOWS_DEG:
        window_rad = math.radians(window_deg)
        pulse_work_j = work_per_pulse_j(PULSE_ASSIST_TORQUE_NM, window_deg)
        mechanical_power_w = pulse_work_j * events_per_second
        electrical_power_w = NET_ELECTRICAL_ENERGY_PER_PULSE_J * events_per_second
        ratio = pulse_work_j / NET_ELECTRICAL_ENERGY_PER_PULSE_J
        mechanical_energy_per_revolution_j = pulse_work_j * GRADIENTS_PER_REVOLUTION

        rows.append(
            AuditRow(
                pulse_window_deg=window_deg,
                pulse_window_rad=window_rad,
                work_per_pulse_j=pulse_work_j,
                mechanical_pulse_power_w=mechanical_power_w,
                electrical_input_power_w=electrical_power_w,
                energy_balance_ratio=ratio,
                required_electrical_energy_per_pulse_j=pulse_work_j,
                mechanical_energy_per_revolution_j=mechanical_energy_per_revolution_j,
                net_electrical_energy_per_revolution_j=net_electrical_energy_per_revolution_j,
                load_energy_per_revolution_j=load_energy_per_revolution_j,
                status=classify_balance(
                    pulse_work_j, NET_ELECTRICAL_ENERGY_PER_PULSE_J
                ),
            )
        )
    return rows


def write_csv(rows: Iterable[AuditRow], path: Path = CSV_PATH) -> None:
    fieldnames = [
        "pulse_window_deg",
        "pulse_window_rad",
        "work_per_pulse_j",
        "mechanical_pulse_power_w",
        "electrical_input_power_w",
        "energy_balance_ratio",
        "required_electrical_energy_per_pulse_j",
        "mechanical_energy_per_revolution_j",
        "net_electrical_energy_per_revolution_j",
        "load_energy_per_revolution_j",
        "status",
    ]
    with path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({name: getattr(row, name) for name in fieldnames})


def fmt(value: float, digits: int = 6) -> str:
    """Compact numeric formatting for markdown tables."""
    return f"{value:.{digits}f}"


def write_report(rows: list[AuditRow], path: Path = REPORT_PATH) -> None:
    omega = angular_speed_rad_per_sec(TARGET_RPM)
    gradients_hz = event_frequency_hz(TARGET_RPM, GRADIENTS_PER_REVOLUTION)
    pulse_events_per_second = gradients_hz
    electrical_power_w = NET_ELECTRICAL_ENERGY_PER_PULSE_J * pulse_events_per_second
    load_power_w = FRICTION_LOAD_TORQUE_NM * omega
    load_energy_per_revolution_j = FRICTION_LOAD_TORQUE_NM * 2.0 * math.pi
    gross_pulse_energy_before_recovery_j = NET_ELECTRICAL_ENERGY_PER_PULSE_J / (
        1.0 - FLYBACK_RECOVERY_FRACTION
    )
    recovered_energy_per_pulse_j = (
        gross_pulse_energy_before_recovery_j * FLYBACK_RECOVERY_FRACTION
    )

    table_lines = [
        "| Pulse window (deg) | Work/pulse (J) | Mechanical pulse power (W) | Electrical input power (W) | Energy balance ratio | Required electrical energy/pulse for 100% (J) | Per-rev pulse mechanical energy (J) | Status |",
        "|---:|---:|---:|---:|---:|---:|---:|---|",
    ]
    for row in rows:
        table_lines.append(
            "| "
            f"{fmt(row.pulse_window_deg, 1)} | "
            f"{fmt(row.work_per_pulse_j)} | "
            f"{fmt(row.mechanical_pulse_power_w)} | "
            f"{fmt(row.electrical_input_power_w)} | "
            f"{fmt(row.energy_balance_ratio, 3)} | "
            f"{fmt(row.required_electrical_energy_per_pulse_j)} | "
            f"{fmt(row.mechanical_energy_per_revolution_j)} | "
            f"{row.status} |"
        )

    report = f"""# One-Channel PM-Gradient Assisted Motor Energy Audit

## Purpose

This validation simulation audits one stationary EML50mm-24 interaction channel over one full rotor revolution. It does **not** assume permanent magnets provide free continuous net torque. Any case where modeled mechanical pulse work exceeds the measured net electrical pulse input is flagged as **unbalanced pending source identification**.

## Model Inputs

- Rotor diameter: {ROTOR_DIAMETER_MM:.1f} mm
- Rotor radius: {ROTOR_RADIUS_MM:.1f} mm
- Magnetic gradients per revolution: {GRADIENTS_PER_REVOLUTION}
- Stationary interaction channels: {INTERACTION_CHANNELS}
- Target speed: {TARGET_RPM:.1f} RPM
- Timing advance: {TIMING_ADVANCE_DEG:.1f} degrees
- Pulse assist torque assumption: {PULSE_ASSIST_TORQUE_NM:.3f} Nm
- Pulse windows tested: {', '.join(f'{w:g}°' for w in PULSE_WINDOWS_DEG)}
- Net electrical energy per pulse: {NET_ELECTRICAL_ENERGY_PER_PULSE_J:.6f} J ({NET_ELECTRICAL_ENERGY_PER_PULSE_J * 1000:.1f} mJ)
- Flyback recovery: {FLYBACK_RECOVERY_FRACTION * 100:.1f}%
- Friction/load torque: {FRICTION_LOAD_TORQUE_NM:.3f} Nm

## Equations

1. Angular speed: `omega = RPM * 2*pi / 60`
2. Gradient event frequency: `f_gradient = gradients_per_revolution * RPM / 60`
3. Pulse events per second, one channel: `f_pulse = f_gradient * channels`
4. Pulse window radians: `theta = pulse_window_deg * pi / 180`
5. Work per pulse: `W_pulse = torque * theta`
6. Mechanical pulse power: `P_mech_pulse = W_pulse * f_pulse`
7. Electrical input power: `P_elec = net_electrical_energy_per_pulse * f_pulse`
8. Energy balance ratio: `ratio = W_pulse / net_electrical_energy_per_pulse`
9. Required electrical pulse energy for 100% balance: `E_required_100pct = W_pulse`
10. Load energy per revolution: `E_load_rev = load_torque * 2*pi`

## Baseline Results

- Angular speed: **{omega:.6f} rad/s**
- Gradient event frequency: **{gradients_hz:.6f} Hz**
- Pulse events per second: **{pulse_events_per_second:.6f} pulses/s**
- Net electrical input power: **{electrical_power_w:.6f} W**
- Gross pulse energy before 51.5% flyback recovery, inferred from the stated net value: **{gross_pulse_energy_before_recovery_j:.6f} J/pulse**
- Recovered flyback energy, inferred: **{recovered_energy_per_pulse_j:.6f} J/pulse**
- Friction/load power at target speed: **{load_power_w:.6f} W**
- Friction/load energy per revolution: **{load_energy_per_revolution_j:.6f} J/rev**
- Net electrical pulse energy per revolution: **{NET_ELECTRICAL_ENERGY_PER_PULSE_J * GRADIENTS_PER_REVOLUTION:.6f} J/rev**

## Numerical Results Table

{chr(10).join(table_lines)}

## Energy-Balance Decision

All tested pulse windows produce mechanical pulse work greater than the stated net electrical pulse input of {NET_ELECTRICAL_ENERGY_PER_PULSE_J:.6f} J. Under this audit rule, none of the tested pulse windows can be called energy-balanced unless an additional measured source of energy is added to the model.

## Physical Interpretation

The pulse torque assumption creates mechanical work equal to torque integrated over angle. For the smallest tested pulse window, 2°, the modeled work is already above the stated net electrical input per pulse. Wider pulse windows increase the imbalance linearly because the torque assumption is held constant while the energized angular interval grows.

A permanent-magnet gradient can redistribute stored magnetic field energy and can exchange energy with the rotor and coil, but this simulation does not include a measured source capable of supplying the excess continuous net work. Therefore, any apparent output above electrical input is not treated as success; it is classified as **unbalanced pending source identification**.

The friction/load requirement is also significant: {FRICTION_LOAD_TORQUE_NM:.3f} Nm at {TARGET_RPM:.1f} RPM corresponds to {load_power_w:.6f} W. The stated net pulse electrical input is only {electrical_power_w:.6f} W, so sustaining the specified load at speed requires either substantially more electrical energy, a verified external/mechanical energy source, or a corrected torque/window assumption.

## Next Data Needed From Prototype

- Direct torque-vs-angle measurements through each gradient, including attraction and exit/drag regions.
- Coil voltage and current waveforms at high sample rate for every pulse, including flyback path measurements.
- Rotor speed before and after each pulse to derive kinetic-energy change independently.
- Load torque calibration and bearing/friction characterization across speed.
- Magnetic force mapping over a full 360° revolution to prove that positive and negative gradient regions are balanced or to identify a real stored-energy source.
- Thermal measurements of coil, driver, magnets, bearings, and load to close the energy budget.
- Repeatability data across many revolutions to distinguish transient stored-energy release from continuous operation.

## Output Files

- `simulation_results.csv`
- `energy_audit_report.md`
- `torque_energy_audit.py`
"""
    path.write_text(report, encoding="utf-8")


def main() -> None:
    rows = build_rows()
    write_csv(rows)
    write_report(rows)
    print(f"Wrote {CSV_PATH}")
    print(f"Wrote {REPORT_PATH}")


if __name__ == "__main__":
    main()
