"""Compare selective coil-on vs coil-off FEMM pulse assist results."""

from __future__ import annotations

import argparse
import csv
import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from validation.analyze_femm_sweeps import curve_stats, load_curve  # noqa: E402
from validation.analyze_selective_assist import integrate_segment, window_span_deg  # noqa: E402
from validation.pulse_control import load_pulse_windows  # noqa: E402
from validation.rank_femm_variants import cancellation_ratio, full_rev_equivalent  # noqa: E402


CASES = [
    ("coil-off", "data/field_sim/femm_pulse_gap159_coiloff_period45_step1.csv"),
    ("low", "data/field_sim/femm_pulse_gap159_low_period45_step1.csv"),
    ("medium", "data/field_sim/femm_pulse_gap159_medium_period45_step1.csv"),
    ("high", "data/field_sim/femm_pulse_gap159_high_period45_step1.csv"),
]


def load_pulse_curve(path: Path) -> list[dict[str, float | int]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return [
            {
                "angle_deg": float(row["angle_deg"]),
                "torque_nm": float(row["torque_nm"]),
                "coil_current_a": float(row.get("coil_current_a", 0.0)),
                "active_eml": int(float(row.get("active_eml", 0))),
                "pulse_on": int(float(row.get("pulse_on", 0))),
            }
            for row in csv.DictReader(handle)
        ]


def region_metrics(
    curve: list[tuple[float, float]],
    windows: list[dict[str, float]],
) -> dict[str, float]:
    work = sum(integrate_segment(curve, w["start_deg"], w["end_deg"]) for w in windows)
    torques = []
    for angle, torque in curve:
        for window in windows:
            if window["start_deg"] <= angle <= window["end_deg"]:
                torques.append(torque)
                break
    peak_pos = max(torques) if torques else math.nan
    peak_neg = min(torques) if torques else math.nan
    return {
        "work_j": work,
        "peak_positive_nm": peak_pos,
        "peak_negative_nm": peak_neg,
    }


def delta_metrics(case: dict[str, float], baseline: dict[str, float]) -> dict[str, float]:
    return {
        "added_work_45deg_j": case["work_period_j"] - baseline["work_period_j"],
        "added_full_rev_j": case["full_rev_equiv_j"] - baseline["full_rev_equiv_j"],
        "assist_work_delta_j": case["assist_work_j"] - baseline["assist_work_j"],
        "lockout_work_delta_j": case["lockout_work_j"] - baseline["lockout_work_j"],
        "peak_positive_delta_nm": case["peak_positive_nm"] - baseline["peak_positive_nm"],
        "peak_negative_delta_nm": case["peak_negative_nm"] - baseline["peak_negative_nm"],
        "cancellation_delta": case["cancellation_ratio"] - baseline["cancellation_ratio"],
    }


def summarize_case(
    label: str,
    path: Path,
    assist: list[dict[str, float]],
    lockout: list[dict[str, float]],
) -> dict[str, float | str | int]:
    stats = curve_stats(path)
    curve = load_curve(path)
    angle_span = float(stats["angle_span_deg"])
    assist_stats = region_metrics(curve, assist)
    lockout_stats = region_metrics(curve, lockout)
    pulse_rows = load_pulse_curve(path) if path.exists() else []
    pulsed_points = sum(1 for row in pulse_rows if row["pulse_on"])
    return {
        "label": label,
        "csv": str(path.as_posix()),
        "angle_span_deg": angle_span,
        "screen_status": "complete_period" if angle_span >= 44.9 else "incomplete_period",
        "work_period_j": float(stats["work_j_per_rev"]),
        "full_rev_equiv_j": full_rev_equivalent(stats),
        "peak_positive_nm": float(stats["max_torque_nm"]),
        "peak_negative_nm": float(stats["min_torque_nm"]),
        "positive_gross_work_j": float(stats["positive_work_j"]),
        "negative_gross_work_abs_j": abs(float(stats["negative_work_j"])),
        "cancellation_ratio": cancellation_ratio(stats),
        "closure_delta_nm": float(stats["closure_delta_nm"]),
        "assist_work_j": assist_stats["work_j"],
        "lockout_work_j": lockout_stats["work_j"],
        "assist_peak_positive_nm": assist_stats["peak_positive_nm"],
        "assist_peak_negative_nm": assist_stats["peak_negative_nm"],
        "lockout_peak_negative_nm": lockout_stats["peak_negative_nm"],
        "pulsed_angle_count": pulsed_points,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Compare selective pulse assist FEMM cases.")
    parser.add_argument(
        "--windows",
        type=Path,
        default=ROOT / "field_sim/femm/pulse_strategy.gap159_eml12.json",
    )
    parser.add_argument("--json-out", type=Path, default=ROOT / "reports/pulse_assist_comparison_latest.json")
    parser.add_argument("--md-out", type=Path, default=ROOT / "reports/pulse_assist_comparison.md")
    args = parser.parse_args()

    assist, lockout = load_pulse_windows(args.windows)
    rows = []
    for label, rel in CASES:
        path = ROOT / rel
        if not path.exists():
            rows.append({"label": label, "csv": rel, "status": "missing"})
            continue
        row = summarize_case(label, path, assist, lockout)
        row["status"] = "complete"
        rows.append(row)

    solved = [
        row
        for row in rows
        if row.get("status") == "complete" and row.get("screen_status") == "complete_period"
    ]
    baseline = next((row for row in solved if row["label"] == "coil-off"), None)
    if baseline:
        for row in solved:
            if row["label"] != "coil-off":
                row.update(delta_metrics(row, baseline))

    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    args.json_out.write_text(json.dumps(rows, indent=2) + "\n", encoding="utf-8")

    assist_span = window_span_deg(assist)
    lockout_span = window_span_deg(lockout)
    lines = [
        "# Selective Pulse Assist Comparison",
        "",
        "**Date:** 2026-06-15",
        "",
        f"**Geometry:** ASYM_B + EML +12° + gap 159.0 mm",
        f"**Pulse windows:** `{args.windows.as_posix()}`",
        "",
        "Assist: 0–2°, 14–25°, 37–45°. Lockout: 2–14°, 25–37°.",
        "First screen only; not mesh-converged. No performance claims unless net energy closes.",
        "",
        "## Summary",
        "",
        "| Case | 45° work (J) | Full-rev equiv (J/rev) | Assist work (J) | Lockout work (J) | Peak + (Nm) | Peak − (Nm) | Cancellation | Pulsed angles |",
        "|------|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in solved:
        lines.append(
            f"| {row['label']} | {row['work_period_j']:.6f} | {row['full_rev_equiv_j']:.6f} | "
            f"{row['assist_work_j']:.6f} | {row['lockout_work_j']:.6f} | "
            f"{row['peak_positive_nm']:.3f} | {row['peak_negative_nm']:.3f} | "
            f"{row['cancellation_ratio']:.3f} | {row['pulsed_angle_count']} |"
        )

    if baseline:
        lines.extend(
            [
                "",
                "## Delta vs Coil-Off Baseline",
                "",
                "| Case | Added 45° work (J) | Added full-rev (J/rev) | Assist Δ (J) | Lockout Δ (J) | Peak + Δ (Nm) | Peak − Δ (Nm) | Cancel Δ |",
                "|------|---:|---:|---:|---:|---:|---:|---:|",
            ]
        )
        for row in solved:
            if row["label"] == "coil-off":
                continue
            lines.append(
                f"| {row['label']} | {row['added_work_45deg_j']:.6f} | {row['added_full_rev_j']:.6f} | "
                f"{row['assist_work_delta_j']:.6f} | {row['lockout_work_delta_j']:.6f} | "
                f"{row['peak_positive_delta_nm']:.3f} | {row['peak_negative_delta_nm']:.3f} | "
                f"{row['cancellation_delta']:.3f} |"
            )

    lines.extend(
        [
            "",
            "## Window Spans",
            "",
            f"- Assist span: {assist_span:.1f}°",
            f"- Lockout span: {lockout_span:.1f}°",
            "",
            "## Interpretation",
            "",
            "Added mechanical work must exceed estimated electrical input before claiming pulse assist benefit.",
            "Lockout-region work should not become more negative when coils are off outside assist windows.",
        ]
    )
    args.md_out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(rows, indent=2))


if __name__ == "__main__":
    main()
