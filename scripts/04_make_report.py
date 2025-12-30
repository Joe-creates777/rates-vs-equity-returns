#!/usr/bin/env python3
"""
04_make_report.py

Goal
----
Create a lightweight, human-readable report artifact from generated outputs.

Inputs (optional)
-----------------
reports/tables/baseline_regression.txt
reports/figures/baseline_scatter.png

Outputs
-------
reports/tables/summary.md
"""

from __future__ import annotations

from pathlib import Path
from datetime import datetime


PROJECT_ROOT = Path(__file__).resolve().parents[1]
FIG_PATH = PROJECT_ROOT / "reports" / "figures" / "baseline_scatter.png"
REG_PATH = PROJECT_ROOT / "reports" / "tables" / "baseline_regression.txt"
OUT_MD = PROJECT_ROOT / "reports" / "tables" / "summary.md"


def _rel(p: Path) -> str:
    try:
        return str(p.relative_to(PROJECT_ROOT))
    except Exception:
        return str(p)


def main() -> None:
    print("[04] Make report summary")
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    lines: list[str] = []
    lines.append("# Rates vs Equity Returns — Summary")
    lines.append("")
    lines.append(f"_Generated on: {ts}_")
    lines.append("")
    lines.append("## Artifacts")
    lines.append("")

    if FIG_PATH.exists():
        lines.append(f"- Figure: `{_rel(FIG_PATH)}`")
    else:
        lines.append(f"- Figure: (missing) expected `{_rel(FIG_PATH)}`")

    if REG_PATH.exists():
        lines.append(f"- Regression output: `{_rel(REG_PATH)}`")
    else:
        lines.append(f"- Regression output: (missing) expected `{_rel(REG_PATH)}`")

    lines.append("")
    lines.append("## How to reproduce")
    lines.append("")
    lines.append("Run the pipeline sequentially:")
    lines.append("")
    lines.append("```bash")
    lines.append("python scripts/01_fetch_data.py")
    lines.append("python scripts/02_build_dataset.py")
    lines.append("python scripts/03_run_analysis.py")
    lines.append("python scripts/04_make_report.py")
    lines.append("```")
    lines.append("")

    lines.append("## Notes")
    lines.append("")
    lines.append("- This is a lightweight summary for quick inspection.")
    lines.append("- Detailed exploration and validation live in `notebooks/`.")
    lines.append("- Most generated outputs are intentionally excluded from version control.")

    OUT_MD.parent.mkdir(parents=True, exist_ok=True)
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")

    print(f"     Saved: {_rel(OUT_MD)}")
    print("[04] Done.")


if __name__ == "__main__":
    main()
