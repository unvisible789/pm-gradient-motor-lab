from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from validation.femm_geometry_builder import (  # noqa: E402
    default_geometry_config,
    render_pm_gradient_motor_lua,
)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Write a FEMM geometry variant without changing motor design intent."
    )
    parser.add_argument("--label", required=True)
    parser.add_argument("--config-json", default=None)
    parser.add_argument("--air-boundary-radius-mm", type=float, default=None)
    parser.add_argument("--block-mesh-size-mm", type=float, default=None)
    parser.add_argument("--segment-mesh-size-mm", type=float, default=None)
    parser.add_argument("--arc-max-segment-deg", type=float, default=None)
    args = parser.parse_args()

    if args.config_json:
        config = json.loads((ROOT / args.config_json).read_text(encoding="utf-8"))
    else:
        config = default_geometry_config()
    config["verification_label"] = args.label
    if args.air_boundary_radius_mm is not None:
        config["air_boundary_radius_mm"] = args.air_boundary_radius_mm
    if args.block_mesh_size_mm is not None:
        config["block_mesh_size_mm"] = args.block_mesh_size_mm
    if args.segment_mesh_size_mm is not None:
        config["segment_mesh_size_mm"] = args.segment_mesh_size_mm
    if args.arc_max_segment_deg is not None:
        config["arc_max_segment_deg"] = args.arc_max_segment_deg

    geometry_dir = ROOT / "geometry"
    femm_dir = ROOT / "field_sim" / "femm"
    geometry_dir.mkdir(parents=True, exist_ok=True)
    femm_dir.mkdir(parents=True, exist_ok=True)

    (geometry_dir / "pm_gradient_motor_config.json").write_text(
        json.dumps(config, indent=2) + "\n",
        encoding="utf-8",
    )
    (femm_dir / "build_pm_gradient_motor.lua").write_text(
        render_pm_gradient_motor_lua(config),
        encoding="utf-8",
    )
    print(json.dumps(config, indent=2))


if __name__ == "__main__":
    main()
