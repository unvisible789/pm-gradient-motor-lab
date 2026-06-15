from __future__ import annotations

import json
import math
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def default_geometry_config() -> dict[str, Any]:
    return {
        "model_name": "pm_gradient_motor_base",
        "output_fem_file": "geometry/pm_gradient_motor_base.fem",
        "rotor_diameter_mm": 300.0,
        "rotor_core_radius_mm": 110.0,
        "rotor_magnet_inner_radius_mm": 120.0,
        "rotor_magnet_outer_radius_mm": 145.0,
        "rotor_gradient_count": 16,
        "rotor_magnet_arc_deg": 12.0,
        "stator_inner_radius_mm": 158.0,
        "stator_outer_radius_mm": 205.0,
        "eml_unit_count": 8,
        "eml_arc_deg": 18.0,
        "air_boundary_radius_mm": 260.0,
        "depth_mm": 25.0,
        "rotor_group": 2,
        "stator_group": 1,
        "coil_group": 3,
        "magnet_material": "NdFeB 40 MGOe",
        "rotor_core_material": "1010 Steel",
        "stator_core_material": "1010 Steel",
        "coil_material": "Copper",
        "air_material": "Air",
        "current_density_ma_per_mm2": 0.0,
    }


def validate_geometry_config(config: dict[str, Any]) -> None:
    if float(config["rotor_diameter_mm"]) <= 0:
        raise ValueError("rotor_diameter_mm must be positive")
    if int(config["rotor_gradient_count"]) != int(config["eml_unit_count"]) * 2:
        raise ValueError("Expected a 2:1 rotor-gradient to EML ratio")
    radii = [
        "rotor_core_radius_mm",
        "rotor_magnet_inner_radius_mm",
        "rotor_magnet_outer_radius_mm",
        "stator_inner_radius_mm",
        "stator_outer_radius_mm",
        "air_boundary_radius_mm",
    ]
    values = [float(config[name]) for name in radii]
    if values != sorted(values):
        raise ValueError("Radii must increase from rotor core to air boundary")


def _polar(radius: float, angle_deg: float) -> tuple[float, float]:
    angle_rad = math.radians(angle_deg)
    return radius * math.cos(angle_rad), radius * math.sin(angle_rad)


def _lua_string(value: str) -> str:
    return '"' + value.replace("\\", "/").replace('"', '\\"') + '"'


def _arc_segment_lua(
    *,
    center_angle: float,
    arc_deg: float,
    inner_radius: float,
    outer_radius: float,
    label_radius: float,
    material: str,
    group: int,
    magnetization_deg: float | None = None,
    turns: int = 0,
) -> str:
    start = center_angle - arc_deg / 2.0
    end = center_angle + arc_deg / 2.0
    points = {
        "outer_start": _polar(outer_radius, start),
        "outer_end": _polar(outer_radius, end),
        "inner_start": _polar(inner_radius, start),
        "inner_end": _polar(inner_radius, end),
        "outer_mid": _polar(outer_radius, center_angle),
        "inner_mid": _polar(inner_radius, center_angle),
        "label": _polar(label_radius, center_angle),
    }
    radial_start_mid = (
        (points["outer_start"][0] + points["inner_start"][0]) / 2.0,
        (points["outer_start"][1] + points["inner_start"][1]) / 2.0,
    )
    radial_end_mid = (
        (points["outer_end"][0] + points["inner_end"][0]) / 2.0,
        (points["outer_end"][1] + points["inner_end"][1]) / 2.0,
    )
    mag_dir = 0.0 if magnetization_deg is None else magnetization_deg
    material_lua = _lua_string(material)
    return f"""
add_arc_segment({points['outer_start'][0]:.6f}, {points['outer_start'][1]:.6f}, {points['outer_end'][0]:.6f}, {points['outer_end'][1]:.6f}, {arc_deg:.6f}, 1)
add_arc_segment({points['inner_end'][0]:.6f}, {points['inner_end'][1]:.6f}, {points['inner_start'][0]:.6f}, {points['inner_start'][1]:.6f}, {arc_deg:.6f}, 1)
add_line({points['outer_start'][0]:.6f}, {points['outer_start'][1]:.6f}, {points['inner_start'][0]:.6f}, {points['inner_start'][1]:.6f})
add_line({points['inner_end'][0]:.6f}, {points['inner_end'][1]:.6f}, {points['outer_end'][0]:.6f}, {points['outer_end'][1]:.6f})
mi_selectarcsegment({points['outer_mid'][0]:.6f}, {points['outer_mid'][1]:.6f})
mi_setarcsegmentprop(1, "<None>", 0, {group})
mi_clearselected()
mi_selectarcsegment({points['inner_mid'][0]:.6f}, {points['inner_mid'][1]:.6f})
mi_setarcsegmentprop(1, "<None>", 0, {group})
mi_clearselected()
mi_selectsegment({radial_start_mid[0]:.6f}, {radial_start_mid[1]:.6f})
mi_setsegmentprop("<None>", 0, 1, 0, {group})
mi_clearselected()
mi_selectsegment({radial_end_mid[0]:.6f}, {radial_end_mid[1]:.6f})
mi_setsegmentprop("<None>", 0, 1, 0, {group})
mi_clearselected()
mi_addblocklabel({points['label'][0]:.6f}, {points['label'][1]:.6f})
mi_selectlabel({points['label'][0]:.6f}, {points['label'][1]:.6f})
mi_setblockprop({material_lua}, 1, 0, "<None>", {mag_dir:.6f}, {group}, {turns})
mi_clearselected()
"""


