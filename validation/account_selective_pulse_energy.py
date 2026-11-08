"""Identify what selective pulse data can and cannot establish about energy."""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from validation.analyze_pulse_assist_comparison import CASES, delta_metrics, format_metric, summarize_case  # noqa: E402
from validation.pulse_control import (  # noqa: E402
    PULSE_CURRENT_LEVELS,
    ampere_turns_from_density_ma_per_mm2,
    eml_coil_area_mm2,
    load_pulse_windows,
    pulse_current_levels_for_geometry,
)


def measured_energy_balance(*, total_input_j: float, output_j: float, losses_j: float,
                            stored_energy_change_j: float, tolerance_j: float = 1e-9) -> dict:
    """Check one supplied boundary ledger; closure is conservation, not surplus output.

    All quantities must describe the same boundary and interval. This arithmetic
    helper does not validate measurements or establish sustained operation.
    """
    values = (total_input_j, output_j, losses_j, stored_energy_change_j, tolerance_j)
    if not all(math.isfinite(value) for value in values):
        raise ValueError("Energy balance quantities must be finite")
    if min(total_input_j, output_j, losses_j, tolerance_j) < 0:
        raise ValueError("Input, output, losses and tolerance must be nonnegative")
    residual = total_input_j - output_j - losses_j - stored_energy_change_j
    closes = abs(residual) <= tolerance_j
    return {
        "status": "accounted" if closes else "imbalance",
        "balance_residual_j": residual,
        "closes_energy": closes,
        "output_to_input_ratio": output_j / total_input_j if total_input_j else None,
        "efficiency": output_j / total_input_j
        if total_input_j and closes and abs(stored_energy_change_j) <= tolerance_j else None,
        "net_boundary_output_j": output_j - total_input_j,
        "performance_claim_eligible": False,
    }


def solved_metric_case(case: dict | None) -> bool:
    """Only a validated complete sector can supply a raw work diagnostic."""
    return bool(case and case.get("sector_complete") is True
                and isinstance(case.get("work_period_j"), (int, float))
                and math.isfinite(case["work_period_j"]))


