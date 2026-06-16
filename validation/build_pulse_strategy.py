from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from validation.extract_pulse_windows import extract_windows, load_curve  # noqa: E402
from validation.pulse_control import (  # noqa: E402
    PulseElectricalModel,
    build_phase_schedule,
    estimate_revolution_energy,
    merge_windows,
)
from validation.rank_femm_variants import full_rev_equivalent  # noqa: E402
from validation.analyze_femm_sweeps import curve_stats  # noqa: E402


def build_strategy_payload(
    *,
    label: str,
    source_csv: str,
    assist_windows: list[dict[str, float]],
    mechanical_work_j_per_rev: float,
    advance_deg: float = 1.0,
    coil_inductance_mh: float = 5.0,
    pulse_current_a: float = 2.0,
    recovery_efficiency: float = 0.75,
    pulses_per_eml_per_rev: float = 8.0,
) -> dict:
    merged = merge_windows(assist_windows, min_gap_deg=0.5)
    schedule = build_phase_schedule(merged, advance_deg=advance_deg)
    budget = estimate_revolution_energy(
        mechanical_work_j_per_rev=mechanical_work_j_per_rev,
        electrical_model=PulseElectricalModel(
            coil_inductance_mh=coil_inductance_mh,
            pulse_current_a=pulse_current_a,
            recovery_efficiency=recovery_efficiency,
            eml_count=8,
            pulses_per_eml_per_rev=pulses_per_eml_per_rev,
        ),
    )
    return {
        "label": label,
        "source_csv": source_csv,
        "strategy": "selective_phased_assist",
        "advance_deg": advance_deg,
        "positive_torque_windows_per_45deg_period": merged,
        "pulse_schedule_360deg": schedule,
        "electrical_budget": budget,
        "control_rules": [
            "Pulse only inside assist windows.",
            "Do not pulse in lockout windows unless energized FEMM shows a local sign reversal.",
            "Account for coil input, copper loss, switching loss, and imperfect flyback recovery.",
            "Regenerate this schedule after each geometry or EML offset change.",
        ],
    }


def markdown_report(payload: dict) -> str:
    budget = payload["electrical_budget"]
    return f"""# Pulse Strategy: {payload['label']}

First-screen control scaffold only. This is not a performance claim.

## Source

- CSV: `{payload['source_csv']}`
- Strategy: `{payload['strategy']}`
- Phase advance: {payload['advance_deg']:.2f} deg

## Assist Windows Per 45 Deg

{_window_lines(payload['positive_torque_windows_per_45deg_period'])}

## Electrical Budget Placeholder

| Metric | Value |
|---|---:|
| Mechanical work | {budget['mechanical_work_j_per_rev']:.6f} J/rev |
| Stored energy per pulse | {budget['stored_j_per_pulse']:.6f} J |
| Unrecovered energy per pulse | {budget['unrecovered_j_per_pulse']:.6f} J |
| Pulse count per rev | {budget['pulse_count_per_rev']:.3f} |
| Unrecovered pulse input | {budget['input_j_per_rev']:.6f} J/rev |
| Mechanical minus unrecovered input | {budget['net_after_input_j_per_rev']:.6f} J/rev |

## Control Rules

{chr(10).join(f'- {rule}' for rule in payload['control_rules'])}

## Next Validation

Run energized FEMM for coil-on vs coil-off inside the scheduled windows, then compare added mechanical work against measured or simulated electrical input.
"""


def _window_lines(windows: list[dict[str, float]]) -> str:
    if not windows:
        return "- none"
    return "\n".join(f"- {w['start_deg']:.2f} to {w['end_deg']:.2f} deg" for w in windows)


def main() -> None:
    parser = argparse.ArgumentParser(description="Build selective pulse strategy from torque CSV.")
    parser.add_argument("--csv", type=Path, default=ROOT / "data/field_sim/femm_opt_gap_159p0_period45_step1.csv")
    parser.add_argument("--label", default="best_gap_candidate")
    parser.add_argument("--advance-deg", type=float, default=1.0)
    parser.add_argument("--json-out", type=Path, default=ROOT / "field_sim/femm/pulse_strategy.best_candidate.json")
    parser.add_argument("--report-out", type=Path, default=ROOT / "reports/best_candidate_pulse_strategy.md")
    args = parser.parse_args()

    curve = load_curve(args.csv)
    windows = extract_windows(curve)["positive_torque_windows"]
    stats = curve_stats(args.csv)
    payload = build_strategy_payload(
        label=args.label,
        source_csv=str(args.csv.as_posix()),
        assist_windows=windows,
        mechanical_work_j_per_rev=full_rev_equivalent(stats),
        advance_deg=args.advance_deg,
    )
    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    args.report_out.parent.mkdir(parents=True, exist_ok=True)
    args.json_out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    args.report_out.write_text(markdown_report(payload), encoding="utf-8")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
