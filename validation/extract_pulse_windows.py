"""Extract positive-torque assist and lockout windows from a torque-angle CSV."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def load_curve(path: Path) -> list[tuple[float, float]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return [(float(r["angle_deg"]), float(r["torque_nm"])) for r in csv.DictReader(handle)]


def extract_windows(curve: list[tuple[float, float]]) -> dict:
    if not curve:
        return {"positive_torque_windows": [], "negative_torque_lockout_windows": []}

    curve = sorted(curve, key=lambda item: item[0])
    span_end = curve[-1][0]
    positive: list[dict[str, float]] = []
    negative: list[dict[str, float]] = []
    current_sign = curve[0][1] >= 0
    start = curve[0][0]

    for angle, torque in curve[1:]:
        sign = torque >= 0
        if sign != current_sign:
            window = {"start_deg": round(start, 2), "end_deg": round(angle, 2)}
            if current_sign:
                positive.append(window)
            else:
                negative.append(window)
            start = angle
            current_sign = sign

    closing = {"start_deg": round(start, 2), "end_deg": round(span_end, 2)}
    if current_sign:
        positive.append(closing)
    else:
        negative.append(closing)

    return {
        "positive_torque_windows": positive,
        "negative_torque_lockout_windows": negative,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("csv", type=Path)
    parser.add_argument("--out", type=Path, default=None)
    parser.add_argument("--source-label", default=None)
    args = parser.parse_args()

    windows = extract_windows(load_curve(args.csv))
    payload = {
        "strategy": "selective_position_based",
        "source_csv": str(args.csv.as_posix()),
        "source_label": args.source_label,
        "positive_torque_windows_per_45deg_period": windows["positive_torque_windows"],
        "negative_torque_lockout_windows_per_45deg_period": windows["negative_torque_lockout_windows"],
        "notes": [
            "Windows derived from sampled torque sign over the sweep span.",
            "First screen only; not mesh-converged.",
        ],
    }
    text = json.dumps(payload, indent=2) + "\n"
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(text, encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()