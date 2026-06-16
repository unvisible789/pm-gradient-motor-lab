"""Rank full ASYM_B EML angular offset first-screen sweep."""

from __future__ import annotations

import csv
import json
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

OFFSETS = [-12, -6, 0, 6, 9, 12, 15, 18, 21]


def offset_tag(deg: int) -> str:
    if deg < 0:
        return f"neg{abs(deg)}"
    if deg > 0:
        return f"pos{deg}"
    return "zero"


def csv_for_offset(deg: int) -> Path:
    if deg == 0:
        return ROOT / "data/field_sim/femm_asym_b_period45_step1.csv"
    return ROOT / f"data/field_sim/femm_asym_b_eml_offset_{offset_tag(deg)}_period45_step1.csv"


def main() -> None:
    rows = []
    for offset in OFFSETS:
        path = csv_for_offset(offset)
        if not path.exists():
            rows.append({"eml_offset_deg": offset, "csv": str(path), "femm_status": "missing"})
            continue
        stats = curve_stats(path)
        complete_period = float(stats["angle_span_deg"]) >= 44.9
        rows.append(
            {
                "eml_offset_deg": offset,
                "csv": str(path.as_posix()),
                "angle_span_deg": float(stats["angle_span_deg"]),
                "work_45deg_j": float(stats["work_j_per_rev"]),
                "full_rev_equiv_j": full_rev_equivalent(stats),
                "peak_positive_nm": float(stats["max_torque_nm"]),
                "peak_negative_nm": float(stats["min_torque_nm"]),
                "positive_gross_work_j": float(stats["positive_work_j"]),
                "negative_gross_work_j": float(stats["negative_work_j"]),
                "cancellation_ratio": cancellation_ratio(stats),
                "decision": promotion_decision(stats) if complete_period else "INCOMPLETE_SWEEP_IGNORE",
                "femm_status": "solved" if complete_period else "incomplete",
            }
        )
    rows.sort(
        key=lambda r: (
            r.get("femm_status") == "solved",
            r.get("full_rev_equiv_j", float("-inf")),
        ),
        reverse=True,
    )

    out_json = ROOT / "reports/eml_offset_rankings_latest.json"
    out_csv = ROOT / "reports/eml_offset_rankings_latest.csv"
    out_json.write_text(json.dumps(rows, indent=2) + "\n", encoding="utf-8")
    solved = [r for r in rows if r.get("femm_status") == "solved"]
    if solved:
        with out_csv.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(solved[0].keys()))
            writer.writeheader()
            writer.writerows(solved)
    print(json.dumps(rows, indent=2))


if __name__ == "__main__":
    main()
