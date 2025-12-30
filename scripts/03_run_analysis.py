from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import statsmodels.api as sm


# ----------------------------
# Project paths
# ----------------------------
PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_PROC_DIR = PROJECT_ROOT / "data" / "processed"
REPORTS_FIG_DIR = PROJECT_ROOT / "reports" / "figures"
REPORTS_TAB_DIR = PROJECT_ROOT / "reports" / "tables"


# ----------------------------
# Helpers
# ----------------------------
def _load_dataset() -> pd.DataFrame | None:
    """Load processed dataset produced by scripts/02_build_dataset.py."""
    pq = DATA_PROC_DIR / "dataset.parquet"
    csv = DATA_PROC_DIR / "dataset.csv"

    if pq.exists():
        try:
            df = pd.read_parquet(pq)
            return df
        except Exception:
            pass

    if csv.exists():
        try:
            df = pd.read_csv(csv)
            return df
        except Exception:
            pass

    return None


def _pick_first(cols: list[str], prefix: str) -> str | None:
    for c in cols:
        if c.startswith(prefix):
            return c
    return None


def _ensure_returns(series: pd.Series) -> pd.Series:
    """
    If the series looks like a price level, convert to log returns.
    If it already looks like returns, keep it.
    """
    s = pd.to_numeric(series, errors="coerce")

    # Heuristic: if values are all positive and typical magnitude is large, treat as price-like
    s_abs_med = np.nanmedian(np.abs(s.values))
    s_min = np.nanmin(s.values)
    if np.isfinite(s_abs_med) and s_abs_med > 5 and s_min > 0:
        return np.log(s).diff()
    return s


def _find_or_build_vol(df: pd.DataFrame, ret_col: str) -> tuple[pd.Series, str]:
    """
    Try to find a volatility column in df. If not found, build 21-day rolling vol from returns.
    Returns (vol_series, vol_label).
    """
    cols = list(df.columns)

    # Prefer exact / common names first
    preferred = [
        "vol_21", "volatility_21", "rolling_vol_21", "vol21",
        "vol_1m", "rolling_vol", "vol"
    ]
    for name in preferred:
        if name in df.columns:
            return pd.to_numeric(df[name], errors="coerce"), name

    # Otherwise, look for any column that contains "vol" and "21"
    for c in cols:
        cl = c.lower()
        if ("vol" in cl) and ("21" in cl):
            return pd.to_numeric(df[c], errors="coerce"), c

    # Fallback: compute from returns
    r = pd.to_numeric(df[ret_col], errors="coerce")
    vol = r.rolling(21).std()
    return vol, "vol_21 (computed)"


def _maybe_set_datetime_index(df: pd.DataFrame) -> pd.DataFrame:
    """
    If df has a date-like index/column, try to set a DatetimeIndex for prettier downstream ops.
    Safe to fail.
    """
    if isinstance(df.index, pd.DatetimeIndex):
        return df

    # common date column names
    for dc in ["date", "Date", "DATE", "dt", "timestamp", "time"]:
        if dc in df.columns:
            try:
                df = df.copy()
                df[dc] = pd.to_datetime(df[dc])
                df = df.set_index(dc).sort_index()
                return df
            except Exception:
                pass

    # try parsing current index if it's string-like
    try:
        idx = pd.to_datetime(df.index)
        df = df.copy()
        df.index = idx
        return df
    except Exception:
        return df


# ----------------------------
# Main
# ----------------------------
def main() -> None:
    print("[03] Run baseline analysis")
    print(f"     Project root: {PROJECT_ROOT}")

    df = _load_dataset()
    if df is None or df.empty:
        print("     Missing processed dataset.")
        print("     Expected: data/processed/dataset.parquet (or dataset.csv)")
        print("     Please run: python scripts/02_build_dataset.py")
        sys.exit(0)

    df = _maybe_set_datetime_index(df)

    cols = list(df.columns)

    # pick equity column
    eq_col = _pick_first(cols, "eq_")
    if eq_col is None:
        raise RuntimeError("No equity column found. Expected a column starting with 'eq_' in dataset.")

    # pick rate change column
    d_rate_col = None
    for c in cols:
        if c.startswith("d_rate_"):
            d_rate_col = c
            break
    if d_rate_col is None:
        d_rate_col = _pick_first(cols, "rate_")
    if d_rate_col is None:
        raise RuntimeError("No rate column found. Expected 'd_rate_*' or 'rate_*' in dataset.")

    # prepare y (returns) and x (rate change)
    y = _ensure_returns(df[eq_col])
    x = pd.to_numeric(df[d_rate_col], errors="coerce")

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

    # ---------------- Figure 1 ----------------
    fig1_path = REPORTS_FIG_DIR / "baseline_scatter.png"
    plt.figure()
    plt.scatter(aligned["x"], aligned["y"], s=10)
    x_line = np.linspace(aligned["x"].min(), aligned["x"].max(), 100)
    y_line = model.params["const"] + model.params["x"] * x_line
    plt.plot(x_line, y_line)
    plt.xlabel(d_rate_col)
    plt.ylabel(f"{eq_col} (returns if price-like)")
    plt.title("Baseline: Equity vs Rate Change")
    plt.tight_layout()
    plt.savefig(fig1_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"     Saved: {fig1_path.relative_to(PROJECT_ROOT)}")

    # ---------------- Figure 2 ----------------
    # Build volatility series from returns or use existing volatility column if present
    # We build volatility from the same return series used for the regression (y).
    vol_series, vol_label = _find_or_build_vol(df.assign(**{eq_col: y}), eq_col)

    fig2_path = REPORTS_FIG_DIR / "volatility_scatter.png"
    tmp = pd.concat(
        [pd.to_numeric(df[d_rate_col], errors="coerce").rename("x"),
         pd.to_numeric(vol_series, errors="coerce").rename("vol")],
        axis=1
    ).dropna()

    if tmp.shape[0] < 30:
        print("     Not enough observations for volatility plot (need >= 30). Skipping Figure 2.")
    else:
        plt.figure()
        plt.scatter(tmp["x"], tmp["vol"], s=8)
        plt.title("Scatter: Rate Change vs Rolling Volatility")
        plt.xlabel(d_rate_col)
        plt.ylabel(vol_label)
        plt.tight_layout()
        plt.savefig(fig2_path, dpi=150, bbox_inches="tight")
        plt.close()
        print(f"     Saved: {fig2_path.relative_to(PROJECT_ROOT)}")

    print("[03] Done.")
    print("Next step:")
    print("  - Run: python scripts/04_make_report.py")


if __name__ == "__main__":
    main()

