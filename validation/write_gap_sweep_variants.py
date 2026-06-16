"""Write stator inner radius gap sweep variants on ASYM_B + EML +12 base."""

from __future__ import annotations

import json
import sys
from copy import deepcopy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from validation.femm_geometry_builder import default_geometry_config  # noqa: E402

VARIANT_DIR = ROOT / "field_sim" / "femm" / "variants"
MATRIX = ROOT / "field_sim" / "femm" / "gap_sweep_variant_matrix.json"

GAPS = [
    ("158p5", 158.5),
    ("159p0", 159.0),
    ("159p5", 159.5),
    ("160p0", 160.0),
    ("161p0", 161.0),
]


def base_config() -> dict:
    asym = json.loads((VARIANT_DIR / "asym_b_lead2p0_trail140.json").read_text(encoding="utf-8"))
    return {**default_geometry_config(), **asym, "eml_angular_offset_deg": 12.0}


def main() -> None:
    VARIANT_DIR.mkdir(parents=True, exist_ok=True)
    entries = []
    for tag, inner in GAPS:
        name = f"gap_{tag}"
        cfg = deepcopy(base_config())
        cfg["stator_inner_radius_mm"] = inner
        cfg["variant_name"] = name
        cfg["variant_purpose"] = f"Stator gap sweep: stator_inner_radius_mm={inner} on ASYM_B+EML+12."
        (VARIANT_DIR / f"{name}.json").write_text(json.dumps(cfg, indent=2) + "\n", encoding="utf-8")
        entries.append(
            {
                "name": name,
                "stator_inner_radius_mm": inner,
                "output_csv": f"data/field_sim/femm_opt_gap_{tag}_period45_step1.csv",
            }
        )
    MATRIX.write_text(json.dumps({"base": "ASYM_B + EML +12", "variants": entries}, indent=2) + "\n")
    print(f"Wrote {len(entries)} gap variants")


if __name__ == "__main__":
    main()