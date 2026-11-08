"""Compatibility command for the corrected passive-cycle audit.

The previous reporter extrapolated arbitrary recorded spans and pooled unlike
runs into an unsupported uncertainty estimate. Use the coverage-aware audit.
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from validation.passive_cycle_audit import main

if __name__ == "__main__":
    main()
