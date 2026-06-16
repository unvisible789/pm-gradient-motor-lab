from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from validation.analyze_femm_sweeps import curve_stats  # noqa: E402
from validation.rank_femm_variants import cancellation_ratio, full_rev_equivalent, promotion_decision  # noqa: E402


def row(label: str, csv_rel: str, extra: dict | None = None) -> dict:
    stats = curve_stats(ROOT / csv_rel)
    item = {
        "label": label,
        "csv": csv_rel,
        "work_45deg_j": float(stats["work_j_per_rev"]),
        "full_rev_equiv_j": full_rev_equivalent(stats),
        "average_torque_nm": float(stats["average_torque_nm"]),
        "peak_positive_nm": float(stats["max_torque_nm"]),
        "peak_positive_deg": float(stats["max_torque_angle_deg"]),
        "peak_negative_nm": float(stats["min_torque_nm"]),
        "peak_negative_deg": float(stats["min_torque_angle_deg"]),
        "cancellation_ratio": cancellation_ratio(stats),
        "decision": promotion_decision(stats),
        "femm_status": "solved",
    }
    if extra:
        item.update(extra)
    return item


def main() -> None:
    eml = [
        row("ASYM_B offset 0°", "data/field_sim/femm_asym_b_period45_step1.csv", {"eml_offset_deg": 0}),
        row("ASYM_B offset -12°", "data/field_sim/femm_asym_b_eml_offset_neg12_period45_step1.csv", {"eml_offset_deg": -12}),
        row("ASYM_B offset -6°", "data/field_sim/femm_asym_b_eml_offset_neg6_period45_step1.csv", {"eml_offset_deg": -6}),
        row("ASYM_B offset +6°", "data/field_sim/femm_asym_b_eml_offset_pos6_period45_step1.csv", {"eml_offset_deg": 6}),
        row("ASYM_B offset +12°", "data/field_sim/femm_asym_b_eml_offset_pos12_period45_step1.csv", {"eml_offset_deg": 12}),
    ]
    teb = [
        row("TEB_A", "data/field_sim/femm_teb_a_period45_step1.csv"),
        row("TEB_B", "data/field_sim/femm_teb_b_period45_step1.csv"),
        row("TEB_C", "data/field_sim/femm_teb_c_period45_step1.csv"),
        row("TEB_D", "data/field_sim/femm_teb_d_period45_step1.csv"),
    ]
    eml.sort(key=lambda x: x["full_rev_equiv_j"], reverse=True)
    teb.sort(key=lambda x: x["full_rev_equiv_j"], reverse=True)
    print(json.dumps({"eml_offset_sweep": eml, "teb_family": teb}, indent=2))


if __name__ == "__main__":
    main()