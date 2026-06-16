from __future__ import annotations

import json
import math
from dataclasses import dataclass
from pathlib import Path


Window = dict[str, float]

PULSE_CURRENT_LEVELS = {
    "low": 5.0,
    "medium": 10.0,
    "high": 20.0,
}


def eml_coil_area_mm2(
    *,
    stator_inner_radius_mm: float,
    stator_outer_radius_mm: float,
    eml_arc_deg: float,
    coil_inset_mm: float = 8.0,
    coil_arc_fraction: float = 0.55,
) -> float:
    coil_inner = stator_inner_radius_mm + coil_inset_mm
    coil_outer = stator_outer_radius_mm - coil_inset_mm
    arc_deg = eml_arc_deg * coil_arc_fraction
    return (math.pi / 360.0) * arc_deg * (coil_outer**2 - coil_inner**2)


def current_from_density_ma_per_mm2(density_ma_per_mm2: float, coil_area_mm2: float) -> float:
    return density_ma_per_mm2 * coil_area_mm2 / 1000.0


def pulse_current_levels_for_geometry(config: dict[str, float]) -> dict[str, float]:
    area = eml_coil_area_mm2(
        stator_inner_radius_mm=float(config["stator_inner_radius_mm"]),
        stator_outer_radius_mm=float(config["stator_outer_radius_mm"]),
        eml_arc_deg=float(config["eml_arc_deg"]),
    )
    return {
        level: current_from_density_ma_per_mm2(density, area)
        for level, density in PULSE_CURRENT_LEVELS.items()
    }


def angle_mod(angle_deg: float, period_deg: float) -> float:
    if period_deg <= 0:
        return angle_deg
    value = angle_deg % period_deg
    return value + period_deg if value < 0 else value


def angle_in_windows(angle_deg: float, windows: list[Window], period_deg: float = 45.0) -> bool:
    local = angle_mod(angle_deg, period_deg)
    for window in windows:
        start = float(window["start_deg"])
        end = float(window["end_deg"])
        if start <= local <= end:
            return True
    return False


def active_eml_index(
    angle_deg: float,
    *,
    eml_count: int,
    eml_offset_deg: float,
    period_deg: float = 45.0,
) -> int:
    local = angle_mod(angle_deg, period_deg)
    index = int(math.floor((local + period_deg / 2.0 - eml_offset_deg) / period_deg))
    return index % eml_count


def load_pulse_windows(path: Path) -> tuple[list[Window], list[Window]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    assist = payload["positive_torque_windows_per_45deg_period"]
    lockout = payload.get("negative_torque_lockout_windows_per_45deg_period", [])
    return assist, lockout


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
