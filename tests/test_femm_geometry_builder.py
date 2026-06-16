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
        self.assertIn("rotor_halbach_bias_deg", config)
        self.assertIn("rotor_magnet_leading_edge_bias_deg", config)
        self.assertIn("trailing_edge_barrier_enabled", config)
        self.assertIn("asymmetric_pole_enabled", config)
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

    def test_halbach_bias_changes_magnetization_angles(self):
        config = default_geometry_config()
        config["rotor_halbach_bias_deg"] = 15.0
        lua = render_pm_gradient_motor_lua(config)

        self.assertIn('mi_setblockprop("NdFeB 40 MGOe", 1, 0.000000, "<None>", 15.000000, 2, 0)', lua)
        self.assertIn('mi_setblockprop("NdFeB 40 MGOe", 1, 0.000000, "<None>", 187.500000, 2, 0)', lua)

    def test_trailing_edge_barrier_renders_air_slots(self):
        config = default_geometry_config()
        config["trailing_edge_barrier_enabled"] = True
        lua = render_pm_gradient_motor_lua(config)

        self.assertEqual(lua.count("-- TEB_B trailing-edge air-gap barrier"), 16)
        self.assertIn('mi_setblockprop("Air"', lua)

    def test_asymmetric_pole_replaces_symmetric_magnet_shape(self):
        config = default_geometry_config()
        config["asymmetric_pole_enabled"] = True
        lua = render_pm_gradient_motor_lua(config)

        self.assertEqual(lua.count("-- ASYM_B asymmetric pole"), 16)
        self.assertIn("sloped outer edge", lua)


if __name__ == "__main__":
    unittest.main()
