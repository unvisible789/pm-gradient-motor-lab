from __future__ import annotations

from dataclasses import dataclass


Window = dict[str, float]


@dataclass(frozen=True)
class PulseElectricalModel:
    coil_inductance_mh: float
    pulse_current_a: float
    recovery_efficiency: float
    eml_count: int
    pulses_per_eml_per_rev: float


def merge_windows(windows: list[Window], min_gap_deg: float = 0.0) -> list[Window]:
    ordered = sorted(
        (
            {"start_deg": float(window["start_deg"]), "end_deg": float(window["end_deg"])}
            for window in windows
            if float(window["end_deg"]) > float(window["start_deg"])
        ),
        key=lambda window: window["start_deg"],
    )
    if not ordered:
        return []

    merged = [ordered[0]]
    for window in ordered[1:]:
        current = merged[-1]
        if window["start_deg"] - current["end_deg"] <= min_gap_deg:
            current["end_deg"] = max(current["end_deg"], window["end_deg"])
        else:
            merged.append(window)
    return [_rounded(window) for window in merged]


def build_phase_schedule(
    windows_per_period: list[Window],
    *,
    period_deg: float = 45.0,
    periods_per_rev: int = 8,
    advance_deg: float = 0.0,
    min_pulse_width_deg: float = 0.0,
) -> list[Window]:
    schedule: list[Window] = []
    for period in range(periods_per_rev):
        offset = period * period_deg
        for window in windows_per_period:
            start = float(window["start_deg"]) + offset - advance_deg
            end = float(window["end_deg"]) + offset - advance_deg
            if end - start >= min_pulse_width_deg:
                schedule.extend(_wrap_window(start, end, period_deg * periods_per_rev))
    return [_rounded(window) for window in schedule]


def estimate_revolution_energy(
    *,
    mechanical_work_j_per_rev: float,
    electrical_model: PulseElectricalModel,
) -> dict[str, float]:
    stored_j = (
        0.5
        * (electrical_model.coil_inductance_mh / 1000.0)
        * electrical_model.pulse_current_a**2
    )
    unrecovered_j = stored_j * (1.0 - electrical_model.recovery_efficiency)
    pulse_count = electrical_model.eml_count * electrical_model.pulses_per_eml_per_rev
    input_j = unrecovered_j * pulse_count
    return {
        "stored_j_per_pulse": stored_j,
        "unrecovered_j_per_pulse": unrecovered_j,
        "pulse_count_per_rev": pulse_count,
        "input_j_per_rev": input_j,
        "mechanical_work_j_per_rev": mechanical_work_j_per_rev,
        "net_after_input_j_per_rev": mechanical_work_j_per_rev - input_j,
    }


def _rounded(window: Window) -> Window:
    return {
        "start_deg": round(float(window["start_deg"]), 6),
        "end_deg": round(float(window["end_deg"]), 6),
    }


def _wrap_window(start: float, end: float, revolution_deg: float) -> list[Window]:
    if start < 0:
        return [
            {"start_deg": start + revolution_deg, "end_deg": revolution_deg},
            {"start_deg": 0.0, "end_deg": end},
        ]
    if end > revolution_deg:
        return [
            {"start_deg": start, "end_deg": revolution_deg},
            {"start_deg": 0.0, "end_deg": end - revolution_deg},
        ]
    return [{"start_deg": start, "end_deg": end}]
