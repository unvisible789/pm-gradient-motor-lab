import math
import unittest

from validation.passive_cycle_audit import audit_curve


class PassiveCycleAuditTests(unittest.TestCase):
    def test_closed_conservative_curve_has_zero_work(self):
        points = [(a, 4 * math.sin(math.radians(a))) for a in range(361)]
        result = audit_curve(points, 360)
        self.assertAlmostEqual(result["sampled_work_j"], 0, places=12)
        self.assertIsNone(result["validated_shaft_output_j"])

    def test_partial_cycle_is_never_extrapolated(self):
        result = audit_curve([(0, 2), (8, 4), (16.5, -1)], 45)
        self.assertFalse(result["complete_declared_span"])
        self.assertIsNone(result["conditional_full_rev_residual_j"])
        self.assertIsNone(result["full_rev_residual_j"])

    def test_sector_symmetry_is_not_assumed(self):
        result = audit_curve([(0, 1), (45, 1)], 45)
        self.assertIsNone(result["full_rev_residual_j"])
        self.assertAlmostEqual(result["conditional_full_rev_residual_j"], 2 * math.pi)
        self.assertIsNone(result["validated_shaft_output_j"])

    def test_linear_zero_crossing_absolute_area(self):
        result = audit_curve([(0, 1), (180 / math.pi, -1)], 180 / math.pi)
        self.assertAlmostEqual(result["absolute_torque_integral_j"], 0.5)

    def test_invalid_samples_and_periods_rejected(self):
        for points in [[(0, 1)], [(0, 1), (0, 2)], [(2, 1), (1, 2)], [(0, 1), (45, float("nan"))]]:
            with self.subTest(points=points), self.assertRaises(ValueError):
                audit_curve(points, 45)
        with self.assertRaises(ValueError):
            audit_curve([(0, 1), (45, 1)], float("nan"))
        with self.assertRaises(ValueError):
            audit_curve([(0, 1), (44, 1)], 44, symmetry_verified=True)


if __name__ == "__main__":
    unittest.main()
