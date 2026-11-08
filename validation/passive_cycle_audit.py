"""Audit passive torque CSVs without treating numerical residuals as motor output.

Raw curves are never shifted, zeroed, rescaled to conceal missing samples, or
declared energy sources. A sector-to-revolution number is a conditional diagnostic
unless the complete magnetic state really repeats after that sector.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STUDIES = [
    ("original full turn", "femm_torque_angle.csv", 360.0),
    ("original shaped poles", "femm_torque_angle_arc10_offset0_period45_step1.csv", 45.0),
    ("mesh coarse", "femm_verify_mesh_coarse_step1.csv", 45.0),
    ("mesh medium", "femm_verify_mesh_medium_step1.csv", 45.0),
    ("mesh fine", "femm_verify_mesh_fine_step1.csv", 45.0),
    ("mesh very fine", "femm_verify_mesh_veryfine_step1.csv", 45.0),
    ("angle 0.25 degrees", "femm_verify_angle_step0p25.csv", 45.0),
    ("later coil-off baseline", "femm_pulse_gap159_coiloff_period45_step1.csv", 45.0),
]


def audit_curve(points, expected_span_deg: float, *, symmetry_verified: bool = False):
    if not math.isfinite(expected_span_deg) or not 0 < expected_span_deg <= 360:
        raise ValueError("Expected span must be finite and in (0, 360] degrees")
    if symmetry_verified and not math.isclose(360 / expected_span_deg, round(360 / expected_span_deg), abs_tol=1e-9):
        raise ValueError("A declared repeat period must divide one revolution")
    curve = [(float(a), float(t)) for a, t in points]
    if len(curve) < 2 or not all(math.isfinite(v) for pair in curve for v in pair):
        raise ValueError("At least two finite angle/torque samples are required")
    if any(b[0] <= a[0] for a, b in zip(curve, curve[1:])):
        raise ValueError("Angles must be strictly increasing; do not silently sort a cycle")
    work = absolute_work = 0.0
    for (aa, ta), (ab, tb) in zip(curve, curve[1:]):
        width = math.radians(ab - aa)
        work += 0.5 * (ta + tb) * width
        if ta * tb < 0:
            absolute_work += 0.5 * (ta * ta + tb * tb) / (abs(ta) + abs(tb)) * width
        else:
            absolute_work += 0.5 * (abs(ta) + abs(tb)) * width
    span = curve[-1][0] - curve[0][0]
    complete = math.isclose(span, expected_span_deg, rel_tol=0, abs_tol=1e-8)
    multiplier = 360 / expected_span_deg
    repeatable = complete and (math.isclose(expected_span_deg, 360) or symmetry_verified)
    return {
        "sample_count": len(curve),
        "angle_start_deg": curve[0][0],
        "angle_end_deg": curve[-1][0],
        "angle_span_deg": span,
        "expected_span_deg": expected_span_deg,
        "complete_declared_span": complete,
        "sector_symmetry_verified": symmetry_verified,
        "sampled_work_j": work,
        "absolute_torque_integral_j": absolute_work,
        "relative_integral_residual": abs(work) / absolute_work if absolute_work else 0.0,
        "endpoint_torque_difference_nm": curve[-1][1] - curve[0][1],
        "conditional_full_rev_residual_j": work * multiplier if complete else None,
        "full_rev_residual_j": work * multiplier if repeatable else None,
        "status": "PASSIVE_RESIDUAL_REQUIRES_VALIDATION" if complete else "INCOMPLETE_SPAN_DO_NOT_EXTRAPOLATE",
        "validated_shaft_output_j": None,
        "note": "A passive restored-state cycle has zero ideal net work. Nonzero values are residuals to investigate, not available output.",
    }


def audit_file(path: Path, expected_span_deg: float, **kwargs):
    with path.open(newline="", encoding="utf-8-sig") as stream:
        rows = list(csv.DictReader(stream))
    if not rows or not {"angle_deg", "torque_nm"}.issubset(rows[0]):
        raise ValueError("CSV must contain angle_deg and torque_nm")
    return audit_curve([(r["angle_deg"], r["torque_nm"]) for r in rows], expected_span_deg, **kwargs)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json-out", type=Path, default=ROOT / "reports/passive_cycle_audit.json")
    parser.add_argument("--md-out", type=Path, default=ROOT / "reports/passive_cycle_audit.md")
    args = parser.parse_args()
    results = []
    for label, name, span in STUDIES:
        path = ROOT / "data/field_sim" / name
        result = audit_file(path, span)
        results.append({"label": label, "source": path.relative_to(ROOT).as_posix(), **result})
    payload = {
        "audit_date": "2026-11-08",
        "source_status": "Reanalysis of existing CSVs; no new FEMM solve or hardware measurement",
        "model_validation_status": "not_validated",
        "results": results,
    }
    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    args.json_out.write_text(json.dumps(payload, indent=2, allow_nan=False) + "\n")
    lines = [
        "# Passive cycle audit", "", "Date: 2026-11-08", "",
        "This is a new calculation on the existing CSV files, not a new field solve or a bench test. Raw data are unchanged.", "",
        "## Results", "",
        "The last numeric column conditionally repeats a **complete** declared sector through 360 degrees. Sector symmetry and identical geometry/solver provenance are not independently established by these CSVs. These are residuals, not predicted shaft output.", "",
        "| Stored run | Points | Recorded / declared span | Sampled work (J) | Conditional full-turn residual (J) | Status |",
        "|---|---:|---:|---:|---:|---|",
    ]
    for r in results:
        equiv = r["conditional_full_rev_residual_j"]
        value = "not computed" if equiv is None else f"{equiv:.8f}"
        status = "complete; diagnostic only" if r["complete_declared_span"] else "incomplete; cannot extrapolate"
        lines.append(f"| {r['label']} | {r['sample_count']} | {r['angle_span_deg']:g} / {r['expected_span_deg']:g} deg | {r['sampled_work_j']:.8f} | {value} | {status} |")
    lines += ["", "## Engineering interpretation", "",
        "The mesh-labelled series is much closer to zero than the earlier +1.396 J/rev figure and changes sign. It does not establish a positive passive energy source. Because full run provenance is absent, this is not a certified convergence study and no statistical uncertainty is inferred by pooling unlike runs.", "",
        "The 0.25-degree file ends at 16.5 degrees. Extrapolating this partial record to a full revolution would manufacture an apparent result. The audit explicitly withholds that number.", "",
        "Before optimizing the machine or making a net-power claim, validate the passive model against its zero closed-cycle work requirement, torque-angle measurements, mesh/boundary refinement, and a full-state periodicity check. Do not subtract the mean torque and call that a corrected physical model.", "",
        "## Reproduce", "", "```sh", "python validation/passive_cycle_audit.py", "```", "",
        "## Basis", "",
        "- [MIT electromechanical energy balance](https://ocw.mit.edu/courses/6-061-introduction-to-electric-power-systems-spring-2011/c26f6204e05bd4c47875a96452982b6f_MIT6_061S11_ch8.pdf)",
        "- [FEMM force and torque accuracy guidance](https://femm.info/doku/doku.php?id=faq)", "",
    ]
    args.md_out.parent.mkdir(parents=True, exist_ok=True)
    args.md_out.write_text("\n".join(lines))
    print(json.dumps({"report": str(args.md_out), "runs": len(results), "incomplete": sum(not r["complete_declared_span"] for r in results)}))


if __name__ == "__main__":
    main()
