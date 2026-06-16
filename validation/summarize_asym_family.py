from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from validation.analyze_femm_sweeps import curve_stats  # noqa: E402
from validation.rank_femm_variants import cancellation_ratio, full_rev_equivalent, promotion_decision  # noqa: E402


VARIANTS = [
    ("ASYM_A", "asym_a_lead1p5_trail142", "data/field_sim/femm_asym_a_period45_step1.csv"),
    ("ASYM_B", "asym_b_lead2p0_trail140", "data/field_sim/femm_asym_b_period45_step1.csv"),
    ("ASYM_C", "asym_c_lead2p5_trail138", "data/field_sim/femm_asym_c_period45_step1.csv"),
    ("ASYM_D", "asym_d_lead3p0_trail137", "data/field_sim/femm_asym_d_period45_step1.csv"),
]


def summarize(label: str, config_name: str, csv_rel: str) -> dict:
    path = ROOT / csv_rel
    stats = curve_stats(path)
    full_rev = full_rev_equivalent(stats)
    return {
        "label": label,
        "config_name": config_name,
        "csv": csv_rel,
        "work_45deg_j": float(stats["work_j_per_rev"]),
        "full_rev_equiv_j": full_rev,
        "average_torque_nm": float(stats["average_torque_nm"]),
        "peak_positive_nm": float(stats["max_torque_nm"]),
        "peak_positive_deg": float(stats["max_torque_angle_deg"]),
        "peak_negative_nm": float(stats["min_torque_nm"]),
        "peak_negative_deg": float(stats["min_torque_angle_deg"]),
        "cancellation_ratio": cancellation_ratio(stats),
        "decision": promotion_decision(stats),
        "femm_status": "solved",
    }


def main() -> None:
    rows = [summarize(*item) for item in VARIANTS]
    rows.sort(key=lambda item: item["full_rev_equiv_j"], reverse=True)
    print(json.dumps(rows, indent=2))


if __name__ == "__main__":
    main()