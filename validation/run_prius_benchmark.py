from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from validation.validation_core import compare_motor_benchmark, load_numeric_csv


REFERENCE = ROOT / "data" / "published" / "ornl_2010_prius_mg2_reference.csv"
SIMULATION = ROOT / "data" / "published" / "prius_consistency_simulation.csv"
REPORT = ROOT / "reports" / "prius_benchmark_validation_report.md"


def main() -> None:
    reference = load_numeric_csv(REFERENCE)[0]
    simulation = load_numeric_csv(SIMULATION)[0]
    comparison = compare_motor_benchmark(simulation, reference, tolerance_pct=5.0)

    lines = [
        "# Prius Benchmark Validation Report",
        "",
        "Benchmark motor: 2010 Toyota Prius MG2 permanent-magnet synchronous motor.",
        "",
        "Source: ORNL/TM-2010/253, Oak Ridge National Laboratory, March 2011.",
        "",
        f"Overall status: **{comparison['overall_status']}**",
        "",
        "| Metric | Simulation | Published reference | Error (%) | Status |",
        "|---|---:|---:|---:|---|",
    ]
    for metric, result in comparison["metrics"].items():
        lines.append(
            "| "
            f"{metric} | "
            f"{result['simulated']:.3f} | "
            f"{result['reference']:.3f} | "
            f"{result['error_pct']:.3f} | "
            f"{result['status']} |"
        )

    lines.extend(
        [
            "",
            "Interpretation:",
            "",
            "This is a benchmark consistency check, not a proof of the PM-gradient",
            "concept. It confirms the validation tools can compare a simulated motor",
            "envelope against a real published PMSM benchmark before applying the same",
            "workflow to prototype measurements.",
            "",
            "Next steps:",
            "",
            "- Digitize or measure torque-angle curves.",
            "- Add field-simulation torque-angle exports.",
            "- Add real bench waveform captures.",
        ]
    )
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {REPORT.relative_to(ROOT)}")
    print(f"Overall status: {comparison['overall_status']}")


if __name__ == "__main__":
    main()
