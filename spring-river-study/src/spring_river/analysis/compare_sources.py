"""Second-edition comparison: every precipitation-dependent result under each
basin source (aorc | prism_polygon | prism_buffer). Writes one long table,
a markdown summary and a figure. Uses the same functions as the phase
runners so a number here equals the phase doc's number for the default source.
"""
from datetime import date

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from spring_river.analysis.phase4 import _major_flood_dates
from spring_river.climate.coupling import lag_correlation, monthly_series, response_lag
from spring_river.climate.intensity import annual_indices, index_trends
from spring_river.config import (
    BASIN_PRECIP_SOURCE,
    BASIN_SOURCES,
    DOCS_DIR,
    FIGURES_DIR,
    PARAM_DISCHARGE,
    SITE_HARDY,
    SITE_MAMMOTH,
    START_DATE,
    TABLES_DIR,
)
from spring_river.hydro.lowflow import attribution_table, fit_attribution
from spring_river.hydro.postflood import matched_comparison, paired_summary
from spring_river.ingest import basin as basin_mod, oni, usgs

Q3_INDICES = ("total_in", "recharge_in", "max1_in", "sdii_in")
N_BOOT = 1000


def _row(source: str, block: str, metric: str, value: float, lo: float = np.nan, hi: float = np.nan, n: int | None = None) -> dict:
    return {"source": source, "block": block, "metric": metric, "value": float(value), "lo": float(lo), "hi": float(hi),
            "n": None if n is None else int(n)}


def _q1_rows(source: str, label: str, q: pd.DataFrame, basin: pd.DataFrame, oni_df: pd.DataFrame) -> list[dict]:
    fit = fit_attribution(attribution_table(q, basin, oni_df))
    blk = f"q1_{label}"
    lo, hi = fit.ci["p_trailing_in"]
    rt = fit.residual_trend
    return [
        _row(source, blk, "p_trailing_in coef (log-cfs/in)", fit.coef["p_trailing_in"], lo, hi, fit.n),
        _row(source, blk, "OLS R²", fit.r2, n=fit.n),
        _row(source, blk, "residual trend (log-cfs/yr)", rt.slope, rt.slope_lo, rt.slope_hi, rt.n),
    ]


def _q4_rows(source: str, label: str, q: pd.DataFrame, basin: pd.DataFrame, majors: pd.Series) -> list[dict]:
    s = paired_summary(matched_comparison(q, basin, majors))
    return [_row(source, f"q4_{label}", "post-flood base-flow diff (%)", s["mean_diff_pct"], s["lo"], s["hi"], s["n"])]


def _q3_rows(source: str, basin: pd.DataFrame) -> list[dict]:
    tr = index_trends(annual_indices(basin)).set_index("index")
    out = []
    for k in Q3_INDICES:
        r = tr.loc[k]
        out.append(_row(source, "q3", f"{k} slope/decade", r["slope_per_decade"], r["lo"], r["hi"], r["n"]))
        out.append(_row(source, "q3", f"{k} BH-significant", float(bool(r["significant_bh"])), n=r["n"]))
    return out


def _coupling_rows(source: str, basin: pd.DataFrame, mammoth: pd.DataFrame) -> list[dict]:
    lc = lag_correlation(monthly_series(basin, mammoth), n_boot=N_BOOT)
    best = response_lag(lc)
    r = lc.loc[lc["lag"] == best].iloc[0]
    return [_row(source, "coupling", "response lag (months)", best, n=r["n"]),
            _row(source, "coupling", "r at response lag", r["r"], r["r_lo"], r["r_hi"], r["n"])]


def compare_rows(source: str, series: dict[str, pd.DataFrame], basin: pd.DataFrame, oni_df: pd.DataFrame,
                 majors: pd.Series) -> list[dict]:
    rows = []
    for label, q in series.items():
        rows += _q1_rows(source, label, q, basin, oni_df)
        rows += _q4_rows(source, label, q, basin, majors)
    rows += _q3_rows(source, basin)
    rows += _coupling_rows(source, basin, series["mammoth"])
    return rows


