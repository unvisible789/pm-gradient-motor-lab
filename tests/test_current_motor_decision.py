import unittest

from validation.current_motor_decision import evaluate_current_motor_case


class CurrentMotorDecisionTests(unittest.TestCase):
    def test_flags_baseline_case_as_unbalanced_and_quantifies_gap(self):
        result = evaluate_current_motor_case(
            rpm=800.0,
            gradients_per_revolution=12,
            channels=1,
            net_electrical_energy_per_pulse_j=0.0175,
            load_torque_nm=0.8,
            pulse_assist_torque_nm=1.8,
            pulse_window_deg=2.0,
        )

        self.assertEqual(result["status"], "UNBALANCED_PENDING_SOURCE_IDENTIFICATION")
        self.assertAlmostEqual(result["electrical_input_power_w"], 2.8, places=6)
        self.assertAlmostEqual(result["load_power_w"], 67.020643, places=6)
        self.assertAlmostEqual(result["pulse_work_j"], 0.062832, places=6)
        self.assertAlmostEqual(result["minimum_extra_energy_per_pulse_j"], 0.045332, places=6)
        self.assertAlmostEqual(result["minimum_extra_energy_per_rev_j"], 4.816548, places=6)

    def test_accepts_low_torque_narrow_window_case_as_pulse_balanced(self):
        result = evaluate_current_motor_case(
            rpm=800.0,
            gradients_per_revolution=12,
            channels=1,
            net_electrical_energy_per_pulse_j=0.0175,
            load_torque_nm=0.0,
            pulse_assist_torque_nm=1.0,
            pulse_window_deg=1.0,
        )

        self.assertEqual(result["pulse_balance_flag"], "BALANCED_BY_STATED_PULSE_INPUT")
        self.assertEqual(result["status"], "BALANCED_BY_STATED_INPUT")
        self.assertAlmostEqual(result["minimum_extra_energy_per_pulse_j"], 0.0, places=6)


if __name__ == "__main__":
    unittest.main()
