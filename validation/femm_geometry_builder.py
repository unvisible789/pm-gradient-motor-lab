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
        "design_variant": "anti_cancellation_v1",
        "rotor_diameter_mm": 300.0,
        "rotor_core_radius_mm": 110.0,
        "rotor_magnet_inner_radius_mm": 120.0,
        "rotor_magnet_mid_radius_mm": 145.0,
        "rotor_magnet_outer_radius_mm": 146.0,
        "rotor_gradient_count": 16,
        "rotor_magnet_arc_deg": 10.0,
        "rotor_magnet_leading_edge_bias_deg": 0.0,
        "rotor_halbach_bias_deg": 0.0,
        # TEB_B mode: a near-air-gap air slot behind each magnet trailing edge.
        "trailing_edge_barrier_enabled": False,
        "trailing_edge_barrier_arc_deg": 3.0,
        "trailing_edge_barrier_inner_radius_mm": 132.0,
        "trailing_edge_barrier_outer_radius_mm": 145.0,
        "trailing_edge_barrier_gap_deg": 0.0,
        # ASYM_B mode: one asymmetric magnet polygon, no separate pole cap.
        "asymmetric_pole_enabled": False,
        "asymmetric_leading_extension_deg": 2.0,
        "asymmetric_trailing_pullback_deg": 2.0,
        "asymmetric_leading_outer_radius_mm": 145.0,
        "asymmetric_trailing_outer_radius_mm": 140.0,
        "rotor_outer_pole_cap_arc_deg": 0.0,
        "rotor_outer_pole_cap_offset_deg": 2.0,
        "rotor_flux_barrier_inner_radius_mm": 76.0,
        "rotor_flux_barrier_outer_radius_mm": 106.0,
        "rotor_flux_barrier_arc_deg": 0.0,
        "stator_inner_radius_mm": 158.0,
        "stator_outer_radius_mm": 205.0,
        "eml_unit_count": 8,
        "eml_arc_deg": 14.0,
        "eml_angular_offset_deg": 0.0,
        "stator_flux_relief_arc_deg": 0.0,
        "stator_flux_relief_offset_deg": -9.0,
        "air_boundary_radius_mm": 260.0,
        "depth_mm": 25.0,
        "block_mesh_size_mm": 0.0,
        "segment_mesh_size_mm": 0.0,
        "arc_max_segment_deg": 1.0,
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
    eml_count = int(config["eml_unit_count"])
    if eml_count not in {6, 8}:
        raise ValueError("eml_unit_count must be 6 or 8 for the current optimizer")
    if eml_count == 8 and int(config["rotor_gradient_count"]) != eml_count * 2:
        raise ValueError("Expected a 2:1 rotor-gradient to EML ratio for 8 EMLs")
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
    if float(config["rotor_magnet_mid_radius_mm"]) <= float(
        config["rotor_magnet_inner_radius_mm"]
    ):
        raise ValueError("rotor_magnet_mid_radius_mm must exceed magnet inner radius")
    if float(config["rotor_magnet_mid_radius_mm"]) >= float(
        config["rotor_magnet_outer_radius_mm"]
    ):
        raise ValueError("rotor_magnet_mid_radius_mm must be inside magnet outer radius")


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
    block_mesh_size: float = 0.0,
    segment_mesh_size: float = 0.0,
    arc_max_segment_deg: float = 1.0,
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
    block_auto_mesh = 1 if block_mesh_size <= 0 else 0
    segment_auto_mesh = 1 if segment_mesh_size <= 0 else 0
    material_lua = _lua_string(material)
    return f"""
add_arc_segment({points['outer_start'][0]:.6f}, {points['outer_start'][1]:.6f}, {points['outer_end'][0]:.6f}, {points['outer_end'][1]:.6f}, {arc_deg:.6f}, {arc_max_segment_deg:.6f})
add_arc_segment({points['inner_end'][0]:.6f}, {points['inner_end'][1]:.6f}, {points['inner_start'][0]:.6f}, {points['inner_start'][1]:.6f}, {arc_deg:.6f}, {arc_max_segment_deg:.6f})
add_line({points['outer_start'][0]:.6f}, {points['outer_start'][1]:.6f}, {points['inner_start'][0]:.6f}, {points['inner_start'][1]:.6f})
add_line({points['inner_end'][0]:.6f}, {points['inner_end'][1]:.6f}, {points['outer_end'][0]:.6f}, {points['outer_end'][1]:.6f})
mi_selectarcsegment({points['outer_mid'][0]:.6f}, {points['outer_mid'][1]:.6f})
mi_setarcsegmentprop(1, "<None>", 0, {group})
mi_clearselected()
mi_selectarcsegment({points['inner_mid'][0]:.6f}, {points['inner_mid'][1]:.6f})
mi_setarcsegmentprop(1, "<None>", 0, {group})
mi_clearselected()
mi_selectsegment({radial_start_mid[0]:.6f}, {radial_start_mid[1]:.6f})
mi_setsegmentprop("<None>", {segment_mesh_size:.6f}, {segment_auto_mesh}, 0, {group})
mi_clearselected()
mi_selectsegment({radial_end_mid[0]:.6f}, {radial_end_mid[1]:.6f})
mi_setsegmentprop("<None>", {segment_mesh_size:.6f}, {segment_auto_mesh}, 0, {group})
mi_clearselected()
mi_addblocklabel({points['label'][0]:.6f}, {points['label'][1]:.6f})
mi_selectlabel({points['label'][0]:.6f}, {points['label'][1]:.6f})
mi_setblockprop({material_lua}, {block_auto_mesh}, {block_mesh_size:.6f}, "<None>", {mag_dir:.6f}, {group}, {turns})
mi_clearselected()
"""


