import csv
import math
import tempfile
import unittest
from pathlib import Path

from validation.validation_core import (
    audit_bench_run,
    compare_motor_benchmark,
    compare_torque_angle_sources,
    integrate_torque_angle,
    load_numeric_csv,
)


class ValidationCoreTests(unittest.TestCase):
    def test_integrates_closed_torque_angle_curve_in_joules_per_revolution(self):
        rows = [
            {"angle_deg": 0, "torque_nm": 1.0},
            {"angle_deg": 90, "torque_nm": 1.0},
            {"angle_deg": 180, "torque_nm": 1.0},
            {"angle_deg": 270, "torque_nm": 1.0},
            {"angle_deg": 360, "torque_nm": 1.0},
        ]

        result = integrate_torque_angle(rows)

        self.assertAlmostEqual(result["work_j_per_rev"], 2.0 * math.pi, places=6)
        self.assertAlmostEqual(result["average_torque_nm"], 1.0, places=6)

    def test_compares_field_curve_against_bench_curve(self):
        bench = [
            {"angle_deg": 0, "torque_nm": 0.0},
            {"angle_deg": 90, "torque_nm": 1.0},
            {"angle_deg": 180, "torque_nm": 0.0},
        ]
        field = [
            {"angle_deg": 0, "torque_nm": 0.1},
            {"angle_deg": 90, "torque_nm": 0.9},
            {"angle_deg": 180, "torque_nm": -0.1},
        ]

        result = compare_torque_angle_sources(bench, field)

        self.assertAlmostEqual(result["mean_abs_error_nm"], 0.1, places=6)
        self.assertEqual(result["points_compared"], 3)

    def test_audits_bench_run_energy_balance(self):
        rows = [
            {
                "time_s": 0.0,
                "voltage_v": 10.0,
                "current_a": 1.0,
                "torque_nm": 1.0,
                "rpm": 60.0,
            },
            {
                "time_s": 1.0,
                "voltage_v": 10.0,
                "current_a": 1.0,
                "torque_nm": 1.0,
                "rpm": 60.0,
            },
        ]

        result = audit_bench_run(rows)

        self.assertAlmostEqual(result["electrical_input_j"], 10.0, places=6)
        self.assertAlmostEqual(result["mechanical_output_j"], 2.0 * math.pi, places=6)
        self.assertEqual(result["energy_balance_flag"], "BALANCED_BY_MEASURED_INPUT")

    def test_compares_simulated_motor_against_published_prius_reference(self):
        simulated = {
            "motor_name": "2010 Toyota Prius MG2 simulated",
            "peak_power_kw_18s": 59.4,
            "peak_torque_nm": 200.0,
            "max_speed_rpm": 13400.0,
            "peak_efficiency_pct": 96.0,
        }
        reference = {
            "motor_name": "2010 Toyota Prius MG2 ORNL benchmark",
            "peak_power_kw_18s": 60.0,
            "peak_torque_nm": 205.0,
            "max_speed_rpm": 13500.0,
            "peak_efficiency_pct": 96.0,
        }

        result = compare_motor_benchmark(simulated, reference, tolerance_pct=5.0)

        self.assertEqual(result["overall_status"], "PASS")
        self.assertLessEqual(result["metrics"]["peak_torque_nm"]["error_pct"], 5.0)

    def test_load_numeric_csv_converts_numbers(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.csv"
            with path.open("w", newline="", encoding="utf-8") as handle:
                writer = csv.DictWriter(handle, fieldnames=["angle_deg", "torque_nm", "label"])
                writer.writeheader()
                writer.writerow({"angle_deg": "12.5", "torque_nm": "3", "label": "point"})

            rows = load_numeric_csv(path)

        self.assertEqual(rows, [{"angle_deg": 12.5, "torque_nm": 3.0, "label": "point"}])


if __name__ == "__main__":
    unittest.main()
