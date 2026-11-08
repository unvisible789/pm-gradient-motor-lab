import json
import unittest

from validation.account_selective_pulse_energy import account_case, measured_energy_balance


class PulseAccountingTests(unittest.TestCase):
    def test_ordinary_motor_closes_with_input_equal_output_plus_loss(self):
        result = measured_energy_balance(total_input_j=100, output_j=80, losses_j=20,
                                         stored_energy_change_j=0)
        self.assertTrue(result["closes_energy"])
        self.assertEqual(result["balance_residual_j"], 0)
        self.assertEqual(result["efficiency"], 0.8)
        self.assertEqual(result["net_boundary_output_j"], -20)
        self.assertFalse(result["performance_claim_eligible"])

    def test_output_exceeding_input_does_not_mean_closure(self):
        result = measured_energy_balance(total_input_j=100, output_j=120, losses_j=20,
                                         stored_energy_change_j=0)
        self.assertFalse(result["closes_energy"])
        self.assertEqual(result["balance_residual_j"], -40)
        self.assertIsNone(result["efficiency"])

    def test_storage_depletion_can_supply_output_without_a_sustained_claim(self):
        result = measured_energy_balance(total_input_j=100, output_j=120, losses_j=20,
                                         stored_energy_change_j=-40)
        self.assertTrue(result["closes_energy"])
        self.assertIsNone(result["efficiency"])
        self.assertFalse(result["performance_claim_eligible"])

    def test_nonfinite_or_negative_quantities_are_rejected(self):
        for value in (float("nan"), float("inf"), -1):
            with self.subTest(value=value), self.assertRaises(ValueError):
                measured_energy_balance(total_input_j=value, output_j=80, losses_j=20,
                                        stored_energy_change_j=0)

    def test_sector_data_cannot_establish_input_or_net_output(self):
        case = {"sector_complete": True, "angle_start_deg": 0, "angle_end_deg": 45,
                "work_period_j": 0.2, "pulsed_angle_count": 24, "full_rev_equiv_j": 1.6}
        baseline = {**case, "work_period_j": 0.15}
        result = account_case(level="high", case=case, baseline_case=baseline, ampere_turns=15)
        self.assertEqual(result["status"], "insufficient_data")
        self.assertEqual(result["raw_work_45deg_j"], 0.2)
        self.assertAlmostEqual(result["added_raw_work_45deg_j"], 0.05)
        for key in ("total_electrical_input_j_per_rev", "total_input_j_per_rev", "efficiency",
                    "net_output_j_per_rev", "closes_energy", "pulse_count_per_rev",
                    "nominal_wire_current_a", "mechanical_work_j_per_rev"):
            self.assertIsNone(result[key])
        self.assertFalse(result["performance_claim_eligible"])
        json.dumps(result, allow_nan=False)

    def test_incomplete_or_legacy_unvalidated_data_withhold_diagnostics(self):
        for case in (None, {"work_period_j": 0.2, "full_rev_equiv_j": 1.6},
                     {"sector_complete": False, "work_period_j": 0.2},
                     {"sector_complete": True, "work_period_j": float("nan")}):
            with self.subTest(case=case):
                result = account_case(level="low", case=case)
                self.assertIsNone(result["raw_work_45deg_j"])
                self.assertIsNone(result["added_raw_work_45deg_j"])
                self.assertEqual(result["status"], "insufficient_data")


if __name__ == "__main__":
    unittest.main()
