"""Electrical energy accounting for selective pulse assist FEMM cases."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from validation.analyze_pulse_assist_comparison import CASES, summarize_case  # noqa: E402
from validation.pulse_control import (  # noqa: E402
    PulseElectricalModel,
    estimate_revolution_energy,
    load_pulse_windows,
    pulse_current_levels_for_geometry,
)


def account_case(
    *,
    level: str,
    current_a: float,
    case: dict,
    baseline_work_j_per_rev: float,
    eml_count: int,
    periods_per_rev: int,
    coil_inductance_mh: float,
    recovery_efficiency: float,
    copper_loss_fraction: float,
    switching_loss_j_per_pulse: float,
) -> dict:
    model = PulseElectricalModel(
        coil_inductance_mh=coil_inductance_mh,
        pulse_current_a=current_a,
        recovery_efficiency=recovery_efficiency,
        eml_count=eml_count,
        pulses_per_eml_per_rev=float(periods_per_rev),
    )
    budget = estimate_revolution_energy(
        mechanical_work_j_per_rev=float(case["full_rev_equiv_j"]),
        electrical_model=model,
    )
    pulsed_fraction = float(case.get("pulsed_angle_count", 0)) / 45.0
    effective_pulses = budget["pulse_count_per_rev"] * pulsed_fraction
    unrecovered = budget["unrecovered_j_per_pulse"] * effective_pulses
    copper_loss = budget["stored_j_per_pulse"] * copper_loss_fraction * effective_pulses
    switching_loss = switching_loss_j_per_pulse * effective_pulses
    total_input = unrecovered + copper_loss + switching_loss
    added_mech = float(case["full_rev_equiv_j"]) - baseline_work_j_per_rev
    net_added = added_mech - total_input
    return {
        "label": level,
        "pulse_current_a": current_a,
        "current_density_ma_per_mm2": {"low": 5.0, "medium": 10.0, "high": 20.0}[level],
        "stored_j_per_pulse": budget["stored_j_per_pulse"],
        "unrecovered_j_per_pulse": budget["unrecovered_j_per_pulse"],
        "effective_pulses_per_rev": effective_pulses,
        "unrecovered_input_j_per_rev": unrecovered,
        "copper_loss_j_per_rev": copper_loss,
        "switching_loss_j_per_rev": switching_loss,
        "total_electrical_input_j_per_rev": total_input,
        "mechanical_work_j_per_rev": float(case["full_rev_equiv_j"]),
        "added_mechanical_work_j_per_rev": added_mech,
        "net_added_work_after_input_j_per_rev": net_added,
        "closes_energy": net_added > 0,
    }


def solved_metric_case(case: dict | None) -> bool:
    return bool(
        case
        and case.get("screen_status") != "incomplete_period"
        and "full_rev_equiv_j" in case
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Account electrical input for pulse assist cases.")
    parser.add_argument(
        "--variant-config",
        type=Path,
        default=ROOT / "field_sim/femm/variants/gap_159p0.json",
    )
    parser.add_argument(
        "--windows",
        type=Path,
        default=ROOT / "field_sim/femm/pulse_strategy.gap159_eml12.json",
    )
    parser.add_argument("--comparison-json", type=Path, default=ROOT / "reports/pulse_assist_comparison_latest.json")
    parser.add_argument("--coil-inductance-mh", type=float, default=5.0, help="PLACEHOLDER coil L")
    parser.add_argument("--recovery-efficiency", type=float, default=0.75, help="PLACEHOLDER flyback recovery")
    parser.add_argument("--copper-loss-fraction", type=float, default=0.05, help="PLACEHOLDER I^2R fraction of stored energy")
    parser.add_argument("--switching-loss-j-per-pulse", type=float, default=0.0002, help="PLACEHOLDER driver switching loss")
    parser.add_argument("--md-out", type=Path, default=ROOT / "reports/pulse_electrical_accounting.md")
    parser.add_argument("--json-out", type=Path, default=ROOT / "reports/pulse_electrical_accounting_latest.json")
    args = parser.parse_args()

    config = json.loads(args.variant_config.read_text(encoding="utf-8"))
    assist, lockout = load_pulse_windows(args.windows)
    current_levels = pulse_current_levels_for_geometry(config)
    eml_count = int(config["eml_unit_count"])
    periods_per_rev = 8

    if args.comparison_json.exists():
        comparison = json.loads(args.comparison_json.read_text(encoding="utf-8"))
    else:
        comparison = []
        for label, rel in CASES:
            path = ROOT / rel
            if path.exists():
                comparison.append(summarize_case(label, path, assist, lockout))

    baseline = next((row for row in comparison if row.get("label") == "coil-off"), None)
    baseline_work = float(baseline["full_rev_equiv_j"]) if baseline else 0.0

    rows = []
    for level, current_a in current_levels.items():
        case = next((row for row in comparison if row.get("label") == level), None)
        if not solved_metric_case(case):
            continue
        rows.append(
            account_case(
                level=level,
                current_a=current_a,
                case=case,
                baseline_work_j_per_rev=baseline_work,
                eml_count=eml_count,
                periods_per_rev=periods_per_rev,
                coil_inductance_mh=args.coil_inductance_mh,
                recovery_efficiency=args.recovery_efficiency,
                copper_loss_fraction=args.copper_loss_fraction,
                switching_loss_j_per_pulse=args.switching_loss_j_per_pulse,
            )
        )

    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    args.json_out.write_text(json.dumps(rows, indent=2) + "\n", encoding="utf-8")

    report = f"""# Pulse Electrical Accounting

