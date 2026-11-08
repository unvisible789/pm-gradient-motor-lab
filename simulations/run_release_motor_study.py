"""Reproduce the bounded illustrative release-motor grid and its energy audit.

Run from any directory with Python and NumPy:
    python simulations/run_release_motor_study.py

The model prescribes current and speed. Results compare externally powered
commands; they are not calibrated hardware predictions or self-running claims.
"""
from __future__ import annotations

import argparse
from collections import Counter
import csv
from dataclasses import asdict
import hashlib
from itertools import product
import json
import math
from pathlib import Path
import sys
from typing import Any

import numpy as np

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from simulations.release_motor_model import (  # noqa: E402
    ReferenceMotor, ReleasePulse, simulate_cycle,
)


def record(result: Any, case_id: str) -> dict[str, Any]:
    row = asdict(result)
    row["case_id"] = case_id
    row["source_minus_shaft_power_w"] = (
        row["net_source_power_w"] - row["shaft_power_w"]
    )
    row["shaft_minus_source_power_w"] = -row["source_minus_shaft_power_w"]
    return row


def select(rows: list[dict[str, Any]], metric: str) -> dict[str, Any] | None:
    candidates = [r for r in rows if r["feasible_command"] and r[metric] is not None]
    if not candidates:
        return None
    maximum = max(r[metric] for r in candidates)
    # Analytically equal commands can differ by integration roundoff. Prefer
    # the smaller external input within this explicitly stated numeric tie.
    tied = [r for r in candidates if math.isclose(r[metric], maximum, rel_tol=1e-10, abs_tol=1e-12)]
    return min(tied, key=lambda r: (r["net_source_power_w"], r["case_id"]))


