-- PM Gradient Motor Lab FEMM torque-angle sweep
-- Run inside FEMM: File -> Open Lua Script -> this file.
--
-- Prerequisite:
--   Build or import geometry in the base .fem file and assign the complete
--   rotating assembly to group 2.
--
-- Output:
--   angle_deg,torque_nm CSV for validation/integration.

open("geometry/pm_gradient_motor_base.fem")

csv = assert(io.open("data/field_sim/femm_torque_angle.csv", "w"))
csv:write("angle_deg,torque_nm\n")
csv:flush()

previous_angle = 0
for angle_deg = 0, 360, 2 do
  delta_angle = angle_deg - previous_angle
  if delta_angle ~= 0 then
    mi_seteditmode("group")
    mi_selectgroup(2)
    mi_moverotate(0.0, 0.0, delta_angle)
    mi_clearselected()
  end

  mi_analyze(1)
  mi_loadsolution()
  mo_groupselectblock(2)
  torque_nm = mo_blockintegral(22)
  mo_clearblock()
  csv:write(string.format("%g,%.12g\n", angle_deg, torque_nm))
  csv:flush()
  previous_angle = angle_deg
end

csv:close()
