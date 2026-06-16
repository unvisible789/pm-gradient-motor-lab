from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load_windows(path: Path) -> list[dict[str, float]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if "positive_torque_windows_per_45deg_period" in payload:
        return payload["positive_torque_windows_per_45deg_period"]
    if "assist_windows" in payload:
        return payload["assist_windows"]
    raise KeyError("Pulse strategy must define positive_torque_windows_per_45deg_period")


def window_duty(windows: list[dict[str, float]], period_deg: float) -> float:
    span = sum(max(0.0, w["end_deg"] - w["start_deg"]) for w in windows)
    return span / period_deg if period_deg else math.nan


def main() -> None:
    parser = argparse.ArgumentParser(description="Estimate EML pulse input energy budget.")
    parser.add_argument("--windows", type=Path, default=ROOT / "field_sim/femm/pulse_strategy.asym_b.json")
    parser.add_argument("--period-deg", type=float, default=45.0)
    parser.add_argument("--eml-count", type=int, default=8)
    parser.add_argument("--coil-inductance-mh", type=float, default=5.0)
    parser.add_argument("--pulse-current-a", type=float, default=2.0)
    parser.add_argument("--recovery-efficiency", type=float, default=0.75)
    parser.add_argument("--pulses-per-eml-per-period", type=float, default=1.0)
    parser.add_argument("--mechanical-work-j-per-rev", type=float, default=1.159)
    parser.add_argument("--out", type=Path, default=ROOT / "reports/pulse_energy_budget.md")
    args = parser.parse_args()

    windows = load_windows(args.windows)
    duty = window_duty(windows, args.period_deg)
    periods_per_rev = 360.0 / args.period_deg
    inductance_h = args.coil_inductance_mh / 1000.0
    stored_j = 0.5 * inductance_h * args.pulse_current_a**2
    unrecovered_j = stored_j * (1.0 - args.recovery_efficiency)
    pulses_per_rev = args.eml_count * args.pulses_per_eml_per_period * periods_per_rev
    input_j_per_rev = unrecovered_j * pulses_per_rev
    net_after_input = args.mechanical_work_j_per_rev - input_j_per_rev

    report = f"""# Pulse Energy Budget

First-order accounting only. Replace defaults with measured coil L/R/current and driver recovery data before making design claims.

## Assumptions

| Parameter | Value |
|---|---:|
| Pulse window file | `{args.windows.as_posix()}` |
| Assist duty over {args.period_deg:.1f} deg | {duty:.3f} |
| EML count | {args.eml_count} |
| Coil inductance | {args.coil_inductance_mh:.3f} mH |
| Pulse current | {args.pulse_current_a:.3f} A |
| Flyback/recovery efficiency | {args.recovery_efficiency:.3f} |
| Pulses per EML per 45 deg period | {args.pulses_per_eml_per_period:.3f} |
| Mechanical first-screen work | {args.mechanical_work_j_per_rev:.6f} J/rev |

## Estimated Energy

| Metric | Value |
|---|---:|
| Stored magnetic energy per pulse, 0.5 L I^2 | {stored_j:.6f} J |
| Unrecovered input per pulse | {unrecovered_j:.6f} J |
| Pulses per revolution | {pulses_per_rev:.3f} |
| Unrecovered pulse input | {input_j_per_rev:.6f} J/rev |
| Mechanical work minus unrecovered pulse input | {net_after_input:.6f} J/rev |

## Interpretation

This does not model energized torque yet. It only prevents pulse assist from being treated as free.
If FEMM later shows added mechanical work from coil current, compare only the added work against measured or simulated electrical input plus switching, copper, core, and recovery losses.
"""
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(report, encoding="utf-8")
    print(report)


if __name__ == "__main__":
    main()
