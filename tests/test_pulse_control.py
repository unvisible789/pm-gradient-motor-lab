import unittest

from validation.pulse_control import (
    PulseElectricalModel,
    active_eml_index,
    ampere_turns_from_density_ma_per_mm2,
    count_selected_pulses,
    angle_in_windows,
    build_phase_schedule,
    current_from_density_ma_per_mm2,
    eml_coil_area_mm2,
    estimate_revolution_energy,
    merge_windows,
    pulse_current_levels_for_geometry,
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

    def test_magnetic_storage_does_not_establish_source_input(self):
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
        self.assertAlmostEqual(result["illustrative_unrecovered_magnetic_energy_j_per_rev"], 0.16)
        self.assertIsNone(result["input_j_per_rev"])
        self.assertIsNone(result["net_after_input_j_per_rev"])
        self.assertFalse(result["performance_claim_eligible"])

    def test_angle_in_windows_and_active_eml_index(self):
        windows = [
            {"start_deg": 0.0, "end_deg": 2.0},
            {"start_deg": 14.0, "end_deg": 25.0},
        ]
        self.assertTrue(angle_in_windows(1.0, windows))
        self.assertFalse(angle_in_windows(10.0, windows))
        self.assertEqual(active_eml_index(1.0, eml_count=8, eml_offset_deg=12.0), 0)

    def test_pulse_current_levels_for_gap159_geometry(self):
        levels = pulse_current_levels_for_geometry(
            {
                "stator_inner_radius_mm": 159.0,
                "stator_outer_radius_mm": 205.0,
                "eml_arc_deg": 14.0,
                "coil_turns": 100,
            }
        )
        self.assertGreater(levels["high"], levels["medium"])
        self.assertGreater(levels["medium"], levels["low"])
        area = eml_coil_area_mm2(
            stator_inner_radius_mm=159.0,
            stator_outer_radius_mm=205.0,
            eml_arc_deg=14.0,
        )
        self.assertAlmostEqual(
            current_from_density_ma_per_mm2(10.0, area, turns=100),
            levels["medium"],
            places=6,
        )

    def test_density_area_is_ampere_turns_and_requires_turns_for_current(self):
        self.assertEqual(ampere_turns_from_density_ma_per_mm2(10.0, 1000.0), 10.0)
        self.assertEqual(current_from_density_ma_per_mm2(10.0, 1000.0, turns=100), 0.1)
        with self.assertRaises(TypeError):
            current_from_density_ma_per_mm2(10.0, 1000.0)
        for turns in (0, -1, 1.5, True):
            with self.subTest(turns=turns), self.assertRaises(ValueError):
                current_from_density_ma_per_mm2(10.0, 1000.0, turns=turns)
        with self.assertRaises(ValueError):
            pulse_current_levels_for_geometry({"stator_inner_radius_mm": 159.0,
                                               "stator_outer_radius_mm": 205.0, "eml_arc_deg": 14.0})

    def test_event_count_is_gradient_encounters_not_sampled_angles(self):
        self.assertEqual(count_selected_pulses(rotor_gradient_count=16, eml_count=8), 128)
        self.assertEqual(count_selected_pulses(rotor_gradient_count=16, eml_count=2,
                                               selected_events_per_eml=[[0, 3], [1]]), 3)
        with self.assertRaises(ValueError):
            count_selected_pulses(rotor_gradient_count=16, eml_count=1,
                                  selected_events_per_eml=[[1, 1]])

    def test_storage_illustration_rejects_fractional_pulse_events(self):
        with self.assertRaises(ValueError):
            estimate_revolution_energy(mechanical_work_j_per_rev=1.0,
                                       electrical_model=PulseElectricalModel(5.0, 2.0, 0.75, 8, 4.5))


if __name__ == "__main__":
    unittest.main()
