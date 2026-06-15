from __future__ import annotations

import csv
import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from validation.femm_workflow import summarize_torque_angle_csv


def load_curve(path: Path) -> list[tuple[float, float]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return [
            (float(row["angle_deg"]), float(row["torque_nm"]))
            for row in csv.DictReader(handle)
        ]


def curve_stats(path: Path) -> dict[str, float | str]:
    curve = load_curve(path)
    torques = [torque for _, torque in curve]
    min_torque = min(torques)
    max_torque = max(torques)
    summary = summarize_torque_angle_csv(path)
    return {
        "csv": str(path.as_posix()),
        **summary,
        "min_torque_nm": min_torque,
        "min_torque_angle_deg": curve[torques.index(min_torque)][0],
        "max_torque_nm": max_torque,
        "max_torque_angle_deg": curve[torques.index(max_torque)][0],
        "mean_sampled_torque_nm": sum(torques) / len(torques),
        "closure_delta_nm": curve[-1][1] - curve[0][1],
    }


def main() -> None:
    paths = [Path(arg) for arg in sys.argv[1:]]
    if not paths:
        paths = sorted((ROOT / "data" / "field_sim").glob("femm_torque_angle*.csv"))
    report = [curve_stats(path) for path in paths]
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
