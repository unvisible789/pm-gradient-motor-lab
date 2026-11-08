"""Physical invariants and implementation checks for the analytic reference."""
import math
import unittest
from dataclasses import replace

import numpy as np

from simulations.release_motor_model import (
    ReferenceMotor, ReleasePulse, require_feasible, resistance_at_temperature,
    simulate_cycle,
)


class ReleaseMotorModelTests(unittest.TestCase):
    def setUp(self):
        self.motor = ReferenceMotor()
        self.pulse = ReleasePulse(0.15, math.pi / 2.0, math.pi * 0.20)

    def test_passive_closed_cycle_has_zero_work(self):
        passive = ReleasePulse(0.0, math.pi / 2.0, math.pi * 0.20)
        motor = replace(self.motor, controller_power_w=0.0)
        result, trace = simulate_cycle(motor, passive, 1000.0, return_trace=True)
        self.assertAlmostEqual(result.shaft_work_per_revolution_j, 0.0, places=12)
        self.assertAlmostEqual(result.net_source_energy_per_revolution_j, 0.0, places=12)
        self.assertGreater(np.max(trace["passive_torque_nm"]), 0)
        self.assertLess(np.min(trace["passive_torque_nm"]), 0)

    def test_positive_release_work_is_paid_by_input(self):
        result, trace = simulate_cycle(self.motor, self.pulse, 1000.0, return_trace=True)
        require_feasible(result)
        self.assertGreater(result.shaft_work_per_revolution_j, 0.0)
        self.assertGreater(result.net_source_energy_per_revolution_j, result.shaft_work_per_revolution_j)
        self.assertLess(result.shaft_efficiency, 1.0)
        self.assertLess(result.relative_energy_residual, 1e-7)
        self.assertLess(result.max_instantaneous_energy_residual_w_per_coil, 1e-12)
        active = trace["current_a"] < -1e-12
        self.assertTrue(np.all(trace["passive_torque_nm"][active] < 0.0))
        self.assertTrue(np.all(trace["release_torque_nm"][active] >= 0.0))
        self.assertTrue(np.all(trace["total_torque_nm"][active] <= 1e-12))

    def test_regeneration_is_counted_once_from_negative_terminal_power(self):
        # Deliberately high inductance and ample bridge voltage make returned
        # energy visible. These are analytic test parameters, not APW claims.
        motor = replace(self.motor, inductance_h=0.10, bus_voltage_v=1000.0)
        ideal = simulate_cycle(replace(motor, return_path_efficiency=1.0), self.pulse, 1000.0)
        lossy = simulate_cycle(replace(motor, return_path_efficiency=0.50), self.pulse, 1000.0)
        self.assertGreater(ideal.returned_terminal_energy_per_revolution_j, 0.0)
        self.assertAlmostEqual(
            ideal.gross_draw_per_revolution_j - ideal.returned_terminal_energy_per_revolution_j,
            ideal.signed_terminal_energy_per_revolution_j,
            places=12,
        )
        self.assertAlmostEqual(
            ideal.net_source_energy_per_revolution_j,
            ideal.signed_terminal_energy_per_revolution_j + ideal.controller_energy_per_revolution_j,
            places=12,
        )
        self.assertAlmostEqual(
            lossy.net_source_energy_per_revolution_j - ideal.net_source_energy_per_revolution_j,
            0.50 * ideal.returned_terminal_energy_per_revolution_j,
            places=12,
        )
        self.assertAlmostEqual(ideal.shaft_work_per_revolution_j, lossy.shaft_work_per_revolution_j, places=12)

    def test_full_state_and_integrated_ports_close(self):
        result, trace = simulate_cycle(self.motor, self.pulse, 1000.0, return_trace=True)
        self.assertAlmostEqual(trace["stored_energy_j"][0], trace["stored_energy_j"][-1], places=12)
        self.assertEqual(trace["current_a"][0], 0.0)
        self.assertEqual(trace["current_a"][-1], 0.0)
        self.assertAlmostEqual(
            result.signed_terminal_energy_per_revolution_j,
            result.electromagnetic_work_per_revolution_j + result.copper_loss_per_revolution_j
            + result.stored_energy_change_per_revolution_j,
            places=6,
        )

    def test_timestep_convergence(self):
        # Off-grid pulse edges exercise the integration, not only symmetry.
        pulse = ReleasePulse(0.13, math.pi * 0.43, math.pi * 0.17)
        coarse = simulate_cycle(self.motor, pulse, 1000.0, intervals=1024)
        fine = simulate_cycle(self.motor, pulse, 1000.0, intervals=4096)
        reference = simulate_cycle(self.motor, pulse, 1000.0, intervals=32768)
        self.assertLess(abs(fine.shaft_work_per_revolution_j-reference.shaft_work_per_revolution_j), 1e-8)
        self.assertLess(abs(fine.net_source_energy_per_revolution_j-reference.net_source_energy_per_revolution_j), 1e-6)
        self.assertLess(abs(fine.shaft_work_per_revolution_j-reference.shaft_work_per_revolution_j),
                        abs(coarse.shaft_work_per_revolution_j-reference.shaft_work_per_revolution_j))

    def test_voltage_limited_current_command_is_rejected(self):
        pulse = ReleasePulse(0.4, math.pi / 2.0, math.pi * 0.20)
        result = simulate_cycle(self.motor, pulse, 1000.0)
        self.assertIn("voltage_limit", result.constraint_violations)
        with self.assertRaisesRegex(ValueError, "voltage_limit"):
            require_feasible(result)

    def test_current_cap_is_checked_against_command_not_sampled_peak(self):
        motor = replace(self.motor, bus_voltage_v=1000.0, prohibit_overcancellation=False)
        result = simulate_cycle(motor, ReleasePulse(0.431, math.pi * 0.431, math.pi * 0.19), 1000.0)
        self.assertIn("current_cap", result.constraint_violations)
        with self.assertRaisesRegex(ValueError, "current_cap"):
            require_feasible(result)

    def test_subgrid_pulse_cannot_disappear_and_pass_feasibility(self):
        pulse = ReleasePulse(0.15, math.pi / 2 + 0.0005, 0.0002)
        result = simulate_cycle(self.motor, pulse, 1000.0)
        self.assertEqual(result.peak_abs_current_a, 0.0)
        self.assertLess(result.resolved_pulse_intervals, 1.0)
        self.assertIn("pulse_resolution", result.constraint_violations)
        self.assertIn("voltage_limit", result.constraint_violations)
        # Check the required voltage at an actual waveform point the grid missed.
        omega = 1000 * 2 * math.pi / 60
        phase = pulse.start_phase_rad + pulse.width_phase_rad / 4
        exact_v = (-self.motor.resistance_ohm * pulse.peak_current_a / 2
                   - self.motor.inductance_h * pulse.peak_current_a * math.pi
                   * self.motor.encounters_per_coil_per_revolution * omega / pulse.width_phase_rad
                   - self.motor.pm_flux_linkage_amplitude_wb_turn
                   * self.motor.encounters_per_coil_per_revolution * omega * math.sin(phase))
        self.assertGreater(abs(exact_v), 19000)
        self.assertGreaterEqual(result.voltage_upper_bound_v, abs(exact_v))
        with self.assertRaises(ValueError):
            require_feasible(result)

    def test_duty_limit_and_nonrelease_timing_are_rejected(self):
        wide = simulate_cycle(self.motor, ReleasePulse(0.10, math.pi / 2.0, math.pi * 0.30), 1000.0)
        wrong_edge = simulate_cycle(self.motor, ReleasePulse(0.10, 1.5*math.pi, math.pi * 0.10), 1000.0)
        self.assertIn("gate_duty_limit", wide.constraint_violations)
        self.assertIn("outside_trailing_braking_interval", wrong_edge.constraint_violations)
        with self.assertRaises(ValueError):
            require_feasible(wide)

    def test_back_emf_limit_also_applies_between_pulses(self):
        result = simulate_cycle(self.motor, ReleasePulse(0.0, math.pi / 2.0, math.pi * 0.10), 3500.0)
        self.assertGreater(result.open_circuit_emf_peak_v, 24.0)
        self.assertIn("voltage_limit", result.constraint_violations)

    def test_encounters_and_system_overhead_scale_correctly(self):
        one = simulate_cycle(replace(self.motor, coil_count=1), self.pulse, 1000.0)
        full = simulate_cycle(self.motor, self.pulse, 1000.0)
        self.assertAlmostEqual(full.encounters_per_coil_per_second, 16.0*1000/60.0)
        self.assertEqual(full.total_coil_pulses_per_revolution, 256)
        self.assertAlmostEqual(full.total_coil_pulses_per_second, 4266.666666666667)
        self.assertAlmostEqual(full.pulse_duration_ms, 0.375)
        self.assertAlmostEqual(full.shaft_work_per_revolution_j, 16.0*one.shaft_work_per_revolution_j)
        self.assertAlmostEqual(full.controller_energy_per_revolution_j, one.controller_energy_per_revolution_j)

    def test_temperature_is_a_sensitivity_not_a_free_parameter(self):
        self.assertAlmostEqual(resistance_at_temperature(55.9, 20), 55.9)
        self.assertGreater(resistance_at_temperature(55.9, 80), 55.9)
        with self.assertRaises(ValueError):
            simulate_cycle(replace(self.motor, resistance_ohm=-1), self.pulse, 1000.0)
        with self.assertRaises(ValueError):
            simulate_cycle(self.motor, self.pulse, 0.0)


if __name__ == "__main__":
    unittest.main()