def run_study(config: dict[str, Any]) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    motor = ReferenceMotor(**config["motor"])
    grid = config["sweep"]
    intervals = grid["intervals_per_encounter"]
    verification_intervals = grid["verification_intervals_per_encounter"]
    rows: list[dict[str, Any]] = []
    commands = product(grid["rpm"], grid["peak_current_a"],
                       grid["center_phase_fraction_of_pi"], grid["width_phase_fraction_of_pi"])
    for index, (rpm, current, center, width) in enumerate(commands, start=1):
        pulse = ReleasePulse(current, center * math.pi, width * math.pi)
        rows.append(record(simulate_cycle(motor, pulse, rpm, intervals), f"case_{index:04d}"))

    feasible = [r for r in rows if r["feasible_command"]]
    rejected = Counter(v for r in rows for v in r["constraint_violations"])
    selections: dict[str, dict[str, Any] | None] = {
        "maximum_shaft_power": select(rows, "shaft_power_w"),
        "maximum_shaft_efficiency": select(rows, "shaft_efficiency"),
    }
    by_rpm = []
    for rpm in grid["rpm"]:
        group = [r for r in rows if r["rpm"] == rpm]
        power = select(group, "shaft_power_w")
        efficiency = select(group, "shaft_efficiency")
        key = format(rpm, "g")
        selections[f"rpm_{key}_maximum_shaft_power"] = power
        selections[f"rpm_{key}_maximum_shaft_efficiency"] = efficiency
        by_rpm.append({
            "rpm": rpm,
            "case_count": len(group),
            "feasible_count": sum(r["feasible_command"] for r in group),
            "rejection_counts": dict(sorted(Counter(v for r in group for v in r["constraint_violations"]).items())),
            "best_shaft_power_case_id": power["case_id"] if power else None,
            "best_shaft_efficiency_case_id": efficiency["case_id"] if efficiency else None,
        })

    verified: dict[str, dict[str, Any]] = {}
    for candidate in selections.values():
        if candidate is None or candidate["case_id"] in verified:
            continue
        pulse = ReleasePulse(candidate["peak_current_command_a"],
                             math.radians(candidate["pulse_center_phase_deg"]),
                             math.radians(candidate["pulse_width_phase_deg"]))
        result = simulate_cycle(motor, pulse, candidate["rpm"], verification_intervals)
        check = record(result, candidate["case_id"])
        if not check["feasible_command"]:
            raise RuntimeError(f"Selected {candidate['case_id']} failed higher-resolution feasibility: "
                               + ", ".join(check["constraint_violations"]))
        check["convergence_from_grid"] = {
            name + "_absolute_change": abs(check[name] - candidate[name])
            for name in ("shaft_power_w", "net_source_power_w", "shaft_efficiency")
            if check[name] is not None and candidate[name] is not None
        }
        verified[candidate["case_id"]] = check

    target = config["target"]
    target_rows = [r for r in feasible if r["rpm"] == target["rpm"]]
    target_best = select(target_rows, "shaft_power_w")
    target_verified = verified[target_best["case_id"]] if target_best else None
    summary = {
        "schema_version": 1,
        "study_title": config["study_title"],
        "model_status": config["model_status"],
        "hardware_validation_status": config["hardware_validation_status"],
        "study_goal": config["study_goal"],
        "interpretation": "Powered imposed-speed comparisons only; no self-running, generator, self-start, loaded-stability or thermal qualification claim.",
        "motor": asdict(motor),
        "parameter_provenance": config["parameter_provenance"],
        "sweep": grid,
        "case_count": len(rows),
        "feasible_count": len(feasible),
        "rejected_count": len(rows) - len(feasible),
        "rejection_counts": dict(sorted(rejected.items())),
        "feasibility_definition": "Passes the model's conservative whole-encounter voltage envelope, current cap, pulse gate duty, release-only timing, cancellation cap and integration checks. Envelope rejection does not prove every rejected waveform physically impossible.",
        "by_rpm": by_rpm,
        "selection_case_ids": {name: row["case_id"] if row else None for name, row in selections.items()},
        "selection_tie_break": "For equal objective values within relative tolerance 1e-10 or absolute tolerance 1e-12, choose lower net source input, then case ID.",
        "verified_selected_cases": verified,
        "energy_audit": {
            "max_abs_residual_j_per_revolution_all_grid_cases": max(abs(r["energy_residual_per_revolution_j"]) for r in rows),
            "max_relative_residual_all_grid_cases": max(r["relative_energy_residual"] for r in rows),
            "max_abs_stored_energy_change_j_per_revolution_all_grid_cases": max(abs(r["stored_energy_change_per_revolution_j"]) for r in rows),
            "max_abs_passive_work_j_per_coil_encounter_all_grid_cases": max(abs(r["single_coil_encounter"]["passive_work_j"]) for r in rows),
            "max_instantaneous_residual_w_per_coil_all_grid_cases": max(r["max_instantaneous_energy_residual_w_per_coil"] for r in rows),
            "minimum_source_minus_shaft_power_w_feasible": min((r["source_minus_shaft_power_w"] for r in feasible), default=None),
            "feasible_positive_net_output_case_count": sum(r["shaft_minus_source_power_w"] > 1e-9 for r in feasible),
            "balance": "net_source = shaft + copper + unrecovered_return + controller + mechanical_loss + change_in_stored_energy",
        },
        "comparison_350w": {
            **target,
            "feasible_cases_at_comparison_rpm": len(target_rows),
            "feasible_cases_reaching_comparison": sum(r["shaft_power_w"] >= target["shaft_power_w"] for r in target_rows),
            "verified_best_shaft_power_w": target_verified["shaft_power_w"] if target_verified else None,
            "shortfall_w": target["shaft_power_w"] - target_verified["shaft_power_w"] if target_verified else None,
        },
        "thermal_scope": "No thermal simulation or duty qualification. Every modeled coil i^2 R term is integrated over the full encounter. Real hold, freewheel, decay and release currents must all be counted, regardless of PWM switch duty. Published 10% actuator duty alone does not qualify this application.",
        "sensitivity_check": {"configuration": config.get("sensitivity_check"), "executed": False,
                              "reason": "This bounded study uses the nominal reference only; no measured thermal state exists."},
        "sources": config["sources"],
        "reproducibility": {"numpy_version": np.__version__,
                            "command": "python simulations/run_release_motor_study.py"},
    }
    return summary, rows


def fmt(value: Any, digits: int = 6) -> str:
    return "—" if value is None else f"{value:.{digits}g}"


