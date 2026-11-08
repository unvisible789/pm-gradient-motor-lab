"""Report raw, unverified FEMM sector diagnostics without performance extrapolation."""

from __future__ import annotations

import argparse
import csv
import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from validation.analyze_selective_assist import integrate_segment, window_span_deg  # noqa: E402
from validation.pulse_control import load_pulse_windows  # noqa: E402
from validation.passive_cycle_audit import audit_curve  # noqa: E402


CASES = [
    ("coil-off", "data/field_sim/femm_pulse_gap159_coiloff_period45_step1.csv"),
    ("low", "data/field_sim/femm_pulse_gap159_low_period45_step1.csv"),
    ("medium", "data/field_sim/femm_pulse_gap159_medium_period45_step1.csv"),
    ("high", "data/field_sim/femm_pulse_gap159_high_period45_step1.csv"),
]


def load_pulse_curve(path: Path) -> list[dict]:
    """Validate acquisition order; both current headers denote a one-turn surrogate."""
    rows = []
    with path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        if not {"angle_deg", "torque_nm"}.issubset(reader.fieldnames or []):
            raise ValueError("CSV requires angle_deg and torque_nm")
        for line, source in enumerate(reader, start=2):
            angle = float(source["angle_deg"])
            torque = float(source["torque_nm"])
            currents = [float(source[key]) for key in ("femm_single_turn_current_a", "coil_current_a")
                        if source.get(key) not in (None, "")]
            current = currents[0] if currents else None
            active = float(source.get("active_eml") or 0)
            pulse = float(source.get("pulse_on") or 0)
            if not all(math.isfinite(value) for value in [angle, torque, active, pulse, *currents]):
                raise ValueError(f"Non-finite sample at CSV line {line}")
            if len(currents) == 2 and not math.isclose(*currents, rel_tol=1e-9, abs_tol=1e-12):
                raise ValueError(f"Conflicting one-turn current columns at CSV line {line}")
            if active < 0 or not active.is_integer() or pulse not in (0, 1):
                raise ValueError(f"Invalid coil index or pulse flag at CSV line {line}")
            if rows and angle <= rows[-1]["angle_deg"]:
                raise ValueError("Sample angles must be strictly increasing; duplicate or reversed samples are invalid")
            rows.append({"angle_deg": angle, "torque_nm": torque,
                         "femm_single_turn_current_a": current,
                         "physical_wire_current_a": None,
                         "active_eml": int(active), "pulse_on": int(pulse)})
    if len(rows) < 2:
        raise ValueError("At least two samples are required")
    return rows


def region_metrics(curve: list[tuple[float, float]], windows: list[dict[str, float]]) -> dict:
    work = sum(integrate_segment(curve, w["start_deg"], w["end_deg"]) for w in windows)
    torques = [torque for angle, torque in curve
               if any(w["start_deg"] <= angle <= w["end_deg"] for w in windows)]
    return {"work_j": work, "peak_positive_nm": max(torques) if torques else None,
            "peak_negative_nm": min(torques) if torques else None}


def delta_metrics(case: dict, baseline: dict) -> dict:
    """Compare complete matching sectors only; never infer a full revolution."""
    comparable = (case.get("sector_complete") is True and baseline.get("sector_complete") is True
                  and case.get("angle_start_deg") == baseline.get("angle_start_deg")
                  and case.get("angle_end_deg") == baseline.get("angle_end_deg"))
    mapping = {"added_work_45deg_j": "work_period_j", "assist_work_delta_j": "assist_work_j",
               "lockout_work_delta_j": "lockout_work_j", "peak_positive_delta_nm": "peak_positive_nm",
               "peak_negative_delta_nm": "peak_negative_nm", "cancellation_delta": "cancellation_ratio"}
    result = {name: case[key] - baseline[key]
              if comparable and case.get(key) is not None and baseline.get(key) is not None else None
              for name, key in mapping.items()}
    result["added_full_rev_j"] = None
    result["comparison_status"] = "unverified_sector_diagnostic" if comparable else "insufficient_data"
    return result


