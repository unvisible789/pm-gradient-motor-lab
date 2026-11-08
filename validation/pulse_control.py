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


def ampere_turns_from_density_ma_per_mm2(density_ma_per_mm2: float, coil_area_mm2: float) -> float:
    """Return homogenized winding ampere-turns, not conductor current."""
    if not all(math.isfinite(x) for x in (density_ma_per_mm2, coil_area_mm2)) or coil_area_mm2 <= 0:
        raise ValueError("Density must be finite and coil area must be positive and finite")
    return density_ma_per_mm2 * coil_area_mm2 / 1000.0


def current_from_density_ma_per_mm2(density_ma_per_mm2: float, coil_area_mm2: float, *, turns: int) -> float:
    """Convert homogenized J times winding area to wire A with explicit turns."""
    if isinstance(turns, bool) or not isinstance(turns, int) or turns <= 0:
        raise ValueError("A positive integer winding turn count is required")
    return ampere_turns_from_density_ma_per_mm2(density_ma_per_mm2, coil_area_mm2) / turns


def pulse_current_levels_for_geometry(config: dict) -> dict[str, float]:
    if "coil_turns" not in config:
        raise ValueError("coil_turns is missing; homogenized density times area is ampere-turns, not wire amperes")
    area = eml_coil_area_mm2(
        stator_inner_radius_mm=float(config["stator_inner_radius_mm"]),
        stator_outer_radius_mm=float(config["stator_outer_radius_mm"]),
        eml_arc_deg=float(config["eml_arc_deg"]),
    )
    return {level: current_from_density_ma_per_mm2(density, area, turns=config["coil_turns"])
            for level, density in PULSE_CURRENT_LEVELS.items()}


def count_selected_pulses(*, rotor_gradient_count: int, eml_count: int,
                          selected_events_per_eml: list[list[int]] | None = None) -> int:
    """Count selected gradient encounters per coil in one mechanical revolution.

    Event indices identify encounters, not sampled angles or an EML/gradient ratio.
    Omitting the selection explicitly assumes one pulse at every encounter.
    """
    for value in (rotor_gradient_count, eml_count):
        if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
            raise ValueError("Gradient and coil counts must be positive integers")
    if selected_events_per_eml is None:
        return rotor_gradient_count * eml_count
    if len(selected_events_per_eml) != eml_count:
        raise ValueError("Provide one selected-event list for every coil")
    for events in selected_events_per_eml:
        if any(isinstance(e, bool) or not isinstance(e, int) or not 0 <= e < rotor_gradient_count for e in events):
            raise ValueError("Selected gradient event index is invalid")
        if len(set(events)) != len(events):
            raise ValueError("Duplicate selected gradient encounter")
    return sum(len(events) for events in selected_events_per_eml)


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


def estimate_revolution_energy(*, mechanical_work_j_per_rev: float, electrical_model: PulseElectricalModel) -> dict:
    """Deprecated magnetic-storage illustration, never a motor input-energy model.

    One half L I squared is stored field energy. Motion-induced voltage, copper
    heating, switching loss and auxiliary power are absent from this model.
    """
    m = electrical_model
    values = (m.coil_inductance_mh, m.pulse_current_a, m.recovery_efficiency,
              m.eml_count, m.pulses_per_eml_per_rev, mechanical_work_j_per_rev)
    if not all(math.isfinite(x) for x in values):
        raise ValueError("Energy illustration inputs must be finite")
    if m.coil_inductance_mh < 0 or m.pulse_current_a < 0 or not 0 <= m.recovery_efficiency <= 1:
        raise ValueError("Invalid inductance, current or recovery fraction")
    if m.eml_count <= 0 or int(m.eml_count) != m.eml_count or m.pulses_per_eml_per_rev < 0 or int(m.pulses_per_eml_per_rev) != m.pulses_per_eml_per_rev:
        raise ValueError("Coil and per-coil event counts must be whole numbers")
    stored = 0.5 * (m.coil_inductance_mh / 1000.0) * m.pulse_current_a ** 2
    unrecovered = stored * (1.0 - m.recovery_efficiency)
    count = int(m.eml_count * m.pulses_per_eml_per_rev)
    return {
        "status": "illustrative", "performance_claim_eligible": False,
        "stored_j_per_pulse": stored, "unrecovered_j_per_pulse": unrecovered,
        "pulse_count_per_rev": count,
        "illustrative_unrecovered_magnetic_energy_j_per_rev": unrecovered * count,
        "input_j_per_rev": None,
        "mechanical_work_j_per_rev": mechanical_work_j_per_rev,
        "net_after_input_j_per_rev": None,
        "limitation": "Stored magnetic energy is not total electrical input; use signed measured bus waveforms and a full-cycle storage ledger.",
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
