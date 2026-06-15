#!/usr/bin/env python3
"""
Parameter sweep for the one-channel PM-gradient assisted motor energy audit.

This is an audit tool only. It does not claim success, overunity, or a
breakthrough. It flags each parameter combination by comparing modeled
mechanical pulse work against the stated net electrical energy per pulse.

Run:
    python3 torque_energy_sweep.py

Outputs:
    sweep_results.csv
    sweep_summary.md
"""

from __future__ import annotations

import csv
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


# Fixed audit parameters
GRADIENTS_PER_REVOLUTION = 12
INTERACTION_CHANNELS = 1
NET_ELECTRICAL_ENERGY_PER_PULSE_J = 17.5e-3
FRICTION_LOAD_TORQUE_NM = 0.8

# Sweep definitions requested by the user
RPM_VALUES = list(range(100, 3000 + 1, 100))
PULSE_WINDOW_DEG_VALUES = list(range(1, 20 + 1, 1))
TORQUE_TENTHS_NM = list(range(1, 20 + 1, 1))  # 0.1 Nm through 2.0 Nm

CSV_PATH = Path("sweep_results.csv")
REPORT_PATH = Path("sweep_summary.md")


@dataclass(frozen=True)
class SweepRow:
    rpm: int
    torque_nm: float
    pulse_window_deg: int
    pulse_window_rad: float
    pulse_events_per_second: float
    work_per_pulse_j: float
    electrical_input_power_w: float
    mechanical_pulse_power_w: float
    load_power_w: float
    net_electrical_energy_per_revolution_j: float
    mechanical_pulse_energy_per_revolution_j: float
    load_energy_per_revolution_j: float
    balance_ratio: float
    balance_flag: str


def angular_speed_rad_per_sec(rpm: float) -> float:
    """Convert revolutions per minute to radians per second."""
    return rpm * 2.0 * math.pi / 60.0


def pulse_events_per_second(rpm: float) -> float:
    """One-channel gradient pulse event frequency."""
    return rpm / 60.0 * GRADIENTS_PER_REVOLUTION * INTERACTION_CHANNELS


def classify_balance(work_per_pulse_j: float) -> str:
    """Classify using only modeled electrical input as the energy source."""
    if work_per_pulse_j <= NET_ELECTRICAL_ENERGY_PER_PULSE_J:
        return "BALANCED"
    return "UNBALANCED"


def torque_from_tenths(tenths_nm: int) -> float:
    """Avoid floating-point range accumulation while sweeping 0.1 Nm steps."""
    return tenths_nm / 10.0


def build_rows() -> list[SweepRow]:
    rows: list[SweepRow] = []
    net_electrical_energy_per_revolution_j = (
        NET_ELECTRICAL_ENERGY_PER_PULSE_J * GRADIENTS_PER_REVOLUTION
    )
    load_energy_per_revolution_j = FRICTION_LOAD_TORQUE_NM * 2.0 * math.pi

    for rpm in RPM_VALUES:
        events_per_second = pulse_events_per_second(rpm)
        electrical_input_power_w = NET_ELECTRICAL_ENERGY_PER_PULSE_J * events_per_second
        load_power_w = FRICTION_LOAD_TORQUE_NM * angular_speed_rad_per_sec(rpm)

        for pulse_window_deg in PULSE_WINDOW_DEG_VALUES:
            pulse_window_rad = math.radians(pulse_window_deg)

            for torque_tenths in TORQUE_TENTHS_NM:
                torque_nm = torque_from_tenths(torque_tenths)
                work_per_pulse_j = torque_nm * pulse_window_rad
                mechanical_pulse_power_w = work_per_pulse_j * events_per_second
                mechanical_pulse_energy_per_revolution_j = (
                    work_per_pulse_j * GRADIENTS_PER_REVOLUTION
                )
                balance_ratio = work_per_pulse_j / NET_ELECTRICAL_ENERGY_PER_PULSE_J

                rows.append(
                    SweepRow(
                        rpm=rpm,
                        torque_nm=torque_nm,
                        pulse_window_deg=pulse_window_deg,
                        pulse_window_rad=pulse_window_rad,
                        pulse_events_per_second=events_per_second,
                        work_per_pulse_j=work_per_pulse_j,
                        electrical_input_power_w=electrical_input_power_w,
                        mechanical_pulse_power_w=mechanical_pulse_power_w,
                        load_power_w=load_power_w,
                        net_electrical_energy_per_revolution_j=net_electrical_energy_per_revolution_j,
                        mechanical_pulse_energy_per_revolution_j=mechanical_pulse_energy_per_revolution_j,
                        load_energy_per_revolution_j=load_energy_per_revolution_j,
                        balance_ratio=balance_ratio,
                        balance_flag=classify_balance(work_per_pulse_j),
                    )
                )

    return rows


