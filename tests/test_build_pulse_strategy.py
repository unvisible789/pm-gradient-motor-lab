import unittest

from validation.build_pulse_strategy import build_strategy_payload


class BuildPulseStrategyTests(unittest.TestCase):
    def test_payload_contains_repeated_schedule_and_energy_budget(self):
        windows = [
            {"start_deg": 2.0, "end_deg": 13.0},
            {"start_deg": 25.0, "end_deg": 35.0},
        ]

        payload = build_strategy_payload(
            label="best_gap_candidate",
            source_csv="data/field_sim/example.csv",
            assist_windows=windows,
            mechanical_work_j_per_rev=1.486,
            advance_deg=1.0,
        )

        self.assertEqual(payload["label"], "best_gap_candidate")
        self.assertEqual(len(payload["pulse_schedule_360deg"]), 16)
        self.assertEqual(payload["pulse_schedule_360deg"][0], {"start_deg": 1.0, "end_deg": 12.0})
        self.assertEqual(payload["electrical_budget"]["input_j_per_rev"], 0.16)
        self.assertEqual(payload["control_rules"][0], "Pulse only inside assist windows.")


if __name__ == "__main__":
    unittest.main()
