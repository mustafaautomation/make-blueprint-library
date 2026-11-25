#!/usr/bin/env python3
"""Validate every committed blueprint and catalog.json."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from makebp.validate import validate_catalog  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Structurally validate Make blueprints.")
    parser.add_argument("--min", type=int, default=1, help="Minimum number of scenarios in the catalog.")
    args = parser.parse_args()
    errors = validate_catalog(min_scenarios=args.min)
    if errors:
        print(f"{len(errors)} problem(s):", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print("Blueprints passed structural validation.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