def write_csv(rows: Iterable[SweepRow], path: Path = CSV_PATH) -> None:
    fieldnames = [
        "rpm",
        "torque_nm",
        "pulse_window_deg",
        "pulse_window_rad",
        "pulse_events_per_second",
        "work_per_pulse_j",
        "electrical_input_power_w",
        "mechanical_pulse_power_w",
        "load_power_w",
        "net_electrical_energy_per_revolution_j",
        "mechanical_pulse_energy_per_revolution_j",
        "load_energy_per_revolution_j",
        "balance_ratio",
        "balance_flag",
    ]
    with path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: getattr(row, field) for field in fieldnames})


def fmt(value: float, digits: int = 6) -> str:
    """Format values compactly for markdown."""
    return f"{value:.{digits}f}"


def max_balanced_torque_by_window(rows: list[SweepRow]) -> list[tuple[int, float | None]]:
    """Return the maximum balanced torque for each pulse window."""
    result: list[tuple[int, float | None]] = []
    for window in PULSE_WINDOW_DEG_VALUES:
        balanced_torques = [
            row.torque_nm
            for row in rows
            if row.pulse_window_deg == window and row.balance_flag == "BALANCED"
        ]
        result.append((window, max(balanced_torques) if balanced_torques else None))
    return result


def max_balanced_window_by_torque(rows: list[SweepRow]) -> list[tuple[float, int | None]]:
    """Return the maximum balanced pulse window for each torque."""
    result: list[tuple[float, int | None]] = []
    for torque_tenths in TORQUE_TENTHS_NM:
        torque = torque_from_tenths(torque_tenths)
        balanced_windows = [
            row.pulse_window_deg
            for row in rows
            if row.torque_nm == torque and row.balance_flag == "BALANCED"
        ]
        result.append((torque, max(balanced_windows) if balanced_windows else None))
    return result