def render_report(summary: dict[str, Any]) -> str:
    cases = summary["verified_selected_cases"]
    selected = summary["selection_case_ids"]
    power = cases.get(selected["maximum_shaft_power"])
    efficiency = cases.get(selected["maximum_shaft_efficiency"])
    audit = summary["energy_audit"]
    motor = summary["motor"]
    grid = summary["sweep"]
    lines = [
        "# Illustrative release-cycle accounting study",
        "",
        "## Status and objective",
        "",
        "**Illustrative analytic reference; no hardware prediction or hardware validation.** "
        "The objective is sustained shaft output greater than all net external input over a repeatable full cycle. "
        "The results below compare externally powered commands at imposed speed. They establish no self-running or generator capability, "
        "self-starting, stable loaded rotation, or thermal/mechanical reliability.",
        "",
        "**This is not an optimization or evaluation of the user's magnetic geometry.** The sinusoidal magnetic map and its amplitudes are "
        "assumed accounting examples. This grid provides no evidence about the real machine's output and cannot determine actual rated power "
        "or sustained net-power capability. It cannot assess the historical 350 W figure.",
        "",
        f"The configured grid contains **{summary['case_count']:,} commands**: "
        f"{len(grid['rpm'])} speeds × {len(grid['peak_current_a'])} peak currents × "
        f"{len(grid['center_phase_fraction_of_pi'])} phase centers × {len(grid['width_phase_fraction_of_pi'])} widths. "
        f"**{summary['feasible_count']:,} pass** the reference constraints; **{summary['rejected_count']:,} are rejected**. "
        f"No feasible command has positive shaft-minus-source power ({audit['feasible_positive_net_output_case_count']} cases). "
        "This energy-consistent model has no unaccounted external energy source. Its outcome is a consequence of its stated constitutive equations, "
        "not an experimental discovery or a universal search over hardware.",
        "",
        "## Best feasible powered comparisons",
        "",
        f"Selections use only feasible grid commands at {grid['intervals_per_encounter']:,} intervals per encounter. "
        f"Every global and per-speed selection is re-evaluated at {grid['verification_intervals_per_encounter']:,} intervals; "
        "all selected commands must pass again. The table reports those verified values. Power and efficiency are separate objectives. "
        "Numerical ties (relative tolerance 1e-10 or absolute tolerance 1e-12) select lower net source input, then case ID.",
        "",
        "| Selection | Speed (rpm) | Peak current (A) | Center / width (phase °) | Shaft power (W) | Net source input (W) | Source − shaft deficit (W) | Efficiency |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for name, result in (("Maximum shaft power", power), ("Maximum shaft efficiency", efficiency)):
        if result:
            lines.append(f"| {name} | {fmt(result['rpm'])} | {fmt(result['peak_current_command_a'])} | "
                         f"{fmt(result['pulse_center_phase_deg'])} / {fmt(result['pulse_width_phase_deg'])} | "
                         f"{fmt(result['shaft_power_w'])} | {fmt(result['net_source_power_w'])} | "
                         f"{fmt(result['source_minus_shaft_power_w'])} | {100 * result['shaft_efficiency']:.3f}% |")
        else:
            lines.append(f"| {name} | — | — | — | — | — | — | — |")
    lines += ["", "A positive deficit means the external source supplies more power than the shaft delivers. "
              "Net source input includes gross electrical draw, actual recovered bus energy and controller consumption. "
              "Mechanical drag and forward bridge losses are optimistically zero in this reference, so the deficit understates an equivalent real system's losses.",
              "", "| Speed (rpm) | Sampled | Feasible | Best verified shaft power (W) | Best verified efficiency |",
              "|---|---:|---:|---:|---:|"]
    for group in summary["by_rpm"]:
        best_power = cases.get(group["best_shaft_power_case_id"])
        best_eff = cases.get(group["best_shaft_efficiency_case_id"])
        eff_text = f"{100 * best_eff['shaft_efficiency']:.3f}%" if best_eff else "—"
        lines.append(f"| {fmt(group['rpm'])} | {group['case_count']} | {group['feasible_count']} | "
                     f"{fmt(best_power['shaft_power_w']) if best_power else '—'} | {eff_text} |")
    lines += [
        "",
        "Feasibility uses a conservative analytical upper bound on required absolute terminal voltage over the entire encounter, "
        "including back EMF outside the pulse. Some rejected commands could pass a tighter voltage analysis; a conservative rejection is not proof of physical impossibility. "
        "The driver must support both voltage polarities and a receptive regenerative bus. Current cap, gate duty, release-only phase, cancellation cap, "
        "pulse resolution and energy closure are also checked. Rejection counts can overlap: "
        + ", ".join(f"`{name}`: {count}" for name, count in summary["rejection_counts"].items()) + ".",
        "",
        "## Full-cycle energy account",
        "",
        "For each complete repeating cycle the model enforces:",
        "",
        "```text",
        "E_source = E_draw − eta_return × E_returned_terminal + E_controller",
        "E_source − W_shaft = E_copper + E_unrecovered_return + E_controller",
        "                   + E_mechanical_loss + ΔE_stored",
        "```",
        "",
        "`E_returned_terminal` integrates only negative terminal power. Recoverable inductive energy is not assumed to equal "
        "all peak coil storage, and recovery is not subtracted twice from signed terminal energy. The passive PM potential and "
        "coil current return to their starting states, so stored energy does not supply repeated net work. Electrical release reduces "
        "the braking part of this chosen potential profile; the added cycle work is paid for through the electrical port.",
        "",
        "The energy/coenergy framework is supported by [1]; the parameter values and waveform are the stated reference assumptions.",
        "",
        "| Numerical audit across all grid commands | Value |",
        "|---|---:|",
        f"| Maximum absolute cycle balance residual | {fmt(audit['max_abs_residual_j_per_revolution_all_grid_cases'])} J/rev |",
        f"| Maximum relative cycle residual | {fmt(audit['max_relative_residual_all_grid_cases'])} |",
        f"| Maximum instantaneous residual per coil | {fmt(audit['max_instantaneous_residual_w_per_coil_all_grid_cases'])} W |",
        f"| Maximum absolute stored-energy change | {fmt(audit['max_abs_stored_energy_change_j_per_revolution_all_grid_cases'])} J/rev |",
        f"| Maximum absolute passive work per coil encounter | {fmt(audit['max_abs_passive_work_j_per_coil_encounter_all_grid_cases'])} J |",
        f"| Smallest source-minus-shaft deficit among feasible commands | {fmt(audit['minimum_source_minus_shaft_power_w_feasible'])} W |",
        "",
    ]
    if cases:
        max_power_change = max(r["convergence_from_grid"]["shaft_power_w_absolute_change"] for r in cases.values())
        max_input_change = max(r["convergence_from_grid"]["net_source_power_w_absolute_change"] for r in cases.values())
        lines += [f"The {len(cases)} distinct selected commands remain feasible at the finer resolution. "
                  f"Maximum changes are {fmt(max_power_change)} W shaft power and {fmt(max_input_change)} W source input. "
                  "This checks numerical integration of the assumed model, not agreement with hardware.", ""]
    lines += [
        "## Assumptions and limits",
        "",
        f"- **Magnetic map:** `U_pm = −{motor['pm_potential_amplitude_j']} cos(phase)` J per coil and "
        f"`psi_pm = {motor['pm_flux_linkage_amplitude_wb_turn']} cos(phase)` Wb-turn, with "
        f"`phase = {motor['encounters_per_coil_per_revolution']} × mechanical_angle`. "
        "Both amplitudes and the sinusoidal profiles are illustrative, not extracted from FEMM, holding force or measurements. "
        f"The chosen ratio gives {motor['pm_potential_amplitude_j'] / motor['pm_flux_linkage_amplitude_wb_turn']:.3g} A instantaneous cancellation; "
        "overcancellation is prohibited.",
        f"- **Coils and repetition:** {motor['coil_count']} coils, {motor['encounters_per_coil_per_revolution']} encounters per coil per revolution, "
        f"{motor['coil_count'] * motor['encounters_per_coil_per_revolution']} total coil encounters per revolution. "
        "This is the supplied double-face arrangement, not a 2:1 pulse-count shortcut. Summed cycle energy does not establish the actual instantaneous torque ripple or magnetic coupling.",
        f"- **Electrical parameters:** constant {1000 * motor['inductance_h']:g} mH inductance is an unmeasured assumption. "
        f"The {motor['resistance_ohm']:g} Ω nominal resistance, {motor['bus_voltage_v']:g} V, {motor['design_current_cap_a']:g} A "
        f"and {100 * motor['max_gate_duty_fraction']:g}% intermittent-duty figures come from APW actuator metadata [2], "
        "used only to define a reference scenario. They are not validated rotating-machine parameters, a certified peak pulse limit or a high-frequency operating envelope.",
        f"- **Losses and recovery:** {100 * motor['return_path_efficiency']:g}% of actually returned terminal energy is assumed to reach the bus; "
        f"controller draw is {motor['controller_power_w']:g} W total. Return efficiency and controller draw are assumptions. "
        "Ideal forward conversion, zero switching/conduction losses, zero mechanical drag and no reserved voltage margin are optimistic. "
        "No demagnetization, saturation, hysteresis, eddy-current, heat-transfer or bus-storage model is supplied.",
        "- **Thermal duty:** the copper-loss integral includes all modeled coil current over the entire encounter. "
        "Actual hold, freewheel, decay and release currents all contribute to `i²R`; the PWM switching fraction alone is not a thermal duty estimate. "
        "A published 10% intermittent actuator rating cannot certify continuous motor operation. The configured 80 °C sensitivity metadata is not executed here "
        "and is not an allowable winding temperature or an established equilibrium.",
        "- **Evidence needed for a hardware result:** measured or validated current-dependent flux linkage, torque and inductance across the full angle cycle; "
        "complete source/return and controller energy measurements; actual thermal duty and losses; and a loaded dynamic test that returns all energy stores to the same state. "
        "Permanent holding without input [3] is not an energy source for repeatable net shaft work.",
        "",
        "## Reproduce and inspect",
        "",
        "```sh",
        "python simulations/run_release_motor_study.py",
        "```",
        "",
        "Configuration: `configs/release_motor_reference.json`. All 1,560 sampled commands, including rejected ones and their reasons, "
        "are recorded in `data/release_motor_study.csv`; only feasible commands are selected. "
        "The full verified selected cases, energy balances, configuration provenance and source-file hashes are in `reports/release_motor_study.json`. "
        "The runner is deterministic and uses NumPy plus the repository's analytic model; it performs no fitting or external data download.",
        "",
        "## Sources and provenance",
        "",
        "Published sources support only the theory or metadata described below; none validates the illustrative magnetic amplitudes or this motor's output.",
        "",
    ]
    lines += [f"{index}. [{source['title']}]({source['url']}) — {source['use']}" for index, source in enumerate(summary["sources"], start=1)]
    return "\n".join(lines) + "\n"


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    flattened = []
    for row in rows:
        flat = {"case_id": row["case_id"]}
        for key, value in row.items():
            if isinstance(value, dict):
                flat.update({f"{key}.{name}": number for name, number in value.items()})
            elif isinstance(value, list):
                flat[key] = ";".join(value)
            else:
                flat[key] = value
        flattened.append(flat)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(flattened[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(flattened)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=REPO_ROOT / "configs/release_motor_reference.json")
    parser.add_argument("--output-root", type=Path, default=REPO_ROOT,
                        help="Root beneath which data/ and reports/ are written")
    args = parser.parse_args()
    config = json.loads(args.config.read_text(encoding="utf-8"))
    summary, rows = run_study(config)
    summary["reproducibility"]["sha256"] = {
        "configuration": hashlib.sha256(args.config.read_bytes()).hexdigest(),
        "model": hashlib.sha256((REPO_ROOT / "simulations/release_motor_model.py").read_bytes()).hexdigest(),
        "runner": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    }
    for directory in ("reports", "data"):
        (args.output_root / directory).mkdir(parents=True, exist_ok=True)
    write_csv(args.output_root / "data/release_motor_study.csv", rows)
    (args.output_root / "reports/release_motor_study.json").write_text(
        json.dumps(summary, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    (args.output_root / "reports/release_motor_study.md").write_text(render_report(summary), encoding="utf-8")
    print(json.dumps({"cases": summary["case_count"], "feasible": summary["feasible_count"],
                      "rejected": summary["rejected_count"], "selected": summary["selection_case_ids"]}, indent=2))


if __name__ == "__main__":
    main()
