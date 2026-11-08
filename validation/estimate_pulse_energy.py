from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from validation.pulse_control import PulseElectricalModel, estimate_revolution_energy  # noqa: E402


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
    parser = argparse.ArgumentParser(description="Illustrate assumed inductive storage; this cannot estimate motor input or generation.")
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

    if not math.isfinite(args.period_deg) or not 0 < args.period_deg <= 360:
        parser.error("period-deg must be finite and in (0, 360]")
    if not math.isclose(360.0 / args.period_deg, round(360.0 / args.period_deg)):
        parser.error("The assumed sector must divide one revolution")
    windows = load_windows(args.windows)
    duty = window_duty(windows, args.period_deg)
    periods_per_rev = 360.0 / args.period_deg
    budget = estimate_revolution_energy(
        mechanical_work_j_per_rev=args.mechanical_work_j_per_rev,
        electrical_model=PulseElectricalModel(
            coil_inductance_mh=args.coil_inductance_mh,
            pulse_current_a=args.pulse_current_a,
            recovery_efficiency=args.recovery_efficiency,
            eml_count=args.eml_count,
            pulses_per_eml_per_rev=args.pulses_per_eml_per_period * periods_per_rev,
        ),
    )
    stored_j = budget["stored_j_per_pulse"]
    unrecovered_j = budget["unrecovered_j_per_pulse"]
    pulses_per_rev = budget["pulse_count_per_rev"]
    window_label = (args.windows.relative_to(ROOT) if args.windows.is_relative_to(ROOT) else args.windows).as_posix()

    report = f"""# Pulse Energy Budget

**Illustration only; insufficient data for electrical input, efficiency or net generation.** Defaults are assumed numbers, not a qualified APW drive waveform. One half L I squared measures stored magnetic energy, not complete pulse input.

## Assumptions

| Parameter | Value |
|---|---:|
| Pulse window file | `{window_label}` |
| Legacy assist-window coverage over {args.period_deg:.1f} deg | {duty:.3f} |
| EML count | {args.eml_count} |
| Coil inductance | {args.coil_inductance_mh:.3f} mH |
| Pulse current | {args.pulse_current_a:.3f} A |
| Flyback/recovery efficiency | {args.recovery_efficiency:.3f} |
| Assumed pulses per EML per {args.period_deg:g} deg sector | {args.pulses_per_eml_per_period:.3f} |
| Unvalidated torque-integral diagnostic | {args.mechanical_work_j_per_rev:.6f} J/rev |

## Illustrative magnetic storage

| Metric | Value |
|---|---:|
| Stored magnetic energy per pulse, 0.5 L I^2 | {stored_j:.6f} J |
| Assumed unrecovered storage per pulse | {unrecovered_j:.6f} J |
| Pulses per revolution | {pulses_per_rev:.3f} |
| Assumed unrecovered storage over all events | {budget['illustrative_unrecovered_magnetic_energy_j_per_rev']:.6f} J/rev |
| Total electrical input | Unknown |
| Net generation / efficiency | Not evaluated |

## Interpretation

Neither a sampled angular fraction nor a magnet/coil count ratio determines a pulse count. The event count above is an explicit illustrative assumption and needs a complete per-channel switching schedule before use.

Measure signed source voltage times current, all auxiliary and drive inputs, useful output, and stored-energy changes over a complete repeat. Include motion-induced voltage and winding heating. If returned energy is already in the signed source integral, do not subtract recovery again. A positive passive torque residual must not be treated as available shaft energy.
"""
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(report, encoding="utf-8")
    print(report)


if __name__ == "__main__":
    main()