def write_report(rows: list[SweepRow], path: Path = REPORT_PATH) -> None:
    balanced_rows = [row for row in rows if row.balance_flag == "BALANCED"]
    unbalanced_rows = [row for row in rows if row.balance_flag == "UNBALANCED"]

    max_balanced_torque = max((row.torque_nm for row in balanced_rows), default=None)
    max_balanced_window = max((row.pulse_window_deg for row in balanced_rows), default=None)
    max_balanced_torque_rows = [
        row for row in balanced_rows if row.torque_nm == max_balanced_torque
    ] if max_balanced_torque is not None else []
    max_balanced_window_rows = [
        row for row in balanced_rows if row.pulse_window_deg == max_balanced_window
    ] if max_balanced_window is not None else []

    first_rpm = RPM_VALUES[0]
    last_rpm = RPM_VALUES[-1]
    first_events = pulse_events_per_second(first_rpm)
    last_events = pulse_events_per_second(last_rpm)
    first_electrical_power = NET_ELECTRICAL_ENERGY_PER_PULSE_J * first_events
    last_electrical_power = NET_ELECTRICAL_ENERGY_PER_PULSE_J * last_events
    first_load_power = FRICTION_LOAD_TORQUE_NM * angular_speed_rad_per_sec(first_rpm)
    last_load_power = FRICTION_LOAD_TORQUE_NM * angular_speed_rad_per_sec(last_rpm)

    torque_by_window_lines = [
        "| Pulse window (deg) | Maximum BALANCED torque in sweep (Nm) |",
        "|---:|---:|",
    ]
    for window, torque in max_balanced_torque_by_window(rows):
        torque_text = "none" if torque is None else fmt(torque, 1)
        torque_by_window_lines.append(f"| {window} | {torque_text} |")

    window_by_torque_lines = [
        "| Torque (Nm) | Maximum BALANCED pulse window in sweep (deg) |",
        "|---:|---:|",
    ]
    for torque, window in max_balanced_window_by_torque(rows):
        window_text = "none" if window is None else str(window)
        window_by_torque_lines.append(f"| {fmt(torque, 1)} | {window_text} |")

    # Examples are shown at 800 RPM to avoid repeating the same per-pulse
    # balance result for every RPM value. RPM changes power, not per-pulse ratio.
    example_rpm = 800
    balanced_examples = sorted(
        [row for row in balanced_rows if row.rpm == example_rpm],
        key=lambda row: (row.pulse_window_deg, row.torque_nm),
    )[:10]
    unbalanced_examples = sorted(
        [row for row in unbalanced_rows if row.rpm == example_rpm],
        key=lambda row: (row.pulse_window_deg, row.torque_nm),
    )[:10]

    def example_table(title: str, example_rows: list[SweepRow]) -> str:
        lines = [
            title,
            "",
            "| RPM | Torque (Nm) | Window (deg) | Work/pulse (J) | Balance ratio | Flag |",
            "|---:|---:|---:|---:|---:|---|",
        ]
        for row in example_rows:
            lines.append(
                f"| {row.rpm} | {fmt(row.torque_nm, 1)} | {row.pulse_window_deg} | "
                f"{fmt(row.work_per_pulse_j)} | {fmt(row.balance_ratio, 3)} | "
                f"{row.balance_flag} |"
            )
        return "\n".join(lines)

    max_torque_text = "none" if max_balanced_torque is None else fmt(max_balanced_torque, 1)
    max_window_text = "none" if max_balanced_window is None else str(max_balanced_window)

    report = f"""# PM-Gradient Motor Parameter Sweep Energy Audit

## Purpose

This is simulation #2: a parameter sweep for the one-channel PM-gradient assisted motor audit. It is an audit tool only. It does **not** claim success, overunity, or a breakthrough.

Each case is flagged strictly by whether modeled mechanical work per pulse is less than or equal to the stated net electrical input per pulse of {NET_ELECTRICAL_ENERGY_PER_PULSE_J:.6f} J.

## Sweep Inputs

- RPM sweep: {RPM_VALUES[0]} to {RPM_VALUES[-1]} RPM in 100 RPM steps
- Pulse window sweep: {PULSE_WINDOW_DEG_VALUES[0]}° to {PULSE_WINDOW_DEG_VALUES[-1]}° in 1° steps
- Torque sweep: 0.1 Nm to 2.0 Nm in 0.1 Nm steps
- Gradients per revolution: {GRADIENTS_PER_REVOLUTION}
- Interaction channels: {INTERACTION_CHANNELS}
- Net electrical energy per pulse: {NET_ELECTRICAL_ENERGY_PER_PULSE_J:.6f} J ({NET_ELECTRICAL_ENERGY_PER_PULSE_J * 1000:.1f} mJ)
- Friction/load torque: {FRICTION_LOAD_TORQUE_NM:.3f} Nm

## Equations

1. Angular speed: `omega = RPM * 2*pi / 60`
2. Pulse events per second: `f_pulse = RPM / 60 * gradients_per_revolution * channels`
3. Pulse window radians: `theta = pulse_window_deg * pi / 180`
4. Work per pulse: `W_pulse = torque * theta`
5. Electrical input power: `P_elec = net_electrical_energy_per_pulse * f_pulse`
6. Mechanical pulse power: `P_mech = W_pulse * f_pulse`
7. Load power: `P_load = load_torque * omega`
8. Net electrical energy per revolution: `E_elec_rev = net_electrical_energy_per_pulse * gradients_per_revolution`
9. Mechanical pulse energy per revolution: `E_mech_rev = W_pulse * gradients_per_revolution`
10. Load energy per revolution: `E_load_rev = load_torque * 2*pi`
11. Balance ratio: `ratio = W_pulse / net_electrical_energy_per_pulse`
12. Balance flag: `BALANCED if W_pulse <= net_electrical_energy_per_pulse else UNBALANCED`

## Sweep Summary

- Total cases: **{len(rows)}**
- BALANCED cases: **{len(balanced_rows)}**
- UNBALANCED cases: **{len(unbalanced_rows)}**
- Pulse events per second range: **{first_events:.6f} to {last_events:.6f} pulses/s**
- Electrical input power range: **{first_electrical_power:.6f} to {last_electrical_power:.6f} W**
- Load power range: **{first_load_power:.6f} to {last_load_power:.6f} W**
- Net electrical energy per revolution: **{NET_ELECTRICAL_ENERGY_PER_PULSE_J * GRADIENTS_PER_REVOLUTION:.6f} J/rev**
- Load energy per revolution: **{FRICTION_LOAD_TORQUE_NM * 2.0 * math.pi:.6f} J/rev**

## Maximum Balanced Parameters With 17.5 mJ Net Electrical Input

Within this discrete sweep:

- Maximum torque that remains BALANCED: **{max_torque_text} Nm**
- That maximum torque is BALANCED only at pulse window(s): **{', '.join(str(window) + '°' for window in sorted({row.pulse_window_deg for row in max_balanced_torque_rows})) if max_balanced_torque_rows else 'none'}**
- Maximum pulse window that remains BALANCED: **{max_window_text}°**
- That maximum pulse window is BALANCED only at torque value(s): **{', '.join(fmt(torque, 1) + ' Nm' for torque in sorted({row.torque_nm for row in max_balanced_window_rows})) if max_balanced_window_rows else 'none'}**

Analytically, the balance boundary is `torque * radians(window_deg) <= {NET_ELECTRICAL_ENERGY_PER_PULSE_J:.6f}`. RPM changes power because it changes event rate, but it does not change the per-pulse balance ratio.

## Maximum BALANCED Torque by Pulse Window

{chr(10).join(torque_by_window_lines)}

## Maximum BALANCED Pulse Window by Torque

{chr(10).join(window_by_torque_lines)}

## Example BALANCED Combinations

{example_table('', balanced_examples)}

## Example UNBALANCED Combinations

{example_table('', unbalanced_examples)}

## Interpretation

The sweep stays conservative: a case is only BALANCED when the modeled mechanical pulse work does not exceed the stated net electrical pulse input. Cases above that threshold are marked UNBALANCED and require an identified, measured energy source before they can be interpreted as physically closed.

Because the electrical energy per pulse is fixed, wider windows require lower torque to remain balanced, and higher torque requires narrower windows. RPM scales both electrical input power and mechanical pulse power for a fixed torque/window pair, while the per-pulse balance ratio remains unchanged.

## Output Files

- `sweep_results.csv`
- `sweep_summary.md`
- `torque_energy_sweep.py`
"""
    path.write_text(report, encoding="utf-8")


def main() -> None:
    rows = build_rows()
    write_csv(rows)
    write_report(rows)
    print(f"Wrote {CSV_PATH} with {len(rows)} cases")
    print(f"Wrote {REPORT_PATH}")


if __name__ == "__main__":
    main()
