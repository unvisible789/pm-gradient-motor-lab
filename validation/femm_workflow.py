from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from validation.validation_core import integrate_torque_angle, load_numeric_csv


def default_femm_config() -> dict[str, Any]:
    return {
        "base_fem_file": "geometry/pm_gradient_motor_base.fem",
        "output_csv": "data/field_sim/femm_torque_angle.csv",
        "rotor_group": 2,
        "rotation_center_x": 0.0,
        "rotation_center_y": 0.0,
        "angle_step_deg": 2,
        "problem_frequency_hz": 0,
        "problem_depth_mm": 25,
        "solver_precision": 1e-8,
        "min_angle_deg": 0,
        "max_angle_deg": 360,
    }


def _lua_string(value: str) -> str:
    return '"' + value.replace("\\", "/").replace('"', '\\"') + '"'


def render_femm_lua(config: dict[str, Any]) -> str:
    base_fem_file = _lua_string(str(config["base_fem_file"]))
    output_csv = _lua_string(str(config["output_csv"]))
    rotor_group = int(config["rotor_group"])
    center_x = float(config["rotation_center_x"])
    center_y = float(config["rotation_center_y"])
    angle_step = int(config["angle_step_deg"])
    min_angle = int(config["min_angle_deg"])
    max_angle = int(config["max_angle_deg"])

    return f"""-- PM Gradient Motor Lab FEMM torque-angle sweep
-- Run inside FEMM: File -> Open Lua Script -> this file.
--
-- Prerequisite:
--   Build or import geometry in the base .fem file and assign the complete
--   rotating assembly to group {rotor_group}.
--
-- Output:
--   angle_deg,torque_nm CSV for validation/integration.

open({base_fem_file})

csv = assert(io.open({output_csv}, "w"))
csv:write("angle_deg,torque_nm\\n")
csv:flush()

previous_angle = 0
for angle_deg = {min_angle}, {max_angle}, {angle_step} do
  delta_angle = angle_deg - previous_angle
  if delta_angle ~= 0 then
    mi_seteditmode("group")
    mi_selectgroup({rotor_group})
    mi_moverotate({center_x}, {center_y}, delta_angle)
    mi_clearselected()
  end

  mi_analyze(1)
  mi_loadsolution()
  mo_groupselectblock({rotor_group})
  torque_nm = mo_blockintegral(22)
  mo_clearblock()
  csv:write(string.format("%g,%.12g\\n", angle_deg, torque_nm))
  csv:flush()
  previous_angle = angle_deg
end

csv:close()
"""


def write_femm_workflow(root: str | Path = ROOT) -> None:
    root = Path(root)
    workflow_dir = root / "field_sim" / "femm"
    workflow_dir.mkdir(parents=True, exist_ok=True)
    config = default_femm_config()
    (workflow_dir / "config.example.json").write_text(
        json.dumps(config, indent=2) + "\n",
        encoding="utf-8",
    )
    (workflow_dir / "sweep_torque_angle.lua").write_text(
        render_femm_lua(config),
        encoding="utf-8",
    )


def summarize_torque_angle_csv(path: str | Path) -> dict[str, float | str]:
    rows = load_numeric_csv(path)
    summary = integrate_torque_angle(rows)
    work = float(summary["work_j_per_rev"])
    if abs(work) < 1e-6:
        result = "CYCLE_CLOSES_NO_NET_WORK"
    elif work > 0:
        result = "NET_POSITIVE_WORK_REQUIRES_SOURCE_ACCOUNTING"
    else:
        result = "NET_NEGATIVE_WORK_REQUIRES_INPUT"
    return {**summary, "energy_result": result}


def main() -> None:
    write_femm_workflow(ROOT)
    print("Wrote field_sim/femm/config.example.json")
    print("Wrote field_sim/femm/sweep_torque_angle.lua")


if __name__ == "__main__":
    main()
