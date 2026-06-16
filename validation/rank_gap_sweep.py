"""Rank stator gap sweep and top existing candidates."""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from validation.rank_all_femm_results import row_for  # noqa: E402

CANDIDATES = [
    ("ASYM_B +12 offset", "data/field_sim/femm_asym_b_eml_offset_pos12_period45_step1.csv"),
    ("gap 158.5", "data/field_sim/femm_opt_gap_158p5_period45_step1.csv"),
    ("gap 159.0", "data/field_sim/femm_opt_gap_159p0_period45_step1.csv"),
    ("gap 159.5", "data/field_sim/femm_opt_gap_159p5_period45_step1.csv"),
    ("gap 160.0", "data/field_sim/femm_opt_gap_160p0_period45_step1.csv"),
    ("gap 161.0", "data/field_sim/femm_opt_gap_161p0_period45_step1.csv"),
    ("gap+1mm legacy", "data/field_sim/femm_opt_opt_stator_inner_gap_plus1mm_period45_step1.csv"),
    ("EML arc -20%", "data/field_sim/femm_opt_opt_eml_arc_minus20pct_period45_step1.csv"),
    ("gap159 + Halbach15", "data/field_sim/femm_opt_combo_gap159_halbach15_period45_step1.csv"),
    ("gap159 + arc -10%", "data/field_sim/femm_opt_combo_gap159_arc10_period45_step1.csv"),
    ("gap159 + arc -20%", "data/field_sim/femm_opt_combo_gap159_arc20_period45_step1.csv"),
]


def main() -> None:
    rows = []
    for label, rel in CANDIDATES:
        path = ROOT / rel
        if not path.exists():
            rows.append({"label": label, "csv": rel, "screen_status": "missing"})
            continue
        row = row_for(path)
        row["label"] = label
        rows.append(row)
    rows.sort(
        key=lambda r: (r.get("screen_status") == "complete_period", r.get("full_rev_equiv_j", -1)),
        reverse=True,
    )
    out_json = ROOT / "reports/gap_sweep_rankings_latest.json"
    out_csv = ROOT / "reports/gap_sweep_rankings_latest.csv"
    out_json.write_text(json.dumps(rows, indent=2) + "\n", encoding="utf-8")
    solved = [r for r in rows if r.get("screen_status") == "complete_period"]
    if solved:
        with out_csv.open("w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(solved[0].keys()))
            w.writeheader()
            w.writerows(solved)
    print(json.dumps(rows, indent=2))


if __name__ == "__main__":
    main()