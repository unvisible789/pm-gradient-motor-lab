"""Write Priority 2-4 optimization variant JSON configs on ASYM_B + EML +12 base."""

from __future__ import annotations

import json
import sys
from copy import deepcopy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from validation.femm_geometry_builder import default_geometry_config  # noqa: E402

VARIANT_DIR = ROOT / "field_sim" / "femm" / "variants"
MATRIX_PATH = ROOT / "field_sim" / "femm" / "optimization_variant_matrix.json"


def asym_b_plus12_base() -> dict:
    base = default_geometry_config()
    asym = json.loads((VARIANT_DIR / "asym_b_lead2p0_trail140.json").read_text(encoding="utf-8"))
    cfg = {**base, **asym}
    cfg["eml_angular_offset_deg"] = 12.0
    return cfg


def write_variant(name: str, purpose: str, overrides: dict) -> Path:
    cfg = deepcopy(asym_b_plus12_base())
    cfg.update(overrides)
    cfg["variant_name"] = name
    cfg["variant_purpose"] = purpose
    path = VARIANT_DIR / f"{name}.json"
    path.write_text(json.dumps(cfg, indent=2) + "\n", encoding="utf-8")
    return path


def main() -> None:
    VARIANT_DIR.mkdir(parents=True, exist_ok=True)
    variants = []

    # Priority 2: narrower EML pole face
    for pct, arc in [(10, 12.6), (20, 11.2), (30, 9.8)]:
        name = f"opt_eml_arc_minus{pct}pct"
        write_variant(
            name,
            f"Narrow EML pole arc by {pct}% to reduce backward pull.",
            {"eml_arc_deg": arc},
        )
        variants.append({"name": name, "priority": 2, "purpose": f"EML arc -{pct}%"})

    # Priority 2: forward-biased EML pole shoe
    for tag, lead, trail, t_outer in [
        ("mild", 1.0, 1.0, 203.0),
        ("moderate", 2.0, 2.0, 200.0),
    ]:
        name = f"opt_eml_asym_{tag}"
        write_variant(
            name,
            f"Forward-biased EML pole shoe ({tag}).",
            {
                "eml_asymmetric_pole_enabled": True,
                "eml_leading_extension_deg": lead,
                "eml_trailing_pullback_deg": trail,
                "eml_leading_outer_radius_mm": 205.0,
                "eml_trailing_outer_radius_mm": t_outer,
            },
        )
        variants.append({"name": name, "priority": 2, "purpose": f"EML asymmetric pole {tag}"})

    # Priority 2: radial gap tuning
    for tag, inner in [("gap_minus1mm", 157.0), ("gap_plus1mm", 159.0)]:
        name = f"opt_stator_inner_{tag}"
        write_variant(
            name,
            f"EML radial gap tuning: stator_inner_radius_mm={inner}.",
            {"stator_inner_radius_mm": inner},
        )
        variants.append({"name": name, "priority": 2, "purpose": f"stator inner {inner} mm"})

    # Priority 3: stator back-iron shunt
    for tag, offset in [("leading", 6.0), ("center", 0.0)]:
        name = f"opt_stator_shunt_{tag}"
        write_variant(
            name,
            f"Stator back-iron shunt behind EML ({tag} offset).",
            {
                "stator_shunt_enabled": True,
                "stator_shunt_offset_deg": offset,
                "stator_shunt_arc_deg": 8.0,
            },
        )
        variants.append({"name": name, "priority": 3, "purpose": f"stator shunt {tag}"})

    # Priority 3: trailing-side stator air relief
    for arc in [2.0, 3.0, 4.0]:
        name = f"opt_stator_relief_{int(arc)}deg"
        write_variant(
            name,
            f"Trailing-side stator air relief slot ({arc} deg).",
            {
                "stator_flux_relief_arc_deg": arc,
                "stator_flux_relief_offset_deg": -9.0,
            },
        )
        variants.append({"name": name, "priority": 3, "purpose": f"stator relief {arc} deg"})

    MATRIX_PATH.write_text(
        json.dumps(
            {
                "base": "ASYM_B + EML offset +12 deg",
                "protocol": [
                    "45 deg period, 1 deg step first screen.",
                    "Do not mesh-refine below 3 J/rev gate.",
                ],
                "variants": variants,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    print(f"Wrote {len(variants)} variants to {VARIANT_DIR}")
    print(f"Wrote matrix {MATRIX_PATH}")


if __name__ == "__main__":
    main()