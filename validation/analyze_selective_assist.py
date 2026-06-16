"""Analyze passive torque work inside ASYM_B assist vs lockout windows."""

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
from validation.rank_femm_variants import full_rev_equivalent  # noqa: E402


def integrate_segment(curve: list[tuple[float, float]], start: float, end: float) -> float:
    if end < start:
        return 0.0
    work = 0.0
    for (angle_a, torque_a), (angle_b, torque_b) in zip(curve, curve[1:]):
        seg_start = max(angle_a, start)
        seg_end = min(angle_b, end)
        if seg_end <= seg_start:
            continue
        span = angle_b - angle_a
        if span == 0:
            continue
        frac_a = (seg_start - angle_a) / span
        frac_b = (seg_end - angle_a) / span
        torque_start = torque_a + (torque_b - torque_a) * frac_a
        torque_end = torque_a + (torque_b - torque_a) * frac_b
        work += (torque_start + torque_end) / 2.0 * math.radians(seg_end - seg_start)
    return work


def window_span_deg(windows: list[dict[str, float]]) -> float:
    return sum(max(0.0, w["end_deg"] - w["start_deg"]) for w in windows)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", type=Path, default=ROOT / "data/field_sim/femm_asym_b_period45_step1.csv")
    parser.add_argument("--windows", type=Path, default=ROOT / "field_sim/femm/pulse_strategy.asym_b.json")
    parser.add_argument("--out", type=Path, default=ROOT / "reports/asym_b_selective_assist_analysis.md")
    args = parser.parse_args()

    curve = load_curve(args.csv)
    stats = curve_stats(args.csv)
    payload = json.loads(args.windows.read_text(encoding="utf-8"))
    assist = payload["positive_torque_windows_per_45deg_period"]
    lockout = payload["negative_torque_lockout_windows_per_45deg_period"]

    assist_work = sum(integrate_segment(curve, w["start_deg"], w["end_deg"]) for w in assist)
    lockout_work = sum(integrate_segment(curve, w["start_deg"], w["end_deg"]) for w in lockout)
    total_work = float(stats["work_j_per_rev"])
    positive_gross = float(stats["positive_work_j"])
    negative_gross = abs(float(stats["negative_work_j"]))
    gross_work = positive_gross + negative_gross
    period_span = curve[-1][0] - curve[0][0]
    assist_span = window_span_deg(assist)
    lockout_span = window_span_deg(lockout)
    f_neg = lockout_span / period_span if period_span else math.nan
    assist_gross_share = assist_work / gross_work if gross_work else math.nan
    lockout_gross_share = lockout_work / gross_work if gross_work else math.nan

    report = f"""# ASYM_B Selective Assist Analysis

**Source CSV:** `{args.csv.as_posix()}`
**Pulse windows:** `{args.windows.as_posix()}`

First screen only; not mesh-converged. No performance claims.

## Passive Torque Work Over 45°

| Region | Angle span (deg) | Integrated work (J) |
|--------|-----------------:|--------------------:|
| Assist windows | {assist_span:.1f} | {assist_work:.6f} |
| Lockout windows | {lockout_span:.1f} | {lockout_work:.6f} |
| Full 45° period | {period_span:.1f} | {total_work:.6f} |

Full-revolution equivalent (×8): **{full_rev_equivalent(stats):.6f} J/rev**

## Assist / Lockout Windows

**Assist:** {", ".join(f"{w['start_deg']:.1f}–{w['end_deg']:.1f}°" for w in assist)}

**Lockout:** {", ".join(f"{w['start_deg']:.1f}–{w['end_deg']:.1f}°" for w in lockout)}

## Control Metrics

| Metric | Value |
|--------|------:|
| Negative-angle fraction (`f_neg`) | {f_neg:.3f} |
| Gross positive work over 45° (J) | {positive_gross:.6f} |
| Gross negative work over 45° (J) | {negative_gross:.6f} |
| Assist work / gross work | {assist_gross_share:.3f} |
| Lockout work / gross work | {lockout_gross_share:.3f} |

## Interpretation

Selective pulsing should fire only in assist windows and remain off during lockout windows.
Lockout regions still carry {lockout_work:.6f} J of passive torque work over 45°; pulsing there would waste electrical input unless coil energization changes the local torque balance.

This analysis does not include energized EML coil effects or electrical pulse energy accounting.
"""
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(report, encoding="utf-8")
    print(report)


if __name__ == "__main__":
    main()