"""Energy-consistent, illustrative model of a trailing-edge release motor.

This is a reduced-order mathematical reference, NOT a model calibrated to the
repository's FEMM geometry, an APW magnet, or measured motor performance. The
magnetic-potential amplitude, flux linkage, and inductance must be measured or
obtained from a validated electromagnetic solution before hardware predictions.

Conventions
-----------
All angles are mechanical radians except ``phase``. ``n`` is the number of
magnetic encounters PER COIL PER REVOLUTION, not the magnet-to-coil ratio.
For one encounter, phase = n * theta, 0 <= phase <= 2*pi. At positive speed:

    U_pm = -U0*cos(phase)              [J per coil]
    psi_pm = psi0*cos(phase)           [Wb-turn per coil]
    lambda = L*i + psi_pm              [Wb-turn]
    tau = -dU_pm/dtheta + i*dpsi_pm/dtheta
    v = R*i + L*di/dt + omega*dpsi_pm/dtheta
    E_stored = U_pm + L*i**2/2

Therefore the exact instantaneous port balance is

    v*i = R*i**2 + tau*omega + dE_stored/dt.

These equations follow from a coenergy function
W'(i, theta) = L*i**2/2 + i*psi_pm(theta) - U_pm(theta), with constant L.
The total magnetic/magnet storage in the chosen effective model is
E = i*lambda - W' = U_pm + L*i**2/2. Its arbitrary reference offset can be
negative; only differences are physical. No energy is assigned to the PM field
merely because that field continues to exist.

Passive torque is negative on phase in (0, pi). A negative current confined to
that interval opposes PM flux and reduces that braking torque. A sin-squared
pulse makes current and its first derivative continuous at both gate edges.
For this analytic map, I_cancel = U0 / psi0 cancels the passive torque at that
instant. Restricting peak current to I_cancel avoids relabeling extra pushing
as release. Gate timing, rise/fall voltage, copper loss, returned terminal
energy, and electrical control consumption all remain in the account.

Current is prescribed and voltage is solved. A command is feasible only when
its voltage, current, and gate-duty constraints pass. Speed is imposed, as by a
dynamometer: this does NOT prove self-starting, stable loaded rotation, control
stability, or thermal/mechanical reliability. Aggregate cycle energies add over
identical coils; their instantaneous torques need actual coil phase positions.
Voltage certification uses an analytic upper bound, not a sampled-only maximum;
it may conservatively reject a command that a tighter bound could admit. Nonzero
pulses must span at least 32 phase-grid intervals before their integrated results
can be accepted. Manufacturer thermal/pulse limits remain unqualified.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, replace
import math
from typing import Any

import numpy as np

TAU = 2.0 * math.pi


def _integrate(y: np.ndarray, x: np.ndarray) -> float:
    # NumPy 1.x/2.x compatibility, without an extra SciPy dependency.
    trap = getattr(np, "trapezoid", None)
    if trap is None:
        trap = np.trapz
    return float(trap(y, x))


@dataclass(frozen=True)
class ReferenceMotor:
    encounters_per_coil_per_revolution: int = 16
    coil_count: int = 16
    resistance_ohm: float = 55.9
    inductance_h: float = 0.005
    pm_potential_amplitude_j: float = 0.002
    pm_flux_linkage_amplitude_wb_turn: float = 0.005
    bus_voltage_v: float = 24.0
    design_current_cap_a: float = 0.43
    max_gate_duty_fraction: float = 0.10
    return_path_efficiency: float = 0.75
    controller_power_w: float = 0.25
    mechanical_loss_power_w: float = 0.0
    prohibit_overcancellation: bool = True

    def validate(self) -> None:
        for key in ("encounters_per_coil_per_revolution", "coil_count"):
            value = getattr(self, key)
            if isinstance(value, bool) or not isinstance(value, (int, np.integer)) or value <= 0:
                raise ValueError(f"{key} must be a positive integer")
        positive = (
            "resistance_ohm", "inductance_h", "pm_potential_amplitude_j",
            "pm_flux_linkage_amplitude_wb_turn", "bus_voltage_v", "design_current_cap_a",
        )
        for key in positive:
            value = getattr(self, key)
            if not math.isfinite(value) or value <= 0:
                raise ValueError(f"{key} must be finite and positive")
        for key in ("controller_power_w", "mechanical_loss_power_w"):
            value = getattr(self, key)
            if not math.isfinite(value) or value < 0:
                raise ValueError(f"{key} must be finite and nonnegative")
        if not 0 < self.max_gate_duty_fraction <= 1:
            raise ValueError("max_gate_duty_fraction must be in (0, 1]")
        if not 0 <= self.return_path_efficiency <= 1:
            raise ValueError("return_path_efficiency must be in [0, 1]")

    @property
    def full_cancellation_current_a(self) -> float:
        return self.pm_potential_amplitude_j / self.pm_flux_linkage_amplitude_wb_turn


@dataclass(frozen=True)
class ReleasePulse:
    """Negative-current release pulse, given positive peak magnitude and radians."""
    peak_current_a: float
    center_phase_rad: float
    width_phase_rad: float

    def validate(self) -> None:
        if not all(math.isfinite(x) for x in (
            self.peak_current_a, self.center_phase_rad, self.width_phase_rad
        )):
            raise ValueError("pulse values must be finite")
        if self.peak_current_a < 0:
            raise ValueError("peak_current_a is a magnitude and cannot be negative")
        if not 0 < self.width_phase_rad <= TAU:
            raise ValueError("width_phase_rad must be in (0, 2*pi]")
        if not 0 <= self.center_phase_rad <= TAU:
            raise ValueError("center_phase_rad must lie within one encounter")

    @property
    def gate_duty_fraction(self) -> float:
        return self.width_phase_rad / TAU if self.peak_current_a else 0.0

    @property
    def start_phase_rad(self) -> float:
        return self.center_phase_rad - self.width_phase_rad / 2.0

    @property
    def end_phase_rad(self) -> float:
        return self.center_phase_rad + self.width_phase_rad / 2.0


@dataclass
class CycleResult:
    """Full-rotor results, with clearly scoped single-coil encounter energies."""
    rpm: float
    peak_current_command_a: float
    pulse_center_phase_deg: float
    pulse_width_phase_deg: float
    pulse_width_mechanical_deg: float
    pulse_duration_ms: float
    gate_duty_fraction: float
    encounters_per_coil_per_revolution: int
    coil_count: int
    encounters_per_coil_per_second: float
    total_coil_pulses_per_revolution: int
    total_coil_pulses_per_second: float
    peak_abs_voltage_v: float
    voltage_upper_bound_v: float
    peak_abs_current_a: float
    resolved_pulse_intervals: float
    coil_rms_current_a: float
    cancellation_fraction_peak: float
    open_circuit_emf_peak_v: float
    feasible_command: bool
    constraint_violations: list[str]
    single_coil_encounter: dict[str, float]
    electromagnetic_work_per_revolution_j: float
    shaft_work_per_revolution_j: float
    shaft_power_w: float
    mean_shaft_torque_nm: float
    gross_draw_per_revolution_j: float
    returned_terminal_energy_per_revolution_j: float
    recovered_bus_energy_per_revolution_j: float
    unrecovered_return_energy_per_revolution_j: float
    signed_terminal_energy_per_revolution_j: float
    copper_loss_per_revolution_j: float
    controller_energy_per_revolution_j: float
    mechanical_loss_per_revolution_j: float
    stored_energy_change_per_revolution_j: float
    net_source_energy_per_revolution_j: float
    net_source_power_w: float
    shaft_efficiency: float | None
    energy_residual_per_revolution_j: float
    relative_energy_residual: float
    max_instantaneous_energy_residual_w_per_coil: float
    intervals_per_encounter: int

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def simulate_cycle(
    motor: ReferenceMotor,
    pulse: ReleasePulse,
    rpm: float,
    intervals: int = 4096,
    return_trace: bool = False,
) -> CycleResult | tuple[CycleResult, dict[str, np.ndarray]]:
    """Evaluate one full repeat, then scale energies to a rotor revolution.

    Supply and regenerative energy are counted at distinct ports:
      E_terminal = E_draw - E_returned
      E_source = E_draw - eta_return*E_returned + E_controller
               = E_terminal + (1-eta_return)*E_returned + E_controller.

    Recovery is NEVER subtracted from the signed terminal integral a second
    time. An ideal four-quadrant bridge and a receptive DC bus are assumed,
    apart from the specified return efficiency and fixed controller draw.
    Real switching/conduction losses and bus storage limits need measured maps.
    A zero-current segment still needs v = back-EMF; the voltage constraint
    therefore covers the entire encounter, not only the pulse gate.
    """
    motor.validate()
    pulse.validate()
    if not math.isfinite(rpm) or rpm <= 0:
        raise ValueError("rpm must be finite and positive")
    if isinstance(intervals, bool) or not isinstance(intervals, int) or intervals < 128:
        raise ValueError("intervals must be an integer >= 128")
    if pulse.start_phase_rad < -1e-12 or pulse.end_phase_rad > TAU + 1e-12:
        raise ValueError("pulse must be wholly inside the sampled encounter")

    n = motor.encounters_per_coil_per_revolution
    omega = rpm * TAU / 60.0
    phase = np.linspace(0.0, TAU, intervals + 1)
    theta = phase / n
    time = theta / omega
    current = np.zeros_like(phase)
    di_dphase = np.zeros_like(phase)
    active = (phase > pulse.start_phase_rad) & (phase < pulse.end_phase_rad)
    x = (phase[active] - pulse.start_phase_rad) / pulse.width_phase_rad
    current[active] = -pulse.peak_current_a * np.sin(math.pi * x)**2
    di_dphase[active] = -(pulse.peak_current_a * math.pi / pulse.width_phase_rad) * np.sin(TAU * x)
    di_dt = di_dphase * n * omega

    potential = -motor.pm_potential_amplitude_j * np.cos(phase)
    dpotential_dtheta = motor.pm_potential_amplitude_j * n * np.sin(phase)
    flux_linkage = motor.pm_flux_linkage_amplitude_wb_turn * np.cos(phase)
    dflux_dtheta = -motor.pm_flux_linkage_amplitude_wb_turn * n * np.sin(phase)
    passive_torque = -dpotential_dtheta
    release_torque = current * dflux_dtheta
    torque = passive_torque + release_torque
    emf = dflux_dtheta * omega
    voltage = motor.resistance_ohm * current + motor.inductance_h * di_dt + emf
    terminal_power = voltage * current
    copper_power = motor.resistance_ohm * current**2
    mechanical_power = torque * omega
    stored = potential + 0.5 * motor.inductance_h * current**2
    stored_derivative = dpotential_dtheta * omega + motor.inductance_h * current * di_dt
    instantaneous_residual = terminal_power - copper_power - mechanical_power - stored_derivative

    terminal = _integrate(terminal_power, time)
    copper = _integrate(copper_power, time)
    work = _integrate(torque, theta)
    passive_work = _integrate(passive_torque, theta)
    release_work = _integrate(release_torque, theta)
    draw = _integrate(np.maximum(terminal_power, 0.0), time)
    returned = _integrate(np.maximum(-terminal_power, 0.0), time)
    delta_stored = float(stored[-1] - stored[0])
    period = float(time[-1])
    rms_current = math.sqrt(max(0.0, _integrate(current**2, time) / period))
    factor = n * motor.coil_count
    revolution_s = 60.0 / rpm
    controller_energy = motor.controller_power_w * revolution_s
    mechanical_loss = motor.mechanical_loss_power_w * revolution_s
    recovered = motor.return_path_efficiency * returned * factor
    unrecovered = (1.0 - motor.return_path_efficiency) * returned * factor
    source_energy = factor * draw - recovered + controller_energy
    shaft_work = work * factor - mechanical_loss
    total_loss = copper * factor + unrecovered + controller_energy + mechanical_loss
    residual = source_energy - shaft_work - total_loss - delta_stored * factor
    scale = max(abs(source_energy), abs(shaft_work), abs(total_loss), 1e-12)
    relative_residual = abs(residual) / scale

    violations = []
    peak_voltage = float(np.max(np.abs(voltage)))
    peak_current = float(np.max(np.abs(current)))
    resolved_pulse_intervals = pulse.width_phase_rad * intervals / TAU if pulse.peak_current_a else 0.0
    # A pulse entirely between samples has zero sampled current and zero
    # residual. Energy closure alone therefore cannot prove time resolution.
    if pulse.peak_current_a and resolved_pulse_intervals < 32.0:
        violations.append("pulse_resolution")
    # Sampling alone can miss a voltage peak. With x in [0,1] on the pulse,
    # R*i + L*di/dt = -A + A*cos(2*pi*x) - B*sin(2*pi*x).
    # Its magnitude is bounded by A + hypot(A,B), independently of the grid.
    # Add the global PM back-EMF bound. This is deliberately conservative:
    # rejection can mean the envelope is too loose, not actual infeasibility.
    a_v = motor.resistance_ohm * pulse.peak_current_a / 2.0
    b_v = motor.inductance_h * pulse.peak_current_a * math.pi * n * omega / pulse.width_phase_rad
    emf_bound_v = motor.pm_flux_linkage_amplitude_wb_turn * n * omega
    voltage_bound = a_v + math.hypot(a_v, b_v) + emf_bound_v
    # Command amplitude is analytic; this avoids accepting an overcurrent pulse
    # whose peak happens to lie between samples.
    if pulse.peak_current_a > motor.design_current_cap_a + 1e-12:
        violations.append("current_cap")
    if voltage_bound > motor.bus_voltage_v + 1e-9:
        violations.append("voltage_limit")
    if pulse.gate_duty_fraction > motor.max_gate_duty_fraction + 1e-12:
        violations.append("gate_duty_limit")
    if pulse.peak_current_a and (pulse.start_phase_rad < -1e-12 or pulse.end_phase_rad > math.pi + 1e-12):
        violations.append("outside_trailing_braking_interval")
    cancellation = pulse.peak_current_a / motor.full_cancellation_current_a
    if motor.prohibit_overcancellation and cancellation > 1.0 + 1e-12:
        violations.append("overcancellation")
    if relative_residual > 1e-4:
        violations.append("integration_resolution")

    encounter = {
        "duration_s": period,
        "passive_work_j": passive_work,
        "release_added_work_j": release_work,
        "electromagnetic_work_j": work,
        "signed_terminal_energy_j": terminal,
        "gross_draw_energy_j": draw,
        "returned_terminal_energy_j": returned,
        "copper_loss_j": copper,
        "stored_energy_initial_j": float(stored[0]),
        "stored_energy_final_j": float(stored[-1]),
        "stored_energy_change_j": delta_stored,
        "integrated_port_residual_j": terminal - copper - work - delta_stored,
        "peak_inductive_storage_j": float(np.max(0.5 * motor.inductance_h * current**2)),
    }
    result = CycleResult(
        rpm=rpm,
        peak_current_command_a=pulse.peak_current_a,
        pulse_center_phase_deg=math.degrees(pulse.center_phase_rad),
        pulse_width_phase_deg=math.degrees(pulse.width_phase_rad),
        pulse_width_mechanical_deg=math.degrees(pulse.width_phase_rad) / n,
        pulse_duration_ms=pulse.gate_duty_fraction * period * 1000.0,
        gate_duty_fraction=pulse.gate_duty_fraction,
        encounters_per_coil_per_revolution=n,
        coil_count=motor.coil_count,
        encounters_per_coil_per_second=n * rpm / 60.0,
        total_coil_pulses_per_revolution=factor if pulse.peak_current_a else 0,
        total_coil_pulses_per_second=factor * rpm / 60.0 if pulse.peak_current_a else 0.0,
        peak_abs_voltage_v=peak_voltage,
        voltage_upper_bound_v=voltage_bound,
        peak_abs_current_a=peak_current,
        resolved_pulse_intervals=resolved_pulse_intervals,
        coil_rms_current_a=rms_current,
        cancellation_fraction_peak=cancellation,
        open_circuit_emf_peak_v=float(np.max(np.abs(emf))),
        feasible_command=not violations,
        constraint_violations=violations,
        single_coil_encounter=encounter,
        electromagnetic_work_per_revolution_j=work * factor,
        shaft_work_per_revolution_j=shaft_work,
        shaft_power_w=shaft_work / revolution_s,
        mean_shaft_torque_nm=shaft_work / TAU,
        gross_draw_per_revolution_j=draw * factor,
        returned_terminal_energy_per_revolution_j=returned * factor,
        recovered_bus_energy_per_revolution_j=recovered,
        unrecovered_return_energy_per_revolution_j=unrecovered,
        signed_terminal_energy_per_revolution_j=terminal * factor,
        copper_loss_per_revolution_j=copper * factor,
        controller_energy_per_revolution_j=controller_energy,
        mechanical_loss_per_revolution_j=mechanical_loss,
        stored_energy_change_per_revolution_j=delta_stored * factor,
        net_source_energy_per_revolution_j=source_energy,
        net_source_power_w=source_energy / revolution_s,
        shaft_efficiency=shaft_work / source_energy if source_energy > 1e-12 and shaft_work >= 0 else None,
        energy_residual_per_revolution_j=residual,
        relative_energy_residual=relative_residual,
        max_instantaneous_energy_residual_w_per_coil=float(np.max(np.abs(instantaneous_residual))),
        intervals_per_encounter=intervals,
    )
    if not return_trace:
        return result
    return result, {
        "phase_rad": phase,
        "mechanical_angle_rad": theta,
        "time_s": time,
        "current_a": current,
        "current_derivative_a_per_s": di_dt,
        "voltage_v": voltage,
        "passive_torque_nm": passive_torque,
        "release_torque_nm": release_torque,
        "total_torque_nm": torque,
        "pm_flux_linkage_wb_turn": flux_linkage,
        "stored_energy_j": stored,
        "stored_energy_derivative_w": stored_derivative,
        "terminal_power_w": terminal_power,
        "copper_power_w": copper_power,
        "mechanical_power_w": mechanical_power,
        "energy_residual_w": instantaneous_residual,
    }


def require_feasible(result: CycleResult) -> CycleResult:
    """Reject a waveform before treating it as an available operating point."""
    if not result.feasible_command:
        raise ValueError("Current command did not pass feasibility checks: " + ", ".join(result.constraint_violations))
    return result


def resistance_at_temperature(
    resistance_at_reference_ohm: float,
    temperature_c: float,
    reference_temperature_c: float = 20.0,
    alpha_per_c: float = 0.00393,
) -> float:
    """Illustrative copper linear law, not an APW thermal certification."""
    resistance = resistance_at_reference_ohm * (1.0 + alpha_per_c * (temperature_c - reference_temperature_c))
    if not math.isfinite(resistance) or resistance <= 0:
        raise ValueError("resistance must remain positive")
    return resistance
