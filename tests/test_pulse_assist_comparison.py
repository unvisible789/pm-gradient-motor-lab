import csv
import json
import math
import tempfile
import unittest
from pathlib import Path

from validation.analyze_pulse_assist_comparison import (
    delta_metrics, format_metric, load_pulse_curve, summarize_case,
)


class PulseAssistComparisonTests(unittest.TestCase):
    def write_curve(self, directory, angles=range(46), torque=1.0, current_column="coil_current_a"):
        path = Path(directory) / "curve.csv"
        with path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=["angle_deg", "torque_nm", current_column, "active_eml", "pulse_on"])
            writer.writeheader()
            for angle in angles:
                writer.writerow({"angle_deg": angle, "torque_nm": torque, current_column: 10,
                                 "active_eml": 0, "pulse_on": 1})
        return path

    def test_complete_sector_is_not_a_verified_revolution(self):
        with tempfile.TemporaryDirectory() as tmp:
            row = summarize_case("test", self.write_curve(tmp), [{"start_deg": 0, "end_deg": 2}], [])
        self.assertTrue(row["sector_complete"])
        self.assertEqual(row["screen_status"], "complete_sector_unverified")
        self.assertAlmostEqual(row["work_period_j"], math.pi / 4)
        self.assertIsNone(row["full_rev_equiv_j"])
        self.assertIsNone(row["pulse_count_per_rev"])
        self.assertFalse(row["full_state_periodicity_verified"])
        self.assertFalse(row["performance_claim_eligible"])
        self.assertIsNone(row["lockout_peak_negative_nm"])
        json.dumps(row, allow_nan=False)

    def test_incomplete_and_gapped_sectors_withhold_work(self):
        for angles in (range(11), range(1, 46), [0, 45], [x for x in range(46) if x != 20], range(46, 92)):
            with self.subTest(angles=angles), tempfile.TemporaryDirectory() as tmp:
                row = summarize_case("partial", self.write_curve(tmp, angles), [], [])
                self.assertEqual(row["screen_status"], "incomplete_period")
                for key in ("work_period_j", "full_rev_equiv_j", "assist_work_j", "lockout_work_j"):
                    self.assertIsNone(row[key])

    def test_duplicate_reversed_and_nonfinite_samples_are_rejected(self):
        for angles, torque in (([0, 1, 1, 45], 1), ([0, 2, 1, 45], 1),
                              ([0, float("nan")], 1), (range(46), float("inf"))):
            with self.subTest(angles=angles, torque=torque), tempfile.TemporaryDirectory() as tmp:
                path = self.write_curve(tmp, angles, torque)
                with self.assertRaises(ValueError):
                    summarize_case("bad", path, [], [])

    def test_both_current_headers_are_one_turn_surrogates(self):
        for name in ("coil_current_a", "femm_single_turn_current_a"):
            with self.subTest(name=name), tempfile.TemporaryDirectory() as tmp:
                rows = load_pulse_curve(self.write_curve(tmp, current_column=name))
                self.assertEqual(rows[0]["femm_single_turn_current_a"], 10)
                self.assertIsNone(rows[0]["physical_wire_current_a"])

    def test_zero_curve_and_unknown_format_are_json_safe(self):
        with tempfile.TemporaryDirectory() as tmp:
            row = summarize_case("zero", self.write_curve(tmp, torque=0), [], [])
        self.assertIsNone(row["cancellation_ratio"])
        self.assertEqual(format_metric(None), "unknown")
        json.dumps(row, allow_nan=False)

    def test_delta_metrics_compares_only_complete_matching_sectors(self):
        baseline = {"sector_complete": True, "angle_start_deg": 0, "angle_end_deg": 45,
                    "work_period_j": 0.10, "full_rev_equiv_j": 0.80, "assist_work_j": 0.70,
                    "lockout_work_j": -0.60, "peak_positive_nm": 4.0, "peak_negative_nm": -3.0,
                    "cancellation_ratio": 0.90}
        case = {**baseline, "work_period_j": 0.15, "full_rev_equiv_j": 1.20,
                "assist_work_j": 0.80, "lockout_work_j": -0.65, "cancellation_ratio": 0.88}
        delta = delta_metrics(case, baseline)
        self.assertAlmostEqual(delta["added_work_45deg_j"], 0.05)
        self.assertAlmostEqual(delta["assist_work_delta_j"], 0.10)
        self.assertAlmostEqual(delta["lockout_work_delta_j"], -0.05)
        self.assertAlmostEqual(delta["cancellation_delta"], -0.02)
        self.assertIsNone(delta["added_full_rev_j"])
        self.assertIsNone(delta_metrics({**case, "sector_complete": False}, baseline)["added_work_45deg_j"])
        self.assertIsNone(delta_metrics({**case, "angle_end_deg": 44}, baseline)["added_work_45deg_j"])


if __name__ == "__main__":
    unittest.main()
