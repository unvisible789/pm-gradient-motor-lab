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
        curve = [
            (float(row["angle_deg"]), float(row["torque_nm"]))
            for row in csv.DictReader(handle)
        ]
    return sorted(curve, key=lambda item: item[0])


def curve_stats(path: Path) -> dict[str, float | str]:
    curve = load_curve(path)
    torques = [torque for _, torque in curve]
    min_torque = min(torques)
    max_torque = max(torques)
    positive_work = 0.0
    negative_work = 0.0
    positive_segments = 0
    negative_segments = 0
    zero_crossings: list[float] = []
    for (angle_a, torque_a), (angle_b, torque_b) in zip(curve, curve[1:]):
        delta_rad = math.radians(angle_b - angle_a)
        avg_torque = (torque_a + torque_b) / 2.0
        work = avg_torque * delta_rad
        if avg_torque >= 0:
            positive_work += work
            positive_segments += 1
        else:
            negative_work += work
            negative_segments += 1
        if torque_a == 0:
            zero_crossings.append(angle_a)
        elif torque_a * torque_b < 0:
            fraction = abs(torque_a) / (abs(torque_a) + abs(torque_b))
            zero_crossings.append(angle_a + (angle_b - angle_a) * fraction)
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
        "positive_work_j": positive_work,
        "negative_work_j": negative_work,
        "positive_segment_count": float(positive_segments),
        "negative_segment_count": float(negative_segments),
        "zero_crossings_deg": ", ".join(f"{angle:.2f}" for angle in zero_crossings),
    }


def main() -> None:
    paths = [Path(arg) for arg in sys.argv[1:]]
    if not paths:
        paths = sorted((ROOT / "data" / "field_sim").glob("femm_torque_angle*.csv"))
    report = [curve_stats(path) for path in paths]
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
