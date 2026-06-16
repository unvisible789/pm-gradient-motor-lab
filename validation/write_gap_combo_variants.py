"""Limited combinations on gap 159.0 mm optimum."""

from __future__ import annotations

import json
import sys
from copy import deepcopy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

VARIANT_DIR = ROOT / "field_sim" / "femm" / "variants"


def gap159_base() -> dict:
    return json.loads((VARIANT_DIR / "gap_159p0.json").read_text(encoding="utf-8"))


def write(name: str, purpose: str, overrides: dict) -> None:
    cfg = deepcopy(gap159_base())
    cfg.update(overrides)
    cfg["variant_name"] = name
    cfg["variant_purpose"] = purpose
    (VARIANT_DIR / f"{name}.json").write_text(json.dumps(cfg, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    write(
        "combo_gap159_arc20",
        "Gap 159 mm + EML arc -20% (11.2 deg).",
        {"eml_arc_deg": 11.2},
    )
    write(
        "combo_gap159_arc10",
        "Gap 159 mm + EML arc -10% (12.6 deg).",
        {"eml_arc_deg": 12.6},
    )
    write(
        "combo_gap159_halbach15",
        "Gap 159 mm + mild rotor partial-Halbach bias 15 deg.",
        {"rotor_halbach_bias_deg": 15.0},
    )
    print("Wrote 3 gap combination variants")


if __name__ == "__main__":
    main()