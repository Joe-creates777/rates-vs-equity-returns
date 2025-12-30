#!/usr/bin/env python3
"""
03_run_analysis.py

Goal
----
Run a minimal, reproducible baseline analysis:
- choose one equity series and one rate-change series
- compute equity returns if needed
- estimate OLS: equity_return ~ rate_change
- save a summary table and a key figure

Inputs
------
data/processed/dataset.parquet (preferred) or data/processed/dataset.csv

Outputs
-------
reports/tables/baseline_regression.txt
reports/figures/baseline_scatter.png
"""

from __future__ import annotations

from pathlib import Path
import sys

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import statsmodels.api as sm


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
REPORTS_FIG_DIR = PROJECT_ROOT / "reports" / "figures"
REPORTS_TAB_DIR = PROJECT_ROOT / "reports" / "tables"


def _load_dataset() -> pd.DataFrame | None:
    p_parquet = PROCESSED_DIR / "dataset.parquet"
    p_csv = PROCESSED_DIR / "dataset.csv"
    if p_parquet.exists():
        return pd.read_parquet(p_parquet)
    if p_csv.exists():
        return pd.read_csv(p_csv, index_col=0, parse_dates=True)
    return None


def _pick_first(cols: list[str], prefix: str) -> str:
    for c in cols:
        if c.startswith(prefix):
            return c
    raise ValueError(f"No columns found with prefix {prefix}")


def _ensure_returns(series: pd.Series) -> pd.Series:
    """
    If series looks like price levels, compute log returns.
    Heuristic:
      - if values mostly > 5 and std relatively small => likely prices/index level
      - otherwise assume already returns
    """
    s = series.dropna().astype(float)
    if len(s) < 10:
        return s

    # Heuristic: price series often positive and larger magnitude
    if (s > 0).mean() > 0.95 and s.median() > 5:
        # compute log returns
        r = np.log(s).diff()
        return r
    return s


def main() -> None:
    print("[03] Run baseline analysis")
    print(f"     Project root: {PROJECT_ROOT}")

    df = _load_dataset()
    if df is None or df.empty:
        print("     Missing processed dataset.")
        print("     Expected: data/processed/dataset.parquet (or dataset.csv)")
        print("     Please run: python scripts/02_build_dataset.py")
        sys.exit(0)

    # Ensure index is datetime if possible
    if not isinstance(df.index, pd.DatetimeIndex):
        try:
            df.index = pd.to_datetime(df.index)
        except Exception:
            pass

    cols = list(df.columns)

    eq_col = _pick_first(cols, "eq_")
    # Prefer first difference rate change columns created by 02: prefix "d_rate_"
    d_rate_col = None
    for c in cols:
        if c.startswith("d_rate_"):
            d_rate_col = c
            break
    if d_rate_col is None:
        # fallback: try raw rates
        d_rate_col = _pick_first(cols, "rate_")

    y_raw = df[eq_col]
    x_raw = df[d_rate_col]

    y = _ensure_returns(y_raw)
    x = x_raw.astype(float)

    # Align and drop missing
    aligned = pd.concat([y.rename("y"), x.rename("x")], axis=1).dropna()
    if aligned.shape[0] < 30:
        print("     Not enough aligned observations to run regression (need >= 30).")
        print(f"     Got: {aligned.shape[0]}")
        sys.exit(0)

    # OLS with intercept
    X = sm.add_constant(aligned["x"])
    model = sm.OLS(aligned["y"], X).fit()

    REPORTS_FIG_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS_TAB_DIR.mkdir(parents=True, exist_ok=True)

    # Save regression text
    out_txt = REPORTS_TAB_DIR / "baseline_regression.txt"
    out_txt.write_text(model.summary().as_text())

    print(f"     Saved: {out_txt.relative_to(PROJECT_ROOT)}")

    # Plot scatter + fitted line (minimal, no custom colors)
    fig_path = REPORTS_FIG_DIR / "baseline_scatter.png"
    plt.figure()
    plt.scatter(aligned["x"], aligned["y"], s=10)

    # Fitted line
    x_line = np.linspace(aligned["x"].min(), aligned["x"].max(), 100)
    y_line = model.params["const"] + model.params["x"] * x_line
    plt.plot(x_line, y_line)

    plt.xlabel(d_rate_col)
    plt.ylabel(f"{eq_col} (returns if price-like)")
    plt.title("Baseline: Equity vs Rate Change")
    plt.tight_layout()
    plt.savefig(fig_path, dpi=150)
    plt.close()

    print(f"     Saved: {fig_path.relative_to(PROJECT_ROOT)}")

    print("[03] Done.")
    print("Next step:")
    print("  - Run: python scripts/04_make_report.py")


if __name__ == "__main__":
    main()
