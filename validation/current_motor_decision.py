from __future__ import annotations

import math
import sys
from pathlib import Path


def evaluate_current_motor_case(
    *,
    rpm: float,
    gradients_per_revolution: int,
    channels: int,
    net_electrical_energy_per_pulse_j: float,
    load_torque_nm: float,
    pulse_assist_torque_nm: float,
    pulse_window_deg: float,
) -> dict[str, float | str]:
    omega_rad_s = rpm * 2.0 * math.pi / 60.0
    pulse_events_per_second = rpm / 60.0 * gradients_per_revolution * channels
    pulse_window_rad = math.radians(pulse_window_deg)
    pulse_work_j = pulse_assist_torque_nm * pulse_window_rad

    electrical_input_power_w = (
        net_electrical_energy_per_pulse_j * pulse_events_per_second
    )
    mechanical_pulse_power_w = pulse_work_j * pulse_events_per_second
    load_power_w = load_torque_nm * omega_rad_s

    net_electrical_energy_per_rev_j = (
        net_electrical_energy_per_pulse_j * gradients_per_revolution * channels
    )
    pulse_mechanical_energy_per_rev_j = (
        pulse_work_j * gradients_per_revolution * channels
    )
    load_energy_per_rev_j = load_torque_nm * 2.0 * math.pi

    required_energy_per_rev_j = max(
        pulse_mechanical_energy_per_rev_j, load_energy_per_rev_j
    )
    minimum_extra_energy_per_pulse_j = max(
        pulse_work_j - net_electrical_energy_per_pulse_j, 0.0
    )
    minimum_extra_energy_per_rev_j = max(
        required_energy_per_rev_j - net_electrical_energy_per_rev_j, 0.0
    )

    pulse_balance_flag = (
        "BALANCED_BY_STATED_PULSE_INPUT"
        if pulse_work_j <= net_electrical_energy_per_pulse_j
        else "UNBALANCED_PULSE_WORK_EXCEEDS_INPUT"
    )
    status = (
        "BALANCED_BY_STATED_INPUT"
        if minimum_extra_energy_per_rev_j == 0.0
        else "UNBALANCED_PENDING_SOURCE_IDENTIFICATION"
    )

    return {
        "rpm": rpm,
        "pulse_events_per_second": pulse_events_per_second,
        "pulse_window_deg": pulse_window_deg,
        "pulse_assist_torque_nm": pulse_assist_torque_nm,
        "pulse_work_j": pulse_work_j,
        "electrical_input_power_w": electrical_input_power_w,
        "mechanical_pulse_power_w": mechanical_pulse_power_w,
        "load_power_w": load_power_w,
        "net_electrical_energy_per_rev_j": net_electrical_energy_per_rev_j,
        "pulse_mechanical_energy_per_rev_j": pulse_mechanical_energy_per_rev_j,
        "load_energy_per_rev_j": load_energy_per_rev_j,
        "minimum_extra_energy_per_pulse_j": minimum_extra_energy_per_pulse_j,
        "minimum_extra_energy_per_rev_j": minimum_extra_energy_per_rev_j,
        "pulse_balance_ratio": pulse_work_j / net_electrical_energy_per_pulse_j,
        "pulse_balance_flag": pulse_balance_flag,
        "status": status,
    }


def current_default_cases() -> list[dict[str, float | str]]:
    return [
        evaluate_current_motor_case(
            rpm=800.0,
            gradients_per_revolution=12,
            channels=1,
            net_electrical_energy_per_pulse_j=0.0175,
            load_torque_nm=0.8,
            pulse_assist_torque_nm=1.8,
            pulse_window_deg=window_deg,
        )
        for window_deg in [2.0, 4.0, 8.0, 12.0, 20.0]
    ]


def write_current_motor_report(path: str | Path) -> None:
    cases = current_default_cases()
    path = Path(path)
    lines = [
        "# Current Motor Decision Report",
        "",
        "This report uses the current PM-gradient motor assumptions already in",
        "the repository. It does not include new bench measurements.",
        "",
        "Baseline assumptions:",
        "",
        "- 800 RPM",
        "- 12 magnetic gradients per revolution",
        "- 1 interaction channel",
        "- 17.5 mJ net electrical input per pulse",
        "- 0.8 Nm load/friction torque",
        "- 1.8 Nm pulse-assist torque assumption",
        "",
        "| Pulse window (deg) | Work/pulse (J) | Pulse balance ratio | Electrical input power (W) | Mechanical pulse power (W) | Load power (W) | Minimum extra energy/rev (J) | Status |",
        "|---:|---:|---:|---:|---:|---:|---:|---|",
    ]
    for case in cases:
        lines.append(
            "| "
            f"{case['pulse_window_deg']:.1f} | "
            f"{case['pulse_work_j']:.6f} | "
            f"{case['pulse_balance_ratio']:.3f} | "
            f"{case['electrical_input_power_w']:.6f} | "
            f"{case['mechanical_pulse_power_w']:.6f} | "
            f"{case['load_power_w']:.6f} | "
            f"{case['minimum_extra_energy_per_rev_j']:.6f} | "
            f"{case['status']} |"
        )

    first = cases[0]
    lines.extend(
        [
            "",
            "Decision:",
            "",
            "**The current motor model does not pass the conservative energy audit.**",
            "",
            "The smallest tested pulse window, 2 degrees, still needs at least",
            f"{first['minimum_extra_energy_per_pulse_j']:.6f} J of additional",
            "identified energy per pulse before the pulse work is closed.",
            "",
            "At the stated 0.8 Nm load, the design also needs at least",
            f"{first['minimum_extra_energy_per_rev_j']:.6f} J of additional",
            "identified energy per revolution before load operation is closed.",
            "",
            "What would change this result:",
            "",
            "- measured torque-angle data showing net positive work over 360 degrees,",
            "- measured electrical waveforms showing higher true input or recovered energy,",
            "- lower load/friction torque,",
            "- lower pulse torque,",
            "- narrower pulse windows,",
            "- more channels only if their energy input and mechanical work are both measured.",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(root))
    report_path = root / "reports" / "current_motor_decision_report.md"
    write_current_motor_report(report_path)
    print(f"Wrote {report_path.relative_to(root)}")


if __name__ == "__main__":
    main()
