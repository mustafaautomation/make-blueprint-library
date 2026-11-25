#!/usr/bin/env python3
"""Generate blueprint folders, catalog.json, and the root README."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from makebp.build import build_all  # noqa: E402
from makebp.specs import SPECS  # noqa: E402


def main() -> int:
    entries = build_all(SPECS)
    print(f"Wrote {len(entries)} scenarios.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
