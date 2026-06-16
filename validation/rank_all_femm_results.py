from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from validation.analyze_femm_sweeps import curve_stats  # noqa: E402
from validation.rank_femm_variants import (  # noqa: E402
    cancellation_ratio,
    full_rev_equivalent,
    promotion_decision,
)


def label_for(path: Path) -> str:
    name = path.stem.removeprefix("femm_")
    name = re.sub(r"_period45_step1$", "", name)
    return name.replace("_", " ")


def row_for(path: Path) -> dict[str, float | str]:
    stats = curve_stats(path)
    span = float(stats["angle_span_deg"])
    gross_pos = float(stats["positive_work_j"])
    gross_neg = abs(float(stats["negative_work_j"]))
    gross_total = gross_pos + gross_neg
    complete_period = span >= 44.9
    decision = promotion_decision(stats) if complete_period else "INCOMPLETE_SWEEP_IGNORE"
    return {
        "label": label_for(path),
        "csv": str(path.as_posix()),
        "angle_span_deg": span,
        "screen_status": "complete_period" if complete_period else "incomplete_period",
        "work_period_j": float(stats["work_j_per_rev"]),
        "full_rev_equiv_j": full_rev_equivalent(stats),
        "average_torque_nm": float(stats["average_torque_nm"]),
        "peak_positive_nm": float(stats["max_torque_nm"]),
        "peak_positive_deg": float(stats["max_torque_angle_deg"]),
        "peak_negative_nm": float(stats["min_torque_nm"]),
        "peak_negative_deg": float(stats["min_torque_angle_deg"]),
        "positive_gross_work_j": gross_pos,
        "negative_gross_work_abs_j": gross_neg,
        "gross_work_j": gross_total,
        "net_to_gross_ratio": abs(float(stats["work_j_per_rev"])) / gross_total if gross_total else 0.0,
        "cancellation_ratio": cancellation_ratio(stats),
        "closure_delta_nm": float(stats["closure_delta_nm"]),
        "decision": decision,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Rank all solved FEMM first-screen CSVs.")
    parser.add_argument(
        "--glob",
        default="femm_*period45_step1.csv",
        help="Glob under data/field_sim. Default excludes verification sweeps.",
    )
    parser.add_argument("--json-out", type=Path, default=ROOT / "reports/all_femm_rankings_latest.json")
    parser.add_argument("--csv-out", type=Path, default=ROOT / "reports/all_femm_rankings_latest.csv")
    args = parser.parse_args()

    paths = sorted((ROOT / "data" / "field_sim").glob(args.glob))
    rows = [row_for(path) for path in paths]
    rows.sort(
        key=lambda item: (
            item["screen_status"] == "complete_period",
            float(item["full_rev_equiv_j"]),
        ),
        reverse=True,
    )

    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    args.json_out.write_text(json.dumps(rows, indent=2) + "\n", encoding="utf-8")
    with args.csv_out.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]) if rows else [])
        writer.writeheader()
        writer.writerows(rows)
    print(json.dumps(rows, indent=2))


if __name__ == "__main__":
    main()
