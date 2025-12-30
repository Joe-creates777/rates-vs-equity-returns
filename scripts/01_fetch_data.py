#!/usr/bin/env python3
"""
01_fetch_data.py

Goal
----
Fetch or prepare raw inputs for the project in a reproducible way.

This script is intentionally minimal:
- It creates the expected folder structure under `data/raw/`.
- It copies user-provided local files into `data/raw/` if they exist.
- It prints clear next-step instructions.

Why this design?
- Many research repos start with existing datasets from prior notebooks.
- Keeping this step lightweight avoids premature coupling to any single data source API.

Usage
-----
python scripts/01_fetch_data.py

Optional environment variables (advanced):
- RATES_SOURCE_PATH: path to an existing raw rates file (csv/parquet)
- EQUITY_SOURCE_PATH: path to an existing raw equity file (csv/parquet)

Outputs
-------
data/raw/rates.(csv|parquet)   (if provided)
data/raw/equity.(csv|parquet)  (if provided)
"""

from __future__ import annotations

import os
import shutil
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_RAW_DIR = PROJECT_ROOT / "data" / "raw"


def _ensure_dirs() -> None:
    DATA_RAW_DIR.mkdir(parents=True, exist_ok=True)


def _copy_if_provided(env_var: str, target_stem: str) -> str:
    """
    If env_var points to an existing file, copy it into data/raw/ with a normalized name.
    Supported extensions: .csv, .parquet
    Returns a status message for logging.
    """
    src = os.environ.get(env_var, "").strip()
    if not src:
        return f"- {env_var}: not set (skipped)"

    src_path = Path(src).expanduser().resolve()
    if not src_path.exists() or not src_path.is_file():
        return f"- {env_var}: path not found -> {src_path} (skipped)"

    if src_path.suffix.lower() not in {".csv", ".parquet"}:
        return f"- {env_var}: unsupported file type {src_path.suffix} (use .csv or .parquet) (skipped)"

    dst_path = DATA_RAW_DIR / f"{target_stem}{src_path.suffix.lower()}"
    shutil.copy2(src_path, dst_path)
    return f"- {env_var}: copied -> {dst_path.relative_to(PROJECT_ROOT)}"


def main() -> None:
    print("[01] Fetch data / prepare raw inputs")
    print(f"     Project root: {PROJECT_ROOT}")
    _ensure_dirs()

    print("     Creating/validating: data/raw/")
    rates_msg = _copy_if_provided("RATES_SOURCE_PATH", "rates")
    equity_msg = _copy_if_provided("EQUITY_SOURCE_PATH", "equity")

    print("     Import status:")
    print(rates_msg)
    print(equity_msg)

    print("\n[01] Done.")
    print("Next step:")
    print("  - Run: python scripts/02_build_dataset.py")
    print("Notes:")
    print("  - If you already have raw files from your notebook, you can copy them into data/raw/")
    print("  - Or set env vars, e.g.:")
    print("      RATES_SOURCE_PATH=/path/to/rates.csv EQUITY_SOURCE_PATH=/path/to/equity.csv python scripts/01_fetch_data.py")


if __name__ == "__main__":
    main()
