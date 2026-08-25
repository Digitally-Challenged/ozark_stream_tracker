"""Shared formatting/sensitivity helpers for the phase runners.
Enforces: captions carry source/period/approval; trend claims carry
test, effect size, CI, n; every analysis reported for all vs approved-only."""
from pathlib import Path

import pandas as pd

from spring_river.stats.trends import TrendResult


def approval_variants(df: pd.DataFrame) -> dict[str, pd.DataFrame]:
    return {"all": df, "approved": df[df["approved"]].reset_index(drop=True)}


def caption(source: str, df: pd.DataFrame) -> str:
    frac = float(df["approved"].mean()) if len(df) else float("nan")
    prov = df.loc[~df["approved"], "date"].min() if len(df) else None
    s = f"source: {source}; period {df['date'].min().date()}–{df['date'].max().date()}; approved {frac:.0%}"
    if pd.notna(prov):
        s += f", provisional from {prov.date()}"
    return s


def fmt_trend(r: TrendResult, unit: str, per: str = "yr") -> str:
    return (
        f"Sen slope {r.slope:.3g} {unit}/{per} (95% CI {r.slope_lo:.3g} to {r.slope_hi:.3g}); "
        f"MK z={r.z:.2f}, p={r.p:.3f}; n={r.n}"
    )


def _includes_zero(r: TrendResult) -> bool:
    return r.slope_lo <= 0 <= r.slope_hi


def sensitivity_lines(name: str, all_r: TrendResult, appr_r: TrendResult) -> list[str]:
    changed = (all_r.slope > 0) != (appr_r.slope > 0) or _includes_zero(all_r) != _includes_zero(appr_r)
    lines = [f"- {name} (all): {fmt_trend(all_r, '')}", f"- {name} (approved-only): {fmt_trend(appr_r, '')}"]
    if changed:
        lines.append(f"- **CHANGED**: {name} conclusion differs between all and approved-only data.")
    return lines


def write_report(path: Path, lines: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n")