def render_pm_gradient_motor_lua(config: dict[str, Any]) -> str:
    validate_geometry_config(config)
    rotor_count = int(config["rotor_gradient_count"])
    eml_count = int(config["eml_unit_count"])
    rotor_group = int(config["rotor_group"])
    stator_group = int(config["stator_group"])
    coil_group = int(config["coil_group"])
    magnet_material = str(config["magnet_material"])
    rotor_core_material = str(config["rotor_core_material"])
    stator_core_material = str(config["stator_core_material"])
    coil_material = str(config["coil_material"])
    output_fem_file = _lua_string(str(config["output_fem_file"]))

    lines = [
        "-- PM Gradient Motor Lab FEMM geometry builder",
        "-- Radial-flux 2D approximation of the described disc/axial concept.",
        "newdocument(0)",
        f'mi_probdef(0, "millimeters", "planar", 1e-8, {float(config["depth_mm"]):.6f}, 30)',
        "",
        f"rotor_group = {rotor_group}",
        f"stator_group = {stator_group}",
        f"coil_group = {coil_group}",
        "",
        "mi_getmaterial(\"Air\")",
        f"mi_getmaterial({_lua_string(magnet_material)})",
        f"mi_getmaterial({_lua_string(rotor_core_material)})",
        f"mi_getmaterial({_lua_string(stator_core_material)})",
        f"mi_getmaterial({_lua_string(coil_material)})",
        "",
        "function add_line(x1, y1, x2, y2)",
        "  mi_addnode(x1, y1)",
        "  mi_addnode(x2, y2)",
        "  mi_addsegment(x1, y1, x2, y2)",
        "end",
        "",
        "function add_arc_segment(x1, y1, x2, y2, angle, maxseg)",
        "  mi_addnode(x1, y1)",
        "  mi_addnode(x2, y2)",
        "  mi_addarc(x1, y1, x2, y2, angle, maxseg)",
        "end",
        "",
        "-- Air boundary",
        f"mi_drawarc({float(config['air_boundary_radius_mm']):.6f}, 0, {-float(config['air_boundary_radius_mm']):.6f}, 0, 180, 2)",
        f"mi_drawarc({-float(config['air_boundary_radius_mm']):.6f}, 0, {float(config['air_boundary_radius_mm']):.6f}, 0, 180, 2)",
        f"mi_addblocklabel({float(config['air_boundary_radius_mm']) - 10.0:.6f}, 0)",
        f"mi_selectlabel({float(config['air_boundary_radius_mm']) - 10.0:.6f}, 0)",
        'mi_setblockprop("Air", 1, 0, "<None>", 0, 0, 0)',
        "mi_clearselected()",
        "",
        "-- Rotor core",
        f"mi_drawarc({float(config['rotor_core_radius_mm']):.6f}, 0, {-float(config['rotor_core_radius_mm']):.6f}, 0, 180, 2)",
        f"mi_drawarc({-float(config['rotor_core_radius_mm']):.6f}, 0, {float(config['rotor_core_radius_mm']):.6f}, 0, 180, 2)",
        f"mi_selectarcsegment(0, {float(config['rotor_core_radius_mm']):.6f})",
        "mi_setarcsegmentprop(2, \"<None>\", 0, rotor_group)",
        "mi_clearselected()",
        f"mi_selectarcsegment(0, {-float(config['rotor_core_radius_mm']):.6f})",
        "mi_setarcsegmentprop(2, \"<None>\", 0, rotor_group)",
        "mi_clearselected()",
        "mi_addblocklabel(10, 0)",
        "mi_selectlabel(10, 0)",
        f"mi_setblockprop({_lua_string(rotor_core_material)}, 1, 0, \"<None>\", 0, rotor_group, 0)",
        "mi_clearselected()",
    ]

    for index in range(rotor_count):
        angle = index * 360.0 / rotor_count
        magnetization = angle if index % 2 == 0 else angle + 180.0
        lines.append(f"-- Rotor gradient magnet {index + 1:02d}")
        lines.append(
            _arc_segment_lua(
                center_angle=angle,
                arc_deg=float(config["rotor_magnet_arc_deg"]),
                inner_radius=float(config["rotor_magnet_inner_radius_mm"]),
                outer_radius=float(config["rotor_magnet_outer_radius_mm"]),
                label_radius=(
                    float(config["rotor_magnet_inner_radius_mm"])
                    + float(config["rotor_magnet_outer_radius_mm"])
                )
                / 2.0,
                material=magnet_material,
                group=rotor_group,
                magnetization_deg=magnetization,
            )
        )

    for index in range(eml_count):
        angle = index * 360.0 / eml_count
        lines.append(f"-- EML stator unit {index + 1:02d}")
        lines.append(
            _arc_segment_lua(
                center_angle=angle,
                arc_deg=float(config["eml_arc_deg"]),
                inner_radius=float(config["stator_inner_radius_mm"]),
                outer_radius=float(config["stator_outer_radius_mm"]),
                label_radius=float(config["stator_inner_radius_mm"]) + 4.0,
                material=stator_core_material,
                group=stator_group,
            )
        )
        coil_inner = float(config["stator_inner_radius_mm"]) + 8.0
        coil_outer = float(config["stator_outer_radius_mm"]) - 8.0
        lines.append(
            _arc_segment_lua(
                center_angle=angle,
                arc_deg=float(config["eml_arc_deg"]) * 0.55,
                inner_radius=coil_inner,
                outer_radius=coil_outer,
                label_radius=(coil_inner + coil_outer) / 2.0,
                material=coil_material,
                group=coil_group,
                turns=1,
            )
        )

    lines.extend(
        [
            "",
            "mi_zoomnatural()",
            f"mi_saveas({output_fem_file})",
        ]
    )
    return "\n".join(lines) + "\n"


def write_geometry_builder(root: str | Path = ROOT) -> None:
    root = Path(root)
    geometry_dir = root / "geometry"
    workflow_dir = root / "field_sim" / "femm"
    geometry_dir.mkdir(parents=True, exist_ok=True)
    workflow_dir.mkdir(parents=True, exist_ok=True)
    config = default_geometry_config()
    (geometry_dir / "pm_gradient_motor_config.json").write_text(
        json.dumps(config, indent=2) + "\n",
        encoding="utf-8",
    )
    (workflow_dir / "build_pm_gradient_motor.lua").write_text(
        render_pm_gradient_motor_lua(config),
        encoding="utf-8",
    )


def main() -> None:
    write_geometry_builder(ROOT)
    print("Wrote geometry/pm_gradient_motor_config.json")
    print("Wrote field_sim/femm/build_pm_gradient_motor.lua")


if __name__ == "__main__":
    main()