def account_case(*, level: str, case: dict | None, baseline_case: dict | None = None,
                 ampere_turns: float | None = None, nominal_wire_current_a: float | None = None) -> dict:
    raw_work = case["work_period_j"] if solved_metric_case(case) else None
    difference = None
    if solved_metric_case(case) and solved_metric_case(baseline_case):
        difference = delta_metrics(case, baseline_case)["added_work_45deg_j"]
    missing = [
        "Verified full mechanical/electromagnetic/controller operating cycle",
        "Signed electrical bus voltage and current over the same cycle, including returned energy",
        "All auxiliary, control, startup and external mechanical inputs at the chosen boundary",
        "Loaded shaft output and independently accounted losses over that cycle",
        "Changes in magnetic, electrical, mechanical and thermal stored energy",
    ]
    if nominal_wire_current_a is None:
        missing.insert(0, "Physical winding turn count and measured wire current")
    return {
        "label": level,
        "status": "insufficient_data",
        "performance_claim_eligible": False,
        "current_density_ma_per_mm2": PULSE_CURRENT_LEVELS[level],
        "winding_ampere_turns": ampere_turns,
        "nominal_wire_current_a": nominal_wire_current_a,
        "raw_work_45deg_j": raw_work,
        "added_raw_work_45deg_j": difference,
        "mechanical_work_j_per_rev": None,
        "added_mechanical_work_j_per_rev": None,
        "pulse_count_per_rev": None,
        "total_electrical_input_j_per_rev": None,
        "total_input_j_per_rev": None,
        "efficiency": None,
        "net_output_j_per_rev": None,
        "net_added_work_after_input_j_per_rev": None,
        "closes_energy": None,
        "missing_evidence": missing,
        "limitation": "One half L I squared is stored field energy, not total source input. Sampled on-angles are not pulse events. Raw 45-degree sector work is not full-cycle shaft output.",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--variant-config", type=Path, default=ROOT / "field_sim/femm/variants/gap_159p0.json")
    parser.add_argument("--windows", type=Path, default=ROOT / "field_sim/femm/pulse_strategy.gap159_eml12.json")
    parser.add_argument("--comparison-json", type=Path, default=ROOT / "reports/pulse_assist_comparison_latest.json")
    # Retain the old command-line options for existing scripts, without treating
    # guesses about magnetic storage or losses as measured source input.
    for option in ("coil-inductance-mh", "recovery-efficiency", "copper-loss-fraction", "switching-loss-j-per-pulse"):
        parser.add_argument(f"--{option}", type=float, default=None,
                            help="Legacy illustrative parameter; excluded from actual energy accounting")
    parser.add_argument("--md-out", type=Path, default=ROOT / "reports/pulse_electrical_accounting.md")
    parser.add_argument("--json-out", type=Path, default=ROOT / "reports/pulse_electrical_accounting_latest.json")
    args = parser.parse_args()
    config = json.loads(args.variant_config.read_text(encoding="utf-8"))
    assist, lockout = load_pulse_windows(args.windows)
    area = eml_coil_area_mm2(stator_inner_radius_mm=float(config["stator_inner_radius_mm"]),
                            stator_outer_radius_mm=float(config["stator_outer_radius_mm"]),
                            eml_arc_deg=float(config["eml_arc_deg"]))
    ampere_turn_levels = {level: ampere_turns_from_density_ma_per_mm2(density, area)
                         for level, density in PULSE_CURRENT_LEVELS.items()}
    wire_levels = pulse_current_levels_for_geometry(config) if "coil_turns" in config else {}
    if args.comparison_json.exists():
        comparison = json.loads(args.comparison_json.read_text(encoding="utf-8"))
    else:
        comparison = []
        for label, rel in CASES:
            path = ROOT / rel
            if path.exists():
                try:
                    comparison.append(summarize_case(label, path, assist, lockout))
                except (ValueError, KeyError):
                    comparison.append({"label": label, "status": "invalid"})
    baseline = next((row for row in comparison if row.get("label") == "coil-off"), None)
    rows = [account_case(level=level, case=next((row for row in comparison if row.get("label") == level), None),
                         baseline_case=baseline, ampere_turns=ampere_turns,
                         nominal_wire_current_a=wire_levels.get(level))
            for level, ampere_turns in ampere_turn_levels.items()]
    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    args.json_out.write_text(json.dumps(rows, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    lines = ["# Pulse Electrical Accounting", "", "**Status: insufficient data.**", "",
             "Actual total input, shaft output per revolution, efficiency, net output and energy-balance closure are unknown.",
             "The existing data are magnetostatic sector sweeps, without measured electrical waveforms or a verified repeated operating cycle.", "",
             "## Winding Excitation", "",
             "Homogenized current density multiplied by winding-region area gives ampere-turns. Both CSV current headers (`coil_current_a` and `femm_single_turn_current_a`) denote a one-turn FEMM surrogate. Neither establishes physical wire current.",
             "A physical turn count gives nominal current as ampere-turns divided by turns; actual current still requires measurement.", "",
             "| Level | Density (mA/mm²) | Winding ampere-turns | Nominal wire current (A) |",
             "|---|---:|---:|---:|"]
    for row in rows:
        lines.append(f"| {row['label']} | {row['current_density_ma_per_mm2']:.1f} | {row['winding_ampere_turns']:.3f} | {format_metric(row['nominal_wire_current_a'], 3)} |")
    lines.extend(["", "## Available Sector Diagnostics", "",
                  "These values are reported only for complete, ordered, finite 0–45° sweeps. Their numeric precision is not an uncertainty estimate. Full-state periodicity and mesh convergence remain unverified.", "",
                  "| Level | Raw 45° work (J) | Difference from coil-off (J/45°) | Total input | Efficiency | Net output | Energy closure |",
                  "|---|---:|---:|---|---|---|---|"])
    for row in rows:
        lines.append(f"| {row['label']} | {format_metric(row['raw_work_45deg_j'])} | {format_metric(row['added_raw_work_45deg_j'])} | unknown | unknown | unknown | unknown |")
    lines.extend(["", "## Required Accounting", "",
                  "For one defined system boundary and the same interval:", "",
                  "`input energy = useful output energy + losses + change in stored energy`", "",
                  "Closure means that the residual of this balance is consistent with zero within measurement uncertainty. Output exceeding input is not the definition of closure.",
                  "For example, 100 J input, 80 J useful output, 20 J loss and zero stored-energy change close the balance with 80% efficiency and −20 J output minus input.", "",
                  "The quantity `0.5 L I²` describes magnetic energy storage. Multiplying it by an assumed unrecovered fraction and guessed losses does not establish total electrical input. No placeholder loss or recovery estimate is used here.",
                  "Count actual switching events from the controller schedule; an on-angle sample count is neither an event count nor a measured time duty cycle.", "",
                  "Required evidence includes a verified repeated full state, signed bus voltage/current measurements including recovery, all auxiliary and external mechanical inputs, loaded shaft output, losses, and changes in magnetic, electrical, mechanical and thermal energy.",
                  "A positive raw sector difference cannot demonstrate sustained net power exceeding all inputs."])
    args.md_out.parent.mkdir(parents=True, exist_ok=True)
    args.md_out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("insufficient_data: total input, efficiency, net output and energy closure are unknown")


if __name__ == "__main__":
    main()
