from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from validation.femm_geometry_builder import default_geometry_config  # noqa: E402


VARIANT_DIR = ROOT / "field_sim" / "femm" / "variants"
MATRIX_PATH = ROOT / "field_sim" / "femm" / "priority1_variant_matrix.json"


def variant(name: str, purpose: str, changes: dict[str, Any]) -> dict[str, Any]:
    config = default_geometry_config()
    config.update(changes)
    config["variant_name"] = name
    config["variant_purpose"] = purpose
    return config


def main() -> None:
    variants = [
        variant(
            "p1_barrier_5deg_core",
            "Substantial rotor-core air barriers to interrupt return flux paths.",
            {
                "rotor_flux_barrier_arc_deg": 5.0,
                "rotor_flux_barrier_inner_radius_mm": 58.0,
                "rotor_flux_barrier_outer_radius_mm": 108.0,
                "block_mesh_size_mm": 3.0,
                "segment_mesh_size_mm": 3.0,
                "arc_max_segment_deg": 1.0,
            },
        ),
        variant(
            "p1_barrier_8deg_core",
            "Wider rotor-core air barriers for a stronger cancellation falsification test.",
            {
                "rotor_flux_barrier_arc_deg": 8.0,
                "rotor_flux_barrier_inner_radius_mm": 50.0,
                "rotor_flux_barrier_outer_radius_mm": 108.0,
                "block_mesh_size_mm": 3.0,
                "segment_mesh_size_mm": 3.0,
                "arc_max_segment_deg": 1.0,
            },
        ),
        variant(
            "p1_forward_biased_cap",
            "Leading-edge outer pole cap intended to strengthen forward pull and weaken trailing pull.",
            {
                "rotor_outer_pole_cap_arc_deg": 4.0,
                "rotor_outer_pole_cap_offset_deg": 3.0,
                "rotor_magnet_mid_radius_mm": 138.0,
                "block_mesh_size_mm": 3.0,
                "segment_mesh_size_mm": 3.0,
                "arc_max_segment_deg": 1.0,
            },
        ),
        variant(
            "p1_partial_halbach_15deg",
            "Partial Halbach-style magnetization bias to steer flux toward the EML side.",
            {
                "rotor_halbach_bias_deg": 15.0,
                "block_mesh_size_mm": 3.0,
                "segment_mesh_size_mm": 3.0,
                "arc_max_segment_deg": 1.0,
            },
        ),
        variant(
            "p1_barrier_plus_halbach",
            "Combined substantial barriers and partial Halbach bias; test only after individual variants solve.",
            {
                "rotor_flux_barrier_arc_deg": 5.0,
                "rotor_flux_barrier_inner_radius_mm": 58.0,
                "rotor_flux_barrier_outer_radius_mm": 108.0,
                "rotor_halbach_bias_deg": 15.0,
                "block_mesh_size_mm": 3.0,
                "segment_mesh_size_mm": 3.0,
                "arc_max_segment_deg": 1.0,
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
                "objective": "Priority 1 rotor gradient shape + flux barrier exploration",
                "protocol": [
                    "Run a 45 degree, 1 degree sweep first for each variant.",
                    "Reject variants that fail FEMM geometry/material checks.",
                    "For any positive variant, run at least medium/fine/very-fine mesh convergence before accepting.",
                    "Do not claim performance from auto-mesh-only or coarse-only results.",
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
    print(f"Wrote {len(variants)} Priority 1 variants")


if __name__ == "__main__":
    main()
