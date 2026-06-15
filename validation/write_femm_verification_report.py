from __future__ import annotations

import csv
import json
import math
from pathlib import Path
from xml.sax.saxutils import escape

from validation.analyze_femm_sweeps import curve_stats, load_curve


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data" / "field_sim"
PLOT_DIR = ROOT / "reports" / "plots"
REPORT_PATH = ROOT / "reports" / "femm_verification_report.md"
SUMMARY_PATH = ROOT / "reports" / "femm_verification_summary.json"


STUDIES = {
    "mesh": [
        ("coarse", "femm_verify_mesh_coarse_step1.csv"),
        ("medium", "femm_verify_mesh_medium_step1.csv"),
        ("fine", "femm_verify_mesh_fine_step1.csv"),
        ("very_fine", "femm_verify_mesh_veryfine_step1.csv"),
    ],
    "angle": [
        ("2deg", "femm_verify_angle_step2.csv"),
        ("1deg", "femm_verify_angle_step1.csv"),
        ("0p5deg", "femm_verify_angle_step0p5.csv"),
        ("0p25deg", "femm_verify_angle_step0p25.csv"),
    ],
    "boundary": [
        ("260mm", "femm_verify_boundary_260_step1.csv"),
        ("340mm", "femm_verify_boundary_340_step1.csv"),
        ("420mm", "femm_verify_boundary_420_step1.csv"),
    ],
    "reverse": [
        ("forward", "femm_verify_reverse_forward_step1.csv"),
        ("reverse", "femm_verify_reverse_reverse_step1.csv"),
    ],
}


def pct_change(current: float, previous: float) -> float:
    if previous == 0:
        return math.inf
    return (current - previous) / abs(previous) * 100.0


def make_plot(path: Path, title: str, curves: list[tuple[str, Path]]) -> None:
    loaded = [(label, load_curve(csv_path)) for label, csv_path in curves]
    all_points = [point for _, curve in loaded for point in curve]
    xs = [angle for angle, _ in all_points]
    ys = [torque for _, torque in all_points]
    width, height = 920, 460
    pad_left, pad_right, pad_top, pad_bottom = 70, 30, 45, 55
    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)
    if min_y == max_y:
        min_y -= 1
        max_y += 1
    y_margin = (max_y - min_y) * 0.08
    min_y -= y_margin
    max_y += y_margin

    def sx(x: float) -> float:
        return pad_left + (x - min_x) / (max_x - min_x) * (width - pad_left - pad_right)

    def sy(y: float) -> float:
        return height - pad_bottom - (y - min_y) / (max_y - min_y) * (
            height - pad_top - pad_bottom
        )

    colors = ["#2563eb", "#dc2626", "#16a34a", "#9333ea", "#ea580c"]
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="white"/>',
        f'<text x="{pad_left}" y="28" font-family="Arial" font-size="18" font-weight="700">{escape(title)}</text>',
        f'<line x1="{pad_left}" y1="{height-pad_bottom}" x2="{width-pad_right}" y2="{height-pad_bottom}" stroke="#222"/>',
        f'<line x1="{pad_left}" y1="{pad_top}" x2="{pad_left}" y2="{height-pad_bottom}" stroke="#222"/>',
        f'<text x="{width/2-40:.1f}" y="{height-14}" font-family="Arial" font-size="13">angle (deg)</text>',
        f'<text x="15" y="{height/2+60:.1f}" transform="rotate(-90 15 {height/2+60:.1f})" font-family="Arial" font-size="13">torque (Nm)</text>',
    ]
    zero_y = sy(0.0)
    if pad_top <= zero_y <= height - pad_bottom:
        parts.append(
            f'<line x1="{pad_left}" y1="{zero_y:.2f}" x2="{width-pad_right}" y2="{zero_y:.2f}" stroke="#999" stroke-dasharray="4 4"/>'
        )
    for idx, (label, curve) in enumerate(loaded):
        color = colors[idx % len(colors)]
        points = " ".join(f"{sx(x):.2f},{sy(y):.2f}" for x, y in curve)
        parts.append(
            f'<polyline fill="none" stroke="{color}" stroke-width="2" points="{points}"/>'
        )
        legend_y = 55 + idx * 20
        parts.append(
            f'<rect x="{width-210}" y="{legend_y-11}" width="14" height="3" fill="{color}"/>'
        )
        parts.append(
            f'<text x="{width-190}" y="{legend_y-6}" font-family="Arial" font-size="12">{escape(label)}</text>'
        )
    parts.append("</svg>")
    path.write_text("\n".join(parts), encoding="utf-8")


