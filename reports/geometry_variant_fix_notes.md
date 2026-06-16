# Geometry Variant Fix Notes

**Date:** 2026-06-15

## opt_stator_shunt_center / opt_stator_shunt_leading

**Failure:** FEMM `mi_analyze` — material not defined for all regions.

**Cause:** Shunt arc was placed outside the stator yoke (`inner_radius_mm=205`, `outer_radius_mm=225` while `stator_outer_radius_mm=205`), creating unlabeled/overlapping regions.

**Fix attempted:** Default shunt radii changed to 190–204 mm in `femm_geometry_builder.py`. Variant JSON files still carry old 205–225 values until regenerated. Re-test still failed because merged variant JSON overrides defaults.

**Status:** Needs variant JSON update before re-run. Not promoted; gap sweep took priority.

## opt_eml_asym_mild / opt_eml_asym_moderate

**Failure:** Incomplete FEMM sweep (header-only CSV) during prior matrix run.

**Likely cause:** Asymmetric EML pole polygon may create invalid regions or the sweep was interrupted after prepare errors before config-merge fix.

**Status:** Deferred. Gap 159.0 combinations did not justify further EML pole-shoe work in this pass.