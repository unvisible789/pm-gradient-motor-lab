import unittest

from validation.pulse_control import (
    PulseElectricalModel,
    build_phase_schedule,
    estimate_revolution_energy,
    merge_windows,
)


class PulseControlTests(unittest.TestCase):
    def test_merge_windows_combines_overlaps_and_small_gaps(self):
        windows = [
            {"start_deg": 2.0, "end_deg": 8.0},
            {"start_deg": 8.4, "end_deg": 13.0},
            {"start_deg": 25.0, "end_deg": 35.0},
        ]

        merged = merge_windows(windows, min_gap_deg=0.5)

        self.assertEqual(
            merged,
            [
                {"start_deg": 2.0, "end_deg": 13.0},
                {"start_deg": 25.0, "end_deg": 35.0},
            ],
        )

    def test_build_phase_schedule_repeats_windows_for_each_45_degree_period(self):
        schedule = build_phase_schedule(
            [{"start_deg": 2.0, "end_deg": 13.0}],
            period_deg=45.0,
            periods_per_rev=8,
            advance_deg=1.0,
        )

        self.assertEqual(len(schedule), 8)
        self.assertEqual(schedule[0], {"start_deg": 1.0, "end_deg": 12.0})
        self.assertEqual(schedule[1], {"start_deg": 46.0, "end_deg": 57.0})
        self.assertEqual(schedule[-1], {"start_deg": 316.0, "end_deg": 327.0})

    def test_build_phase_schedule_wraps_negative_advance_at_revolution_boundary(self):
        schedule = build_phase_schedule(
            [{"start_deg": 0.0, "end_deg": 2.0}],
            period_deg=45.0,
            periods_per_rev=8,
            advance_deg=1.0,
        )

        self.assertIn({"start_deg": 359.0, "end_deg": 360.0}, schedule)
        self.assertIn({"start_deg": 0.0, "end_deg": 1.0}, schedule)

    def test_estimate_revolution_energy_accounts_for_unrecovered_pulse_input(self):
        model = PulseElectricalModel(
            coil_inductance_mh=5.0,
            pulse_current_a=2.0,
            recovery_efficiency=0.75,
            eml_count=8,
            pulses_per_eml_per_rev=8,
        )

        result = estimate_revolution_energy(
            mechanical_work_j_per_rev=1.486,
            electrical_model=model,
        )

        self.assertAlmostEqual(result["stored_j_per_pulse"], 0.01)
        self.assertAlmostEqual(result["unrecovered_j_per_pulse"], 0.0025)
        self.assertAlmostEqual(result["input_j_per_rev"], 0.16)
        self.assertAlmostEqual(result["net_after_input_j_per_rev"], 1.326)


if __name__ == "__main__":
    unittest.main()
