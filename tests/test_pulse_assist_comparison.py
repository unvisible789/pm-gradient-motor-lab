import csv
import tempfile
import unittest
from pathlib import Path

from validation.analyze_pulse_assist_comparison import delta_metrics, summarize_case


class PulseAssistComparisonTests(unittest.TestCase):
    def test_summarize_case_flags_incomplete_periods(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "partial.csv"
            with path.open("w", newline="", encoding="utf-8") as handle:
                writer = csv.DictWriter(
                    handle,
                    fieldnames=["angle_deg", "torque_nm", "coil_current_a", "active_eml", "pulse_on"],
                )
                writer.writeheader()
                writer.writerow({"angle_deg": 0, "torque_nm": 1, "coil_current_a": 0, "active_eml": 0, "pulse_on": 0})
                writer.writerow({"angle_deg": 10, "torque_nm": 1, "coil_current_a": 0, "active_eml": 0, "pulse_on": 0})

            row = summarize_case("partial", path, [{"start_deg": 0, "end_deg": 2}], [])

            self.assertEqual(row["screen_status"], "incomplete_period")
            self.assertEqual(row["angle_span_deg"], 10.0)

    def test_delta_metrics_compares_added_work_and_lockout_penalty(self):
        baseline = {
            "work_period_j": 0.10,
            "full_rev_equiv_j": 0.80,
            "assist_work_j": 0.70,
            "lockout_work_j": -0.60,
            "peak_positive_nm": 4.0,
            "peak_negative_nm": -3.0,
            "cancellation_ratio": 0.90,
        }
        case = {
            "work_period_j": 0.15,
            "full_rev_equiv_j": 1.20,
            "assist_work_j": 0.80,
            "lockout_work_j": -0.65,
            "peak_positive_nm": 4.5,
            "peak_negative_nm": -3.2,
            "cancellation_ratio": 0.88,
        }

        delta = delta_metrics(case, baseline)

        self.assertAlmostEqual(delta["added_full_rev_j"], 0.40)
        self.assertAlmostEqual(delta["assist_work_delta_j"], 0.10)
        self.assertAlmostEqual(delta["lockout_work_delta_j"], -0.05)
        self.assertAlmostEqual(delta["cancellation_delta"], -0.02)


if __name__ == "__main__":
    unittest.main()