def agreement_rows(a_name: str, a: pd.DataFrame, b_name: str, b: pd.DataFrame) -> list[dict]:
    j = a.merge(b, on="date", suffixes=("_a", "_b")).dropna()
    ya = j.set_index("date")["pcpn_in_a"].resample("YS").agg(["sum", "count"])
    yb = j.set_index("date")["pcpn_in_b"].resample("YS").agg(["sum", "count"])
    full = (ya["count"] >= 360) & (yb["count"] >= 360)
    ya, yb = ya.loc[full, "sum"], yb.loc[full, "sum"]
    src = f"{a_name} vs {b_name}"
    return [
        _row(src, "agreement", "daily_r", np.corrcoef(j["pcpn_in_a"], j["pcpn_in_b"])[0, 1], n=len(j)),
        _row(src, "agreement", "annual_total_r", np.corrcoef(ya, yb)[0, 1], n=len(ya)),
        _row(src, "agreement", "annual_total_ratio", yb.sum() / ya.sum(), n=len(ya)),
        _row(src, "agreement", f"{a_name} mean annual (in)", ya.mean(), n=len(ya)),
        _row(src, "agreement", f"{b_name} mean annual (in)", yb.mean(), n=len(yb)),
    ]


def _cell(r: pd.Series) -> str:
    if r["metric"].endswith("BH-significant"):
        return "yes" if r["value"] else "no"
    s = f"{r['value']:.3g}"
    if pd.notna(r["lo"]):
        s += f" ({r['lo']:.3g} to {r['hi']:.3g}"
        s += f"; n={int(r['n'])})" if pd.notna(r["n"]) else ")"
    elif pd.notna(r["n"]):
        s += f" (n={int(r['n'])})"
    return s


def to_markdown_table(df: pd.DataFrame) -> str:
    d = df.assign(cell=df.apply(_cell, axis=1))
    wide = d.pivot_table(index=["block", "metric"], columns="source", values="cell", aggfunc="first", sort=False)
    ordered = [s for s in BASIN_SOURCES if s in wide.columns]
    remaining = [c for c in wide.columns if c not in ordered]
    wide = wide.reindex(columns=ordered + remaining)
    return wide.reset_index().to_markdown(index=False)


def _figure(basins: dict[str, pd.DataFrame]) -> None:
    fig, ax = plt.subplots(figsize=(10, 4))
    for s, b in basins.items():
        a = b.set_index("date")["pcpn_in"].resample("YS").sum(min_count=360)
        ax.plot(a.index.year, a.values, marker="o", ms=3, label=s)
    ax.set_ylabel("calendar-year total (in)"); ax.set_xlabel("year"); ax.legend()
    ax.set_title("Basin precipitation by source; period 1981–present; no approval flag applies", fontsize=9)
    fig.tight_layout(); fig.savefig(FIGURES_DIR / "precip_sources_annual.png", dpi=150); plt.close(fig)


def main() -> None:
    end = date.today().isoformat()
    TABLES_DIR.mkdir(parents=True, exist_ok=True); FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    oni_df = oni.get_oni()
    series = {"mammoth": usgs.get_dv(SITE_MAMMOTH, PARAM_DISCHARGE, START_DATE, end),
              "hardy": usgs.get_dv(SITE_HARDY, PARAM_DISCHARGE, START_DATE, end)}
    majors = _major_flood_dates(usgs.get_peaks(SITE_HARDY))
    basins = {s: basin_mod.get_basin_pcpn(START_DATE, end, source=s) for s in BASIN_SOURCES}
    rows = []
    for s, b in basins.items():
        rows += compare_rows(s, series, b, oni_df, majors)
    rows += agreement_rows("aorc", basins["aorc"], "prism_polygon", basins["prism_polygon"])
    rows += agreement_rows("prism_polygon", basins["prism_polygon"], "prism_buffer", basins["prism_buffer"])
    df = pd.DataFrame(rows)
    df.to_parquet(TABLES_DIR / "precip_source_comparison.parquet")
    _figure(basins)
    lines = [f"# Basin precipitation source comparison — generated {date.today().isoformat()}", "",
             f"Default source for this edition: `{BASIN_PRECIP_SOURCE}`. Sources:", ""]
    lines += [f"- `{s}`: {basin_mod.basin_label(s)} ({b['date'].min().date()}–{b['date'].max().date()})" for s, b in basins.items()]
    lines += ["", "Same code paths as Phases 4 and 6 (all-data variant). Q1 = OLS p_trailing coefficient, R², residual Sen trend; "
              "Q4 = mean 6-month post-flood base-flow difference vs matched controls; Q3 = Sen slope per decade with BH flag; "
              "coupling = monthly anomaly lag correlation with block-bootstrap CI.", "",
              to_markdown_table(df[df["block"] != "agreement"]), "", "## Agreement between sources", "",
              to_markdown_table(df[df["block"] == "agreement"]), "",
              "![sources](../reports/figures/precip_sources_annual.png)", ""]
    (DOCS_DIR / "precip_comparison.md").write_text("\n".join(lines))
    print(f"wrote {DOCS_DIR / 'precip_comparison.md'} ({len(df)} rows)")


if __name__ == "__main__":
    main()