**Date:** 2026-06-15

First-order accounting with **placeholder** coil values. Not measured L/R.

## Placeholder Assumptions

| Parameter | Value | Note |
|---|---:|---|
| Coil inductance L | {args.coil_inductance_mh:.3f} mH | PLACEHOLDER |
| Flyback recovery | {args.recovery_efficiency:.3f} | PLACEHOLDER |
| Copper loss fraction of 0.5 L I^2 | {args.copper_loss_fraction:.3f} | PLACEHOLDER |
| Switching loss per effective pulse | {args.switching_loss_j_per_pulse:.6f} J | PLACEHOLDER |
| EML count | {eml_count} | from geometry |
| Current levels (mA/mm^2) | low=5, medium=10, high=20 | mapped via coil area |

## Current Levels (from geometry)

| Level | Density (mA/mm^2) | Current (A) |
|---|---:|---:|
| low | 5.0 | {current_levels['low']:.4f} |
| medium | 10.0 | {current_levels['medium']:.4f} |
| high | 20.0 | {current_levels['high']:.4f} |

## Energy Balance vs Coil-Off Baseline ({baseline_work:.6f} J/rev)

| Case | Added mech (J/rev) | Unrecovered input (J/rev) | Copper loss (J/rev) | Switching loss (J/rev) | Total input (J/rev) | Net added after input (J/rev) | Closes? |
|---|---:|---:|---:|---:|---:|---:|---|
"""
    for row in rows:
        report += (
            f"| {row['label']} | {row['added_mechanical_work_j_per_rev']:.6f} | "
            f"{row['unrecovered_input_j_per_rev']:.6f} | {row['copper_loss_j_per_rev']:.6f} | "
            f"{row['switching_loss_j_per_rev']:.6f} | {row['total_electrical_input_j_per_rev']:.6f} | "
            f"{row['net_added_work_after_input_j_per_rev']:.6f} | "
            f"{'yes' if row['closes_energy'] else 'no'} |\n"
        )

    report += """
## Interpretation

- Stored energy per pulse uses 0.5 L I^2 with placeholder L.
- Unrecovered input is stored energy times (1 - recovery efficiency), scaled by effective pulsed angles.
- Added mechanical work is coil-on full-rev equivalent minus coil-off baseline.
- **Do not claim improvement** unless net added work after input is positive and lockout braking did not worsen.

Replace placeholder L, R, recovery, and switching loss with measured values before design decisions.
"""
    args.md_out.write_text(report, encoding="utf-8")
    print(report)


if __name__ == "__main__":
    main()