def summarize_case(label: str, path: Path, assist: list[dict[str, float]],
                   lockout: list[dict[str, float]]) -> dict:
    pulse_rows = load_pulse_curve(path)
    curve = [(row["angle_deg"], row["torque_nm"]) for row in pulse_rows]
    start, end = curve[0][0], curve[-1][0]
    max_gap = max(b[0] - a[0] for a, b in zip(curve, curve[1:]))
    complete = math.isclose(start, 0.0, abs_tol=1e-9) and math.isclose(end, 45.0, abs_tol=1e-9) and max_gap <= 1.0 + 1e-9
    try:
        csv_path = path.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        csv_path = path.as_posix()
    result = {
        "label": label, "csv": csv_path,
        "status": "diagnostic_only" if complete else "incomplete",
        "angle_start_deg": start, "angle_end_deg": end, "angle_span_deg": end - start,
        "sample_count": len(curve), "maximum_sample_gap_deg": max_gap,
        "sector_complete": complete,
        "screen_status": "complete_sector_unverified" if complete else "incomplete_period",
        "full_state_periodicity_verified": False, "performance_claim_eligible": False,
        "work_period_j": None, "full_rev_equiv_j": None,
        "peak_positive_nm": None, "peak_negative_nm": None,
        "positive_gross_work_j": None, "negative_gross_work_abs_j": None,
        "cancellation_ratio": None, "closure_delta_nm": None,
        "assist_work_j": None, "lockout_work_j": None,
        "assist_peak_positive_nm": None, "assist_peak_negative_nm": None,
        "lockout_peak_negative_nm": None,
        "pulsed_angle_count": sum(row["pulse_on"] for row in pulse_rows),
        "pulse_count_per_rev": None,
        "current_column_meaning": "FEMM one-turn surrogate; numerically winding ampere-turns, not physical wire amperes",
        "limitation": "Complete 0–45 degree sampling is not verified full-state periodicity or measured shaft output; pulsed sample counts are not pulse events.",
    }
    if not complete:
        result["limitation"] = "Incomplete 0–45 degree sector or sample gap above 1 degree; work and comparison metrics are withheld."
        return result
    assist_stats, lockout_stats = region_metrics(curve, assist), region_metrics(curve, lockout)
    segments = [(a[1] + b[1]) / 2.0 * math.radians(b[0] - a[0]) for a, b in zip(curve, curve[1:])]
    # Split a linear segment exactly at a torque zero crossing. Classifying a
    # whole trapezoid by its net sign hides cancelling positive/negative area.
    absolute_work = audit_curve(curve, 45.0)["absolute_torque_integral_j"]
    positive = (absolute_work + sum(segments)) / 2.0
    negative = (absolute_work - sum(segments)) / 2.0
    gross = positive + negative
    result.update({
        "work_period_j": sum(segments),
        "peak_positive_nm": max(t for _, t in curve), "peak_negative_nm": min(t for _, t in curve),
        "positive_gross_work_j": positive, "negative_gross_work_abs_j": negative,
        "cancellation_ratio": 1.0 - abs(positive - negative) / gross if gross else None,
        "closure_delta_nm": curve[-1][1] - curve[0][1],
        "assist_work_j": assist_stats["work_j"], "lockout_work_j": lockout_stats["work_j"],
        "assist_peak_positive_nm": assist_stats["peak_positive_nm"],
        "assist_peak_negative_nm": assist_stats["peak_negative_nm"],
        "lockout_peak_negative_nm": lockout_stats["peak_negative_nm"],
    })
    return result


