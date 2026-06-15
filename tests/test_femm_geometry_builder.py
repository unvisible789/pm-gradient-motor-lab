import unittest

from validation.femm_geometry_builder import (
    default_geometry_config,
    render_pm_gradient_motor_lua,
    validate_geometry_config,
)


class FemmGeometryBuilderTests(unittest.TestCase):
    def test_default_config_matches_described_motor_layout(self):
        config = default_geometry_config()

        self.assertEqual(config["rotor_diameter_mm"], 300.0)
        self.assertEqual(config["rotor_gradient_count"], 16)
        self.assertEqual(config["eml_unit_count"], 8)
        self.assertEqual(config["design_variant"], "anti_cancellation_v1")
        self.assertEqual(config["rotor_group"], 2)
        self.assertEqual(config["stator_group"], 1)

    def test_rendered_lua_builds_sixteen_rotor_magnets_and_eight_emls(self):
        lua = render_pm_gradient_motor_lua(default_geometry_config())

        self.assertIn("newdocument(0)", lua)
        self.assertIn('mi_saveas("geometry/pm_gradient_motor_base.fem")', lua)
        self.assertEqual(lua.count("concentrated main pole"), 16)
        self.assertEqual(lua.count("forward-biased outer pole cap"), 0)
        self.assertEqual(lua.count("-- Rotor flux barrier"), 0)
        self.assertEqual(lua.count("-- EML stator unit"), 8)
        self.assertEqual(lua.count("-- EML flux relief"), 0)
        self.assertIn('mi_setblockprop("NdFeB 40 MGOe"', lua)
        self.assertIn('mi_setblockprop("Copper"', lua)
        self.assertIn('mi_setblockprop("Air"', lua)
        self.assertIn("rotor_group = 2", lua)

    def test_rejects_non_2_to_1_gradient_to_eml_ratio(self):
        config = default_geometry_config()
        config["rotor_gradient_count"] = 15

        with self.assertRaisesRegex(ValueError, "2:1"):
            validate_geometry_config(config)

    def test_allows_six_eml_candidate_for_optimizer(self):
        config = default_geometry_config()
        config["eml_unit_count"] = 6

        validate_geometry_config(config)


if __name__ == "__main__":
    unittest.main()