def _render_trailing_edge_barrier(
    *,
    center_angle: float,
    magnet_arc_deg: float,
    barrier_arc_deg: float,
    barrier_inner_radius: float,
    barrier_outer_radius: float,
    barrier_gap_deg: float,
    air_material: str,
    group: int,
    block_mesh_size: float = 0.0,
    segment_mesh_size: float = 0.0,
    arc_max_segment_deg: float = 1.0,
) -> str:
    """Render TEB_B: a closed air slot behind the magnet trailing edge."""
    trailing_edge = center_angle + magnet_arc_deg / 2.0
    barrier_center = trailing_edge + barrier_gap_deg + barrier_arc_deg / 2.0
    return _arc_segment_lua(
        center_angle=barrier_center,
        arc_deg=barrier_arc_deg,
        inner_radius=barrier_inner_radius,
        outer_radius=barrier_outer_radius,
        label_radius=(barrier_inner_radius + barrier_outer_radius) / 2.0,
        material=air_material,
        group=group,
        block_mesh_size=block_mesh_size,
        segment_mesh_size=segment_mesh_size,
        arc_max_segment_deg=arc_max_segment_deg,
    )


def _render_asymmetric_pole(
    *,
    center_angle: float,
    base_arc_deg: float,
    leading_extension_deg: float,
    trailing_pullback_deg: float,
    inner_radius: float,
    leading_outer_radius: float,
    trailing_outer_radius: float,
    material: str,
    group: int,
    magnetization_deg: float,
    block_mesh_size: float = 0.0,
    segment_mesh_size: float = 0.0,
    arc_max_segment_deg: float = 1.0,
) -> str:
    """Render ASYM_B: inner arc plus leading/trailing edges and sloped outer edge."""
    start_angle = center_angle - base_arc_deg / 2.0 - leading_extension_deg
    end_angle = center_angle + base_arc_deg / 2.0 - trailing_pullback_deg
    span_deg = end_angle - start_angle
    if span_deg <= 0:
        raise ValueError("Asymmetric pole angular span must be positive")

    inner_leading = _polar(inner_radius, start_angle)
    inner_trailing = _polar(inner_radius, end_angle)
    outer_leading = _polar(leading_outer_radius, start_angle)
    outer_trailing = _polar(trailing_outer_radius, end_angle)
    inner_mid = _polar(inner_radius, (start_angle + end_angle) / 2.0)
    leading_mid = (
        (inner_leading[0] + outer_leading[0]) / 2.0,
        (inner_leading[1] + outer_leading[1]) / 2.0,
    )
    trailing_mid = (
        (inner_trailing[0] + outer_trailing[0]) / 2.0,
        (inner_trailing[1] + outer_trailing[1]) / 2.0,
    )
    outer_mid = (
        (outer_leading[0] + outer_trailing[0]) / 2.0,
        (outer_leading[1] + outer_trailing[1]) / 2.0,
    )
    label = (
        (inner_leading[0] + inner_trailing[0] + outer_leading[0] + outer_trailing[0]) / 4.0,
        (inner_leading[1] + inner_trailing[1] + outer_leading[1] + outer_trailing[1]) / 4.0,
    )
    block_auto_mesh = 1 if block_mesh_size <= 0 else 0
    segment_auto_mesh = 1 if segment_mesh_size <= 0 else 0
    material_lua = _lua_string(material)
    return f"""
-- ASYM_B asymmetric pole: extended leading side, sloped outer edge, and recessed trailing side.
add_arc_segment({inner_trailing[0]:.6f}, {inner_trailing[1]:.6f}, {inner_leading[0]:.6f}, {inner_leading[1]:.6f}, {span_deg:.6f}, {arc_max_segment_deg:.6f})
add_line({inner_leading[0]:.6f}, {inner_leading[1]:.6f}, {outer_leading[0]:.6f}, {outer_leading[1]:.6f})
add_line({outer_leading[0]:.6f}, {outer_leading[1]:.6f}, {outer_trailing[0]:.6f}, {outer_trailing[1]:.6f})
add_line({outer_trailing[0]:.6f}, {outer_trailing[1]:.6f}, {inner_trailing[0]:.6f}, {inner_trailing[1]:.6f})
mi_selectarcsegment({inner_mid[0]:.6f}, {inner_mid[1]:.6f})
mi_setarcsegmentprop(1, "<None>", 0, {group})
mi_clearselected()
mi_selectsegment({leading_mid[0]:.6f}, {leading_mid[1]:.6f})
mi_setsegmentprop("<None>", {segment_mesh_size:.6f}, {segment_auto_mesh}, 0, {group})
mi_clearselected()
mi_selectsegment({outer_mid[0]:.6f}, {outer_mid[1]:.6f})
mi_setsegmentprop("<None>", {segment_mesh_size:.6f}, {segment_auto_mesh}, 0, {group})
mi_clearselected()
mi_selectsegment({trailing_mid[0]:.6f}, {trailing_mid[1]:.6f})
mi_setsegmentprop("<None>", {segment_mesh_size:.6f}, {segment_auto_mesh}, 0, {group})
mi_clearselected()
mi_addblocklabel({label[0]:.6f}, {label[1]:.6f})
mi_selectlabel({label[0]:.6f}, {label[1]:.6f})
mi_setblockprop({material_lua}, {block_auto_mesh}, {block_mesh_size:.6f}, "<None>", {magnetization_deg:.6f}, {group}, 0)
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
    air_material = str(config["air_material"])
    block_mesh_size = float(config["block_mesh_size_mm"])
    segment_mesh_size = float(config["segment_mesh_size_mm"])
    arc_max_segment_deg = float(config["arc_max_segment_deg"])
    block_auto_mesh = 1 if block_mesh_size <= 0 else 0
    output_fem_file = _lua_string(str(config["output_fem_file"]))

    lines = [
        "-- PM Gradient Motor Lab FEMM geometry builder",
        "-- Radial-flux 2D approximation of the described disc/axial concept.",
        "-- Anti-cancellation v1: concentrated poles, rotor flux barriers,",
        "-- and angularly offset EMLs to reduce backward pull.",
        "newdocument(0)",
        f'mi_probdef(0, "millimeters", "planar", 1e-8, {float(config["depth_mm"]):.6f}, 30)',
        "",
        f"rotor_group = {rotor_group}",
        f"stator_group = {stator_group}",
        f"coil_group = {coil_group}",
        "",
        f"mi_getmaterial({_lua_string(air_material)})",
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
        f"mi_setblockprop({_lua_string(air_material)}, {block_auto_mesh}, {block_mesh_size:.6f}, \"<None>\", 0, 0, 0)",
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
        f"mi_setblockprop({_lua_string(rotor_core_material)}, {block_auto_mesh}, {block_mesh_size:.6f}, \"<None>\", 0, rotor_group, 0)",
        "mi_clearselected()",
    ]

    for index in range(rotor_count):
        angle = (
            index * 360.0 / rotor_count
            + float(config["rotor_magnet_leading_edge_bias_deg"])
        )
        base_magnetization = angle if index % 2 == 0 else angle + 180.0
        halbach_bias = float(config["rotor_halbach_bias_deg"])
        magnetization = base_magnetization + (halbach_bias if index % 2 == 0 else -halbach_bias)
        cap_angle = angle + float(config["rotor_outer_pole_cap_offset_deg"])
        lines.append(
            f"-- Rotor gradient magnet {index + 1:02d}: concentrated main pole"
        )
        if bool(config["asymmetric_pole_enabled"]):
            lines.append(
                _render_asymmetric_pole(
                    center_angle=angle,
                    base_arc_deg=float(config["rotor_magnet_arc_deg"]),
                    leading_extension_deg=float(config["asymmetric_leading_extension_deg"]),
                    trailing_pullback_deg=float(config["asymmetric_trailing_pullback_deg"]),
                    inner_radius=float(config["rotor_magnet_inner_radius_mm"]),
                    leading_outer_radius=float(config["asymmetric_leading_outer_radius_mm"]),
                    trailing_outer_radius=float(config["asymmetric_trailing_outer_radius_mm"]),
                    material=magnet_material,
                    group=rotor_group,
                    magnetization_deg=magnetization,
                    block_mesh_size=block_mesh_size,
                    segment_mesh_size=segment_mesh_size,
                    arc_max_segment_deg=arc_max_segment_deg,
                )
            )
        else:
            lines.append(
                _arc_segment_lua(
                    center_angle=angle,
                    arc_deg=float(config["rotor_magnet_arc_deg"]),
                    inner_radius=float(config["rotor_magnet_inner_radius_mm"]),
                    outer_radius=float(config["rotor_magnet_mid_radius_mm"]),
                    label_radius=(
                        float(config["rotor_magnet_inner_radius_mm"])
                        + float(config["rotor_magnet_mid_radius_mm"])
                    )
                    / 2.0,
                    material=magnet_material,
                    group=rotor_group,
                    magnetization_deg=magnetization,
                    block_mesh_size=block_mesh_size,
                    segment_mesh_size=segment_mesh_size,
                    arc_max_segment_deg=arc_max_segment_deg,
                )
            )
        if bool(config["trailing_edge_barrier_enabled"]):
            lines.append(
                f"-- TEB_B trailing-edge air-gap barrier {index + 1:02d}"
            )
            lines.append(
                _render_trailing_edge_barrier(
                    center_angle=angle,
                    magnet_arc_deg=float(config["rotor_magnet_arc_deg"]),
                    barrier_arc_deg=float(config["trailing_edge_barrier_arc_deg"]),
                    barrier_inner_radius=float(config["trailing_edge_barrier_inner_radius_mm"]),
                    barrier_outer_radius=float(config["trailing_edge_barrier_outer_radius_mm"]),
                    barrier_gap_deg=float(config["trailing_edge_barrier_gap_deg"]),
                    air_material=air_material,
                    group=rotor_group,
                    block_mesh_size=block_mesh_size,
                    segment_mesh_size=segment_mesh_size,
                    arc_max_segment_deg=arc_max_segment_deg,
                )
            )
        if float(config["rotor_outer_pole_cap_arc_deg"]) > 0:
            lines.append(
                f"-- Rotor gradient magnet {index + 1:02d}: forward-biased outer pole cap"
            )
            lines.append(
                _arc_segment_lua(
                    center_angle=cap_angle,
                    arc_deg=float(config["rotor_outer_pole_cap_arc_deg"]),
                    inner_radius=float(config["rotor_magnet_mid_radius_mm"]),
                    outer_radius=float(config["rotor_magnet_outer_radius_mm"]),
                    label_radius=(
                        float(config["rotor_magnet_mid_radius_mm"])
                        + float(config["rotor_magnet_outer_radius_mm"])
                    )
                    / 2.0,
                    material=magnet_material,
                    group=rotor_group,
                    magnetization_deg=magnetization,
                    block_mesh_size=block_mesh_size,
                    segment_mesh_size=segment_mesh_size,
                    arc_max_segment_deg=arc_max_segment_deg,
                )
            )

    if float(config["rotor_flux_barrier_arc_deg"]) > 0:
        for index in range(rotor_count):
            barrier_angle = (index + 0.5) * 360.0 / rotor_count
            lines.append(
                f"-- Rotor flux barrier {index + 1:02d}: air slot to interrupt return flux"
            )
            lines.append(
                _arc_segment_lua(
                    center_angle=barrier_angle,
                    arc_deg=float(config["rotor_flux_barrier_arc_deg"]),
                    inner_radius=float(config["rotor_flux_barrier_inner_radius_mm"]),
                    outer_radius=float(config["rotor_flux_barrier_outer_radius_mm"]),
                    label_radius=(
                        float(config["rotor_flux_barrier_inner_radius_mm"])
                        + float(config["rotor_flux_barrier_outer_radius_mm"])
                    )
                    / 2.0,
                    material=air_material,
                    group=rotor_group,
                    block_mesh_size=block_mesh_size,
                    segment_mesh_size=segment_mesh_size,
                    arc_max_segment_deg=arc_max_segment_deg,
                )
            )

    for index in range(eml_count):
        angle = index * 360.0 / eml_count + float(config["eml_angular_offset_deg"])
        lines.append(f"-- EML stator unit {index + 1:02d}: offset for positive-zone bias")
        lines.append(
            _arc_segment_lua(
                center_angle=angle,
                arc_deg=float(config["eml_arc_deg"]),
                inner_radius=float(config["stator_inner_radius_mm"]),
                outer_radius=float(config["stator_outer_radius_mm"]),
                label_radius=float(config["stator_inner_radius_mm"]) + 4.0,
                material=stator_core_material,
                group=stator_group,
                block_mesh_size=block_mesh_size,
                segment_mesh_size=segment_mesh_size,
                arc_max_segment_deg=arc_max_segment_deg,
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
                block_mesh_size=block_mesh_size,
                segment_mesh_size=segment_mesh_size,
                arc_max_segment_deg=arc_max_segment_deg,
            )
        )
        if float(config["stator_flux_relief_arc_deg"]) > 0:
            relief_angle = angle + float(config["stator_flux_relief_offset_deg"])
            relief_inner = float(config["stator_inner_radius_mm"]) + 2.0
            relief_outer = float(config["stator_outer_radius_mm"]) - 2.0
            lines.append(
                f"-- EML flux relief {index + 1:02d}: air shunt to weaken trailing pull"
            )
            lines.append(
                _arc_segment_lua(
                    center_angle=relief_angle,
                    arc_deg=float(config["stator_flux_relief_arc_deg"]),
                    inner_radius=relief_inner,
                    outer_radius=relief_outer,
                    label_radius=(relief_inner + relief_outer) / 2.0,
                    material=air_material,
                    group=stator_group,
                    block_mesh_size=block_mesh_size,
                    segment_mesh_size=segment_mesh_size,
                    arc_max_segment_deg=arc_max_segment_deg,
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
    pulse_config = {
        "strategy": "selective_position_based",
        "description": (
            "Only pulse an EML when the rotor angle is inside a measured or "
            "simulated positive-torque window for that EML. Do not pulse in "
            "negative torque windows."
        ),
        "eml_angular_offset_deg": config["eml_angular_offset_deg"],
        "positive_torque_windows_per_45deg_period": [
            {"start_deg": 0.0, "end_deg": 11.4},
            {"start_deg": 22.4, "end_deg": 34.1},
            {"start_deg": 44.8, "end_deg": 45.0},
        ],
        "negative_torque_lockout_windows_per_45deg_period": [
            {"start_deg": 11.4, "end_deg": 22.4},
            {"start_deg": 34.1, "end_deg": 44.8},
        ],
        "current_density_ma_per_mm2": config["current_density_ma_per_mm2"],
        "candidate_eml_counts": [6, 8],
        "notes": [
            "Windows were initialized from femm_torque_angle_arc10_offset0_period45_step1.csv.",
            "Update windows from FEMM torque-angle CSV after each geometry run.",
            "Pulse one EML, or a small overlapping subset, only during positive net torque.",
            "Subtract coil input energy and add only measured/reasonable flyback recovery.",
        ],
    }
    (workflow_dir / "pulse_strategy.example.json").write_text(
        json.dumps(pulse_config, indent=2) + "\n",
        encoding="utf-8",
    )


def main() -> None:
    write_geometry_builder(ROOT)
    print("Wrote geometry/pm_gradient_motor_config.json")
    print("Wrote field_sim/femm/build_pm_gradient_motor.lua")
    print("Wrote field_sim/femm/pulse_strategy.example.json")


if __name__ == "__main__":
    main()