def format_metric(value: float | None, places: int = 6) -> str:
    return "unknown" if value is None else f"{value:.{places}f}"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--windows", type=Path, default=ROOT / "field_sim/femm/pulse_strategy.gap159_eml12.json")
    parser.add_argument("--json-out", type=Path, default=ROOT / "reports/pulse_assist_comparison_latest.json")
    parser.add_argument("--md-out", type=Path, default=ROOT / "reports/pulse_assist_comparison.md")
    args = parser.parse_args()
    assist, lockout = load_pulse_windows(args.windows)
    rows = []
    for label, rel in CASES:
        path = ROOT / rel
        if not path.exists():
            rows.append({"label": label, "csv": rel, "status": "missing", "performance_claim_eligible": False})
            continue
        try:
            rows.append(summarize_case(label, path, assist, lockout))
        except (ValueError, KeyError) as error:
            rows.append({"label": label, "csv": rel, "status": "invalid", "error": str(error), "performance_claim_eligible": False})
    complete = [row for row in rows if row.get("sector_complete")]
    baseline = next((row for row in complete if row["label"] == "coil-off"), None)
    if baseline:
        for row in complete:
            if row["label"] != "coil-off":
                row.update(delta_metrics(row, baseline))
    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    args.json_out.write_text(json.dumps(rows, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    lines = ["# Selective Pulse Assist Comparison", "", "**Status: insufficient data for motor performance or energy balance.**", "",
             "Geometry: ASYM_B + EML +12° + gap 159.0 mm. The following values are raw magnetostatic 0–45° sector diagnostics.",
             "The full electromagnetic and controller state has not been shown to repeat after 45°. No sector is extrapolated to 360°.",
             "Mesh convergence, dynamic shaft output, electrical input and stored-energy changes remain unverified.", "", "## Source Coverage", "",
             "| Case | Status | Samples | Span (degrees) |", "|---|---|---:|---:|"]
    for row in rows:
        lines.append(f"| {row['label']} | {row.get('screen_status', row['status'])} | {row.get('sample_count', 'unknown')} | {format_metric(row.get('angle_span_deg'), 1)} |")
    lines.extend(["", "## Complete Sector Diagnostics", "",
                  "| Case | Raw 45° work (J) | Assist work (J) | Lockout work (J) | Peak + (Nm) | Peak − (Nm) | Cancellation | On-samples |",
                  "|---|---:|---:|---:|---:|---:|---:|---:|"])
    for row in complete:
        values = [format_metric(row.get(key), places) for key, places in
                  [("work_period_j", 6), ("assist_work_j", 6), ("lockout_work_j", 6), ("peak_positive_nm", 3), ("peak_negative_nm", 3), ("cancellation_ratio", 3)]]
        lines.append(f"| {row['label']} | " + " | ".join(values) + f" | {row['pulsed_angle_count']} |")
    if baseline:
        lines.extend(["", "## Raw Sector Differences from Coil-Off", "",
                      "| Case | 45° work difference (J) | Assist difference (J) | Lockout difference (J) |",
                      "|---|---:|---:|---:|"])
        for row in complete:
            if row["label"] != "coil-off":
                lines.append(f"| {row['label']} | " + " | ".join(format_metric(row.get(key)) for key in
                             ("added_work_45deg_j", "assist_work_delta_j", "lockout_work_delta_j")) + " |")
    lines.extend(["", "## Limits", "",
                  f"Assist windows cover {window_span_deg(assist):.1f}°; lockout windows cover {window_span_deg(lockout):.1f}°.",
                  "Incomplete sectors, missing samples, non-finite values, duplicate angles and reversed acquisition order cannot support a comparison.",
                  "An on-sample count is not a pulse-event count or a time duty cycle. Both legacy `coil_current_a` and `femm_single_turn_current_a` describe a one-turn FEMM surrogate; physical wire current requires the winding turn count.",
                  "Positive raw sector work or a small case difference is not evidence of sustained net output. A repeated operating cycle, signed electrical bus measurements, all auxiliary inputs, shaft work, losses, and stored-energy changes are required for an energy balance."])
    args.md_out.parent.mkdir(parents=True, exist_ok=True)
    args.md_out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(rows, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
