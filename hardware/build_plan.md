# Hardware Build Plan - PM Gradient Motor Lab

**Status**: Early validation stage. Focus is on lowest-cost fixture to validate FEMM torque-angle results before any full motor construction.

## Strategy Overview

We are **not** building the full 16-gradient / 8-EML motor yet.

**Phase 0 (Current)**: Passive torque-angle fixture (manual stepping)
- Validate FEMM torque-angle curve shape and net work over one 45° repeat period.

**Phase 1**: Circuit validation on dummy inductive load
- Test driver + energy recovery on representative coil before connecting to real EML.

**Phase 2**: Powered single-EML fixture test (conditional)
- Only after passive fixture data matches FEMM within defined tolerance.

**Phase 3**: Full motor prototype
- Only after Phase 0 + Phase 2 data justify the investment.

## Decision Gate
Full motor construction is **NOT READY**. The single-period bench fixture is the correct next step.

## Success Criteria for Phase 0 Fixture
- Measured torque-angle curve shape matches FEMM trend.
- Integrated work over 45° is measured and reported.
- At least 5 repeatable manual sweeps.
- Measurement uncertainty is quantified and reported.
- If measured data does not match FEMM, stop and revise model before proceeding.