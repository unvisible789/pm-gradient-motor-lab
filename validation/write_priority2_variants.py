from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from validation.femm_geometry_builder import default_geometry_config  # noqa: E402


VARIANT_DIR = ROOT / "field_sim" / "femm" / "variants"
MATRIX_PATH = ROOT / "field_sim" / "femm" / "priority2_variant_matrix.json"


def variant(name: str, purpose: str, changes: dict[str, Any]) -> dict[str, Any]:
    config = default_geometry_config()
    config.update(
        {
            "variant_name": name,
            "variant_purpose": purpose,
            "asymmetric_pole_enabled": True,
            "asymmetric_leading_extension_deg": 2.0,
            "asymmetric_trailing_pullback_deg": 2.0,
            "asymmetric_leading_outer_radius_mm": 145.0,
            "asymmetric_trailing_outer_radius_mm": 140.0,
            "eml_angular_offset_deg": 12.0,
        }
    )
    config.update(changes)
    return config


def main() -> None:
    variants = [
        variant(
            "p2_eml_narrow_10",
            "ASYM_B +12 with a 10 percent narrower EML pole face.",
            {"eml_arc_deg": 12.6},
        ),
        variant(
            "p2_eml_narrow_20",
            "ASYM_B +12 with a 20 percent narrower EML pole face.",
            {"eml_arc_deg": 11.2},
        ),
        variant(
            "p2_eml_narrow_30",
            "ASYM_B +12 with a 30 percent narrower EML pole face.",
            {"eml_arc_deg": 9.8},
        ),
        variant(
            "p2_eml_bias_mild",
            "Forward-biased stator pole shoe to favor assist-window attraction.",
            {
                "eml_asymmetric_pole_enabled": True,
                "eml_leading_extension_deg": 1.5,
                "eml_trailing_pullback_deg": 1.5,
                "eml_leading_outer_radius_mm": 205.0,
                "eml_trailing_outer_radius_mm": 198.0,
            },
        ),
        variant(
            "p2_eml_bias_moderate",
            "Stronger stator pole-shoe bias; use only if mild bias is promising.",
            {
                "eml_asymmetric_pole_enabled": True,
                "eml_leading_extension_deg": 2.5,
                "eml_trailing_pullback_deg": 2.5,
                "eml_leading_outer_radius_mm": 205.0,
                "eml_trailing_outer_radius_mm": 194.0,
            },
        ),
        variant(
            "p2_stator_relief_mild",
            "Trailing-side stator air relief to weaken lockout-region pull.",
            {
                "stator_flux_relief_arc_deg": 3.0,
                "stator_flux_relief_offset_deg": 8.0,
            },
        ),
        variant(
            "p2_stator_relief_moderate",
            "Wider trailing-side stator air relief; screen after mild relief.",
            {
                "stator_flux_relief_arc_deg": 5.0,
                "stator_flux_relief_offset_deg": 8.0,
            },
        ),
        variant(
            "p2_stator_shunt_centered",
            "Back-iron shunt behind each EML to alter stator return flux.",
            {
                "stator_shunt_enabled": True,
                "stator_shunt_arc_deg": 8.0,
                "stator_shunt_offset_deg": 0.0,
            },
        ),
        variant(
            "p2_stator_shunt_leading",
            "Leading-biased back-iron shunt to favor assist-side flux closure.",
            {
                "stator_shunt_enabled": True,
                "stator_shunt_arc_deg": 8.0,
                "stator_shunt_offset_deg": -4.0,
            },
        ),
        variant(
            "p2_best_combo_mild",
            "Limited combination: narrower EML, mild pole bias, and mild stator relief.",
            {
                "eml_arc_deg": 12.6,
                "eml_asymmetric_pole_enabled": True,
                "eml_leading_extension_deg": 1.5,
                "eml_trailing_pullback_deg": 1.5,
                "eml_leading_outer_radius_mm": 205.0,
                "eml_trailing_outer_radius_mm": 198.0,
                "stator_flux_relief_arc_deg": 3.0,
                "stator_flux_relief_offset_deg": 8.0,
            },
        ),
    ]

    VARIANT_DIR.mkdir(parents=True, exist_ok=True)
    for config in variants:
        path = VARIANT_DIR / f"{config['variant_name']}.json"
        path.write_text(json.dumps(config, indent=2) + "\n", encoding="utf-8")

    MATRIX_PATH.write_text(
        json.dumps(
            {
                "objective": "Priority 2 EML/stator flux-shaping after ASYM_B +12 offset became best first-screen.",
                "baseline": "ASYM_B rotor geometry with eml_angular_offset_deg = +12.",
                "protocol": [
                    "Run 45 degree period sweeps at 1 degree first.",
                    "Do not mesh-refine unless a candidate beats +12 offset by a large margin.",
                    "Promote only above 3 J/rev equivalent or with much lower cancellation than 0.934.",
                    "Avoid combining changes until at least one individual mechanism improves cancellation.",
                ],
                "variants": [
                    {
                        "name": config["variant_name"],
                        "purpose": config["variant_purpose"],
                        "config": f"field_sim/femm/variants/{config['variant_name']}.json",
                    }
                    for config in variants
                ],
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    print(f"Wrote {len(variants)} Priority 2 variants")


if __name__ == "__main__":
    main()
