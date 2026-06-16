from __future__ import annotations

import argparse
import csv
import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from validation.analyze_femm_sweeps import curve_stats  # noqa: E402


def full_rev_equivalent(stats: dict[str, float | str]) -> float:
    span = float(stats["angle_span_deg"])
    multiplier = 360.0 / span if span else 1.0
    return float(stats["work_j_per_rev"]) * multiplier


def cancellation_ratio(stats: dict[str, float | str]) -> float:
    positive = float(stats["positive_work_j"])
    negative = abs(float(stats["negative_work_j"]))
    gross = positive + negative
    net = positive - negative
    return 1.0 - abs(net) / gross if gross else math.nan


def promotion_decision(stats: dict[str, float | str]) -> str:
    full_rev = full_rev_equivalent(stats)
    peak_pos = float(stats["max_torque_nm"])
    peak_neg = abs(float(stats["min_torque_nm"]))
    cancel = cancellation_ratio(stats)
    if full_rev >= 3.0 and peak_pos > peak_neg * 1.2 and cancel < 0.85:
        return "PROMOTE_TO_MESH_REFINEMENT"
    if full_rev > 1.0 and peak_pos >= peak_neg:
        return "HOLD_FOR_NEARBY_VARIANTS"
    if full_rev > 0.0:
        return "WEAK_POSITIVE_DO_NOT_PROMOTE"
    return "REJECT_OR_REWORK"


def main() -> None:
    parser = argparse.ArgumentParser(description="Rank FEMM torque-angle variant CSVs.")
    parser.add_argument("csvs", nargs="*", type=Path)
    parser.add_argument("--json-out", type=Path, default=None)
    parser.add_argument("--csv-out", type=Path, default=None)
    args = parser.parse_args()

    paths = args.csvs or sorted((ROOT / "data" / "field_sim").glob("femm_*period45_step1.csv"))
    rows = []
    for path in paths:
        stats = curve_stats(path)
        full_rev = full_rev_equivalent(stats)
        row = {
            "csv": str(path.as_posix()),
            "full_rev_equiv_j": full_rev,
            "work_45deg_j": float(stats["work_j_per_rev"]),
            "average_torque_nm": float(stats["average_torque_nm"]),
            "peak_positive_nm": float(stats["max_torque_nm"]),
            "peak_negative_nm": float(stats["min_torque_nm"]),
            "positive_work_j": float(stats["positive_work_j"]),
            "negative_work_j": float(stats["negative_work_j"]),
            "cancellation_ratio": cancellation_ratio(stats),
            "decision": promotion_decision(stats),
        }
        rows.append(row)
    rows.sort(key=lambda item: item["full_rev_equiv_j"], reverse=True)

    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(json.dumps(rows, indent=2) + "\n", encoding="utf-8")
    if args.csv_out:
        args.csv_out.parent.mkdir(parents=True, exist_ok=True)
        with args.csv_out.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0]) if rows else [])
            writer.writeheader()
            writer.writerows(rows)

    print(json.dumps(rows, indent=2))


if __name__ == "__main__":
    main()