def table_for(rows: list[dict[str, object]]) -> str:
    lines = [
        "| Level | Work/rev equiv (J) | Avg torque (Nm) | Peak + (Nm) | Peak - (Nm) | Change vs previous |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    previous = None
    for row in rows:
        work = float(row["full_rev_work_j"])
        change = "" if previous is None else f"{pct_change(work, previous):.2f}%"
        lines.append(
            f"| {row['label']} | {work:.6f} | {float(row['average_torque_nm']):.6f} | "
            f"{float(row['max_torque_nm']):.6f} | {float(row['min_torque_nm']):.6f} | {change} |"
        )
        previous = work
    return "\n".join(lines)


def main() -> None:
    PLOT_DIR.mkdir(parents=True, exist_ok=True)
    report: dict[str, list[dict[str, object]]] = {}
    for study, entries in STUDIES.items():
        rows = []
        for label, filename in entries:
            csv_path = DATA_DIR / filename
            stats = curve_stats(csv_path)
            span = float(stats["angle_span_deg"])
            multiplier = 360.0 / span if span else 1.0
            rows.append(
                {
                    "label": label,
                    "csv": str(csv_path.relative_to(ROOT).as_posix()),
                    "full_rev_work_j": float(stats["work_j_per_rev"]) * multiplier,
                    **stats,
                }
            )
        report[study] = rows

    make_plot(
        PLOT_DIR / "femm_verification_mesh.svg",
        "Mesh Refinement Torque-Angle",
        [(row["label"], ROOT / str(row["csv"])) for row in report["mesh"]],
    )
    make_plot(
        PLOT_DIR / "femm_verification_angle.svg",
        "Angular Resolution Torque-Angle",
        [(row["label"], ROOT / str(row["csv"])) for row in report["angle"]],
    )
    make_plot(
        PLOT_DIR / "femm_verification_boundary.svg",
        "Boundary Sensitivity Torque-Angle",
        [(row["label"], ROOT / str(row["csv"])) for row in report["boundary"]],
    )
    make_plot(
        PLOT_DIR / "femm_verification_reverse.svg",
        "Forward vs Reverse Torque-Angle",
        [(row["label"], ROOT / str(row["csv"])) for row in report["reverse"]],
    )

    final_values = [
        row["full_rev_work_j"]
        for rows in report.values()
        for row in rows
        if row["label"] not in {"coarse", "2deg", "260mm"}
    ]
    uncertainty = (max(final_values) - min(final_values)) / 2.0 if final_values else math.nan
    center = sum(final_values) / len(final_values) if final_values else math.nan

    SUMMARY_PATH.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    md = [
        "# FEMM Verification Report",
        "",
        "Date: 2026-06-15",
        "",
        "Objective: attempt to falsify the positive net-work result for the current anti-cancellation geometry before further optimization.",
        "",
        "All sweeps use the same 45 degree repeat period and report a full-revolution equivalent by multiplying the integrated 45 degree work by 8.",
        "",
        "## Mesh Refinement Study",
        "",
        table_for(report["mesh"]),
        "",
        "![Mesh refinement](plots/femm_verification_mesh.svg)",
        "",
        "## Angular Resolution Study",
        "",
        table_for(report["angle"]),
        "",
        "![Angular resolution](plots/femm_verification_angle.svg)",
        "",
        "## Boundary Sensitivity Study",
        "",
        table_for(report["boundary"]),
        "",
        "![Boundary sensitivity](plots/femm_verification_boundary.svg)",
        "",
        "## Reverse Sweep Validation",
        "",
        table_for(report["reverse"]),
        "",
        "![Reverse sweep](plots/femm_verification_reverse.svg)",
        "",
        "## Numerical Uncertainty",
        "",
        f"Estimated full-rev equivalent center across non-coarse/non-baseline checks: {center:.6f} J/rev.",
        f"Half-range uncertainty estimate: +/- {uncertainty:.6f} J/rev.",
        "",
        "## Confidence Assessment",
        "",
        "This report is generated from raw FEMM CSV files and is intended to falsify, not improve, the result. Interpret the final assessment from the tables above.",
    ]
    REPORT_PATH.write_text("\n".join(md) + "\n", encoding="utf-8")
    print(REPORT_PATH)


if __name__ == "__main__":
    main()
