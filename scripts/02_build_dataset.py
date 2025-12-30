#!/usr/bin/env python3
"""
02_build_dataset.py

Goal
----
Build the modeling dataset by aligning equity returns with rate changes.

Inputs (expected)
-----------------
data/raw/rates.csv or data/raw/rates.parquet
data/raw/equity.csv or data/raw/equity.parquet

Expected minimal columns
------------------------
Rates file:  must contain a date column and at least one numeric rate series
Equity file: must contain a date column and at least one numeric price/return series

This script is intentionally robust:
- It searches for common date column names (date, DATE, Date).
- It allows multiple numeric columns and keeps them all.
- If raw files are missing, it exits with clear instructions.

Outputs
-------
data/processed/dataset.parquet
data/processed/dataset.csv     (optional, for easy inspection)
"""

from __future__ import annotations

from pathlib import Path
import sys

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"


def _find_file(stem: str) -> Path | None:
    """Find data/raw/<stem>.csv or .parquet"""
    for ext in (".parquet", ".csv"):
        p = RAW_DIR / f"{stem}{ext}"
        if p.exists() and p.is_file():
            return p
    return None


def _read_any(path: Path) -> pd.DataFrame:
    if path.suffix.lower() == ".parquet":
        return pd.read_parquet(path)
    if path.suffix.lower() == ".csv":
        return pd.read_csv(path)
    raise ValueError(f"Unsupported file type: {path.suffix}")


def _infer_date_col(df: pd.DataFrame) -> str:
    candidates = ["date", "Date", "DATE", "datetime", "Datetime", "DATETIME"]
    for c in candidates:
        if c in df.columns:
            return c
    # fallback: if first column looks like date
    return df.columns[0]


def _standardize_date_index(df: pd.DataFrame, name: str) -> pd.DataFrame:
    date_col = _infer_date_col(df)
    out = df.copy()
    out[date_col] = pd.to_datetime(out[date_col], errors="coerce")
    out = out.dropna(subset=[date_col]).sort_values(date_col)
    out = out.set_index(date_col)
    out.index.name = name
    return out


def _keep_numeric(df: pd.DataFrame) -> pd.DataFrame:
    numeric = df.select_dtypes(include="number")
    if numeric.shape[1] == 0:
        raise ValueError("No numeric columns found. Provide at least one numeric series.")
    return numeric


def main() -> None:
    print("[02] Build aligned modeling dataset")
    print(f"     Project root: {PROJECT_ROOT}")

    rates_path = _find_file("rates")
    equity_path = _find_file("equity")

    if rates_path is None or equity_path is None:
        print("     Missing required raw files in data/raw/.")
        print("     Expected one of each:")
        print("       - data/raw/rates.csv or data/raw/rates.parquet")
        print("       - data/raw/equity.csv or data/raw/equity.parquet")
        print("\n     How to fix:")
        print("       1) Put your existing raw files into data/raw/ with names rates.* and equity.*")
        print("       2) Or rerun Step 01 with env vars pointing to your files, e.g.:")
        print("          RATES_SOURCE_PATH=/path/rates.csv EQUITY_SOURCE_PATH=/path/equity.csv python scripts/01_fetch_data.py")
        sys.exit(0)

    print(f"     Reading rates:  {rates_path.relative_to(PROJECT_ROOT)}")
    print(f"     Reading equity: {equity_path.relative_to(PROJECT_ROOT)}")

    rates = _read_any(rates_path)
    equity = _read_any(equity_path)

    rates = _standardize_date_index(rates, name="date")
    equity = _standardize_date_index(equity, name="date")

    rates = _keep_numeric(rates).add_prefix("rate_")
    equity = _keep_numeric(equity).add_prefix("eq_")

    # Changes (simple first differences) for rates; returns for equity can be prices or returns.
    # If equity data are prices, users can compute returns later in 03_run_analysis.py.
    rate_changes = rates.diff().add_prefix("d_")

    dataset = pd.concat([equity, rates, rate_changes], axis=1, join="inner").dropna()

    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    out_parquet = PROCESSED_DIR / "dataset.parquet"
    out_csv = PROCESSED_DIR / "dataset.csv"

    dataset.to_parquet(out_parquet)
    dataset.to_csv(out_csv)

    print(f"     Saved: {out_parquet.relative_to(PROJECT_ROOT)}")
    print(f"     Saved: {out_csv.relative_to(PROJECT_ROOT)}")
    print("[02] Done.")
    print("Next step:")
    print("  - Run: python scripts/03_run_analysis.py")


if __name__ == "__main__":
    main()
