import tempfile
import unittest
from pathlib import Path

from validation.femm_workflow import (
    default_femm_config,
    render_femm_lua,
    summarize_torque_angle_csv,
    write_femm_workflow,
)


class FemmWorkflowTests(unittest.TestCase):
    def test_rendered_lua_sweeps_rotor_group_and_exports_torque_csv(self):
        config = default_femm_config()
        config["base_fem_file"] = "geometry/pm_gradient_motor_base.fem"
        config["output_csv"] = "data/field_sim/femm_torque_angle.csv"
        config["rotor_group"] = 2
        config["angle_step_deg"] = 5

        lua = render_femm_lua(config)

        self.assertIn('open("data/field_sim/femm_torque_angle.csv", "w")', lua)
        self.assertIn("for angle_deg = 0, 360, 5 do", lua)
        self.assertIn("mi_selectgroup(2)", lua)
        self.assertIn("delta_angle = angle_deg - previous_angle", lua)
        self.assertIn("mi_moverotate(0.0, 0.0, delta_angle)", lua)
        self.assertIn("mo_blockintegral(22)", lua)
        self.assertIn('csv:write("angle_deg,torque_nm\\n")', lua)

    def test_workflow_writer_creates_config_and_lua_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_femm_workflow(root)

            self.assertTrue((root / "field_sim" / "femm" / "config.example.json").exists())
            self.assertTrue((root / "field_sim" / "femm" / "sweep_torque_angle.lua").exists())

    def test_summarizes_exported_torque_angle_csv(self):
        with tempfile.TemporaryDirectory() as tmp:
            csv_path = Path(tmp) / "torque_angle.csv"
            csv_path.write_text(
                "angle_deg,torque_nm\n0,1\n180,1\n360,1\n",
                encoding="utf-8",
            )

            result = summarize_torque_angle_csv(csv_path)

        self.assertAlmostEqual(result["work_j_per_rev"], 6.283185, places=6)
        self.assertEqual(result["energy_result"], "NET_POSITIVE_WORK_REQUIRES_SOURCE_ACCOUNTING")


if __name__ == "__main__":
    unittest.main()
