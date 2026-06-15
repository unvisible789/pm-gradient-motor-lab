from __future__ import annotations

import csv
import math
from pathlib import Path
from typing import Iterable


NumberRow = dict[str, float | str]


def _as_float(value: float | str) -> float:
    if isinstance(value, (float, int)):
        return float(value)
    return float(str(value).strip())


def load_numeric_csv(path: str | Path) -> list[NumberRow]:
    """Load CSV rows, converting numeric-looking values to floats."""
    rows: list[NumberRow] = []
    with Path(path).open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            converted: NumberRow = {}
            for key, value in row.items():
                if value is None:
                    converted[key] = ""
                    continue
                text = value.strip()
                try:
                    converted[key] = float(text)
                except ValueError:
                    converted[key] = text
            rows.append(converted)
    return rows


def integrate_torque_angle(rows: Iterable[NumberRow]) -> dict[str, float]:
    """Integrate torque over angle and return work per revolution."""
    points = sorted(
        [(_as_float(row["angle_deg"]), _as_float(row["torque_nm"])) for row in rows],
        key=lambda item: item[0],
    )
    if len(points) < 2:
        raise ValueError("At least two torque-angle points are required")

    work_j = 0.0
    for (angle_a, torque_a), (angle_b, torque_b) in zip(points, points[1:]):
        delta_rad = math.radians(angle_b - angle_a)
        avg_torque = (torque_a + torque_b) / 2.0
        work_j += avg_torque * delta_rad

    span_rad = math.radians(points[-1][0] - points[0][0])
    average_torque = work_j / span_rad if span_rad else 0.0
    return {
        "work_j_per_rev": work_j,
        "average_torque_nm": average_torque,
        "angle_span_deg": points[-1][0] - points[0][0],
        "points": float(len(points)),
    }


def compare_torque_angle_sources(
    bench_rows: Iterable[NumberRow], field_rows: Iterable[NumberRow]
) -> dict[str, float]:
    """Compare torque-angle curves at matching angle samples."""
    bench_by_angle = {
        _as_float(row["angle_deg"]): _as_float(row["torque_nm"]) for row in bench_rows
    }
    field_by_angle = {
        _as_float(row["angle_deg"]): _as_float(row["torque_nm"]) for row in field_rows
    }
    common_angles = sorted(set(bench_by_angle) & set(field_by_angle))
    if not common_angles:
        raise ValueError("No matching angle samples found")

    abs_errors = [
        abs(bench_by_angle[angle] - field_by_angle[angle]) for angle in common_angles
    ]
    return {
        "points_compared": float(len(common_angles)),
        "mean_abs_error_nm": sum(abs_errors) / len(abs_errors),
        "max_abs_error_nm": max(abs_errors),
    }


def audit_bench_run(rows: Iterable[NumberRow]) -> dict[str, float | str]:
    """Integrate measured voltage/current and torque/rpm over time."""
    points = sorted(
        [
            (
                _as_float(row["time_s"]),
                _as_float(row["voltage_v"]),
                _as_float(row["current_a"]),
                _as_float(row["torque_nm"]),
                _as_float(row["rpm"]),
            )
            for row in rows
        ],
        key=lambda item: item[0],
    )
    if len(points) < 2:
        raise ValueError("At least two bench samples are required")

    electrical_j = 0.0
    mechanical_j = 0.0
    for a, b in zip(points, points[1:]):
        time_a, voltage_a, current_a, torque_a, rpm_a = a
        time_b, voltage_b, current_b, torque_b, rpm_b = b
        dt = time_b - time_a
        if dt < 0:
            raise ValueError("Time samples must be monotonic")
        power_e_a = voltage_a * current_a
        power_e_b = voltage_b * current_b
        omega_a = rpm_a * 2.0 * math.pi / 60.0
        omega_b = rpm_b * 2.0 * math.pi / 60.0
        power_m_a = torque_a * omega_a
        power_m_b = torque_b * omega_b
        electrical_j += (power_e_a + power_e_b) / 2.0 * dt
        mechanical_j += (power_m_a + power_m_b) / 2.0 * dt

    ratio = mechanical_j / electrical_j if electrical_j else math.inf
    return {
        "electrical_input_j": electrical_j,
        "mechanical_output_j": mechanical_j,
        "mechanical_to_electrical_ratio": ratio,
        "energy_balance_flag": (
            "BALANCED_BY_MEASURED_INPUT"
            if mechanical_j <= electrical_j
            else "UNBALANCED_PENDING_SOURCE_IDENTIFICATION"
        ),
    }


def compare_motor_benchmark(
    simulated: NumberRow, reference: NumberRow, tolerance_pct: float
) -> dict[str, object]:
    """Compare simulated motor summary values against a published benchmark."""
    metrics: dict[str, dict[str, float | str]] = {}
    overall_pass = True
    for key in sorted(set(simulated) & set(reference)):
        if key == "motor_name":
            continue
        try:
            sim_value = _as_float(simulated[key])
            ref_value = _as_float(reference[key])
        except (TypeError, ValueError):
            continue
        error_pct = abs(sim_value - ref_value) / abs(ref_value) * 100.0 if ref_value else 0.0
        status = "PASS" if error_pct <= tolerance_pct else "FAIL"
        if status == "FAIL":
            overall_pass = False
        metrics[key] = {
            "simulated": sim_value,
            "reference": ref_value,
            "error_pct": error_pct,
            "status": status,
        }
    return {
        "overall_status": "PASS" if overall_pass else "FAIL",
        "tolerance_pct": tolerance_pct,
        "metrics": metrics,
    }
