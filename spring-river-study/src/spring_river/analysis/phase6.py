"""Phase 6 exit artifact: docs/phase6_precip.md (Q3 + coupling).

Series: USC00238880 (West Plains COOP; primary for trend because KUNO ASOS
only starts 1998), KUNO (1998→; check), PRISM 30 km basin mean (1981→).
Also resolves the qa_report open item: KUNO-vs-COOP agreement is re-tested
on monthly totals, where the ~7 AM COOP observation-day offset should wash
out.

Cache note: `acis.get_station_pcpn` keys its cache on the station id only,
so a 1948 start date returns the cached 1981+ COOP series. This build
accepts that and says so in the report; a 1948 backfill is a separate
`refresh=True` pull.
"""
import time
from datetime import date

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from spring_river.analysis.common import approval_variants, caption, write_report
from spring_river.climate.coupling import lag_correlation, monthly_series, response_lag
from spring_river.climate.intensity import INDEX_COLUMNS, annual_indices, index_trends
from spring_river.config import DOCS_DIR, FIGURES_DIR, PARAM_DISCHARGE, SITE_MAMMOTH, START_DATE, TABLES_DIR
from spring_river.ingest import acis, prism, usgs
from spring_river.ingest.pull_all import PRECIP_SIDS

COOP_SID = PRECIP_SIDS[1]
KUNO_SID = PRECIP_SIDS[0]
COOP_REQUESTED_START = "1948-01-01"
MIN_MONTH_DAYS = 25
N_BOOT = 1000


def _monthly_agreement(a: pd.DataFrame, b: pd.DataFrame) -> dict:
    ma = a.set_index("date")["pcpn_in"].resample("MS").agg(["sum", "count"])
    mb = b.set_index("date")["pcpn_in"].resample("MS").agg(["sum", "count"])
    j = ma.join(mb, lsuffix="_a", rsuffix="_b", how="inner")
    j = j[(j["count_a"] >= MIN_MONTH_DAYS) & (j["count_b"] >= MIN_MONTH_DAYS)]
    return {"months": int(len(j)), "r": float(np.corrcoef(j["sum_a"], j["sum_b"])[0, 1]),
            "ratio": float(j["sum_b"].sum() / j["sum_a"].sum()),
            "first": j.index.min().strftime("%Y-%m"), "last": j.index.max().strftime("%Y-%m")}


def _series_span(df: pd.DataFrame) -> str:
    ok = df.loc[df["pcpn_in"].notna(), "date"]
    return f"{ok.min().date()}–{ok.max().date()}"


def _trend_section(label: str, idx: pd.DataFrame, tr: pd.DataFrame, span: str) -> list[str]:
    valid = idx.dropna(subset=["total_in"])
    sig = tr[tr["significant_bh"]]
    verdict = ("no index passes BH at q=0.05" if sig.empty
               else "BH-significant: " + ", ".join(f"{r['index']} ({r['slope_per_decade']:+.3g}/decade, "
                                                    f"95% CI {r['lo']:.3g} to {r['hi']:.3g}, n={int(r['n'])} years)"
                                                    for _, r in sig.iterrows()))
    return [f"## {label}: index trends (Sen slope per decade, 95% CI; BH-adjusted p across {len(INDEX_COLUMNS)} indices)", "",
            f"- series span (non-missing days): {span}",
            f"- index years {int(valid['year'].min())}–{int(valid['year'].max())}; years passing 90% coverage: {len(valid)}",
            f"- {verdict}", "",
            tr.drop(columns="series").round(3).to_markdown(index=False), ""]


def _divergence_note(trends: dict[str, pd.DataFrame], coop_idx: pd.DataFrame) -> list[str]:
    n_sig = {k: int(v["significant_bh"].sum()) for k, v in trends.items()}
    failed = coop_idx.loc[coop_idx["total_in"].isna() & (coop_idx["year"] < date.today().year), "year"].astype(int).tolist()
    return ["## Station vs basin: reading the divergence", "",
            f"- BH-significant indices per series: {', '.join(f'{k} {v}/{len(INDEX_COLUMNS)}' for k, v in n_sig.items())}.",
            f"- {COOP_SID} years failing 90% coverage (excluded from its trend tests): {', '.join(map(str, failed))}. "
            "The 2011–2021 hole removes most of the recent wet decade from the station test, so its null result is "
            "low power, not evidence against the basin trend.",
            "- `recharge_in` uses a stricter gate than the other indices: coverage is judged against the full "
            "Sep (year-1)–Feb (year) calendar season, so it is NaN for any year whose season straddles a series start "
            "or a gap (e.g. a series beginning 1 Jan has no recharge value for its first year). Its n can therefore be "
            "smaller than the other indices' n for the same series, never larger.",
            "- PRISM basin values are a 4 km grid mean over a ~60 × 60 km box around West Plains; station gaps enter "
            "PRISM only indirectly through its interpolation. Treat the basin trends as the Q3 headline and the station tests as a consistency check.", ""]


def _lag_line(label: str, lc: pd.DataFrame) -> tuple[int, float, float, str]:
    best = response_lag(lc)
    row = lc.loc[lc["lag"] == best].iloc[0]
    return best, float(row["r_lo"]), float(row["r_hi"]), (
        f"- response lag ({label}): {best} months, r={row['r']:.2f} "
        f"(95% CI {row['r_lo']:.2f} to {row['r_hi']:.2f}), n={int(row['n'])} months")


def _lag_sensitivity(lc_all: pd.DataFrame, lc_appr: pd.DataFrame) -> list[str]:
    lag_a, lo_a, hi_a, line_a = _lag_line("all data", lc_all)
    lag_p, lo_p, hi_p, line_p = _lag_line("approved-only flow", lc_appr)
    overlap = lo_a <= hi_p and lo_p <= hi_a
    lines = ["### Sensitivity: all vs approved-only Mammoth flow", "", line_a, line_p]
    if lag_a != lag_p or not overlap:
        lines.append("- **CHANGED**: response lag or r CI differs between all and approved-only flow.")
    else:
        lines.append("- unchanged: same response lag and overlapping r CIs.")
    return lines + [""]


def _indices_figure(idx: pd.DataFrame, label: str, span: str, path) -> None:
    fig, axes = plt.subplots(3, 1, figsize=(11, 9), sharex=True)
    axes[0].bar(idx["year"], idx["total_in"]); axes[0].set_ylabel("annual total (in)")
    axes[1].plot(idx["year"], idx["days_ge_1"], marker="o"); axes[1].set_ylabel("days ≥ 1 in")
    axes[2].plot(idx["year"], idx["max1_in"], marker="o"); axes[2].set_ylabel("max 1-day (in)"); axes[2].set_xlabel("year")
    fig.suptitle(f"Q3 indices — {label} (West Plains COOP); source: RCC-ACIS StnData; period {span}; "
                 "years with <90% daily coverage omitted; approval: N/A — station precip carries no approval flag",
                 fontsize=9)
    fig.tight_layout(rect=(0, 0, 1, 0.95)); fig.savefig(path, dpi=150); plt.close(fig)


def _lag_figure(lc: pd.DataFrame, mammoth: pd.DataFrame, path) -> None:
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.errorbar(lc["lag"], lc["r"], yerr=[lc["r"] - lc["r_lo"], lc["r_hi"] - lc["r"]], marker="o", capsize=3)
    ax.axhline(0, color="grey", lw=0.8)
    ax.set_xlabel("lag (months)"); ax.set_ylabel("r (anomalies)")
    ax.set_title(f"basin precip → Mammoth Spring flow (block bootstrap 95% CI)\n"
                 f"USGS DV {SITE_MAMMOTH} + PRISM 30 km; {mammoth['date'].min().year}–{mammoth['date'].max().year}; "
                 f"approved {mammoth['approved'].mean():.0%}", fontsize=9)
    fig.tight_layout(); fig.savefig(path, dpi=150); plt.close(fig)


def main() -> None:
    end = date.today().isoformat()
    TABLES_DIR.mkdir(parents=True, exist_ok=True); FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    coop = acis.get_station_pcpn(COOP_SID, COOP_REQUESTED_START, end)
    kuno = acis.get_station_pcpn(KUNO_SID, START_DATE, end)
    basin = prism.get_basin_pcpn(START_DATE, end)
    mammoth = usgs.get_dv(SITE_MAMMOTH, PARAM_DISCHARGE, START_DATE, end)

    coop_span = _series_span(coop)
    lines = [f"# Phase 6 — precipitation regime (Q3) — generated {date.today().isoformat()}", "",
             f"Series: {COOP_SID} West Plains COOP ({coop_span}; COOP series 1981+ in this build — the ACIS cache is "
             f"keyed on station id, so the {COOP_REQUESTED_START[:4]} request returned the cached 1981+ pull; a 1948 backfill "
             f"needs a `refresh=True` pull), KUNO ASOS ({_series_span(kuno)}), PRISM 30 km basin mean ({_series_span(basin)}).", "",
             "## Station agreement on monthly totals (qa_report follow-up)", ""]
    ag = _monthly_agreement(kuno, coop)
    lines += [f"- KUNO vs {COOP_SID} monthly totals (months with ≥{MIN_MONTH_DAYS} days at both stations): r={ag['r']:.2f}, "
              f"ratio COOP/KUNO={ag['ratio']:.2f}, n={ag['months']} months ({ag['first']} to {ag['last']}). "
              f"Daily r was 0.42 in qa_report; monthly aggregation removes the ~7 AM observation-day offset.", ""]

    trends = {}
    for label, df in ((COOP_SID, coop), ("KUNO", kuno), ("basin", basin)):
        idx = annual_indices(df)
        idx.to_parquet(TABLES_DIR / f"phase6_indices_{label}.parquet")
        tr = index_trends(idx).assign(series=label)
        trends[label] = tr
        lines += _trend_section(label, idx, tr, _series_span(df))
    pd.concat(trends.values()).to_parquet(TABLES_DIR / "phase6_index_trends.parquet")
    lines += _divergence_note(trends, pd.read_parquet(TABLES_DIR / f"phase6_indices_{COOP_SID}.parquet"))

    t0 = time.perf_counter()
    lcs = {k: lag_correlation(monthly_series(basin, v), n_boot=N_BOOT) for k, v in approval_variants(mammoth).items()}
    lag_secs = time.perf_counter() - t0
    lc = lcs["all"]
    pd.concat([v.assign(variant=k) for k, v in lcs.items()]).to_parquet(TABLES_DIR / "phase6_lag_correlation.parquet")
    lines += ["## Coupling: monthly basin precip → Mammoth Spring flow (anomaly correlation by lag)", "",
              f"Monthly anomalies (climatology removed; log flow), lags 0–{int(lc['lag'].max())} months, "
              f"{N_BOOT} 12-month block-bootstrap resamples for the CI (both variants, {lag_secs:.0f} s). Table: all data.", "",
              lc.round(3).to_markdown(index=False), "",
              _lag_line("max r", lc)[3], ""]
    lines += _lag_sensitivity(lc, lcs["approved"])

    idx = pd.read_parquet(TABLES_DIR / f"phase6_indices_{COOP_SID}.parquet")
    _indices_figure(idx, COOP_SID, coop_span, FIGURES_DIR / "phase6_indices.png")
    _lag_figure(lc, mammoth, FIGURES_DIR / "phase6_lag_correlation.png")
    lines += ["![indices](../reports/figures/phase6_indices.png)", "",
              f"Figure: annual total, days ≥ 1 in, and max 1-day precip at {COOP_SID}; source RCC-ACIS StnData; period {coop_span}; "
              "years with <90% daily coverage omitted; approval N/A — station precip carries no approval flag.", "",
              "![lag](../reports/figures/phase6_lag_correlation.png)", "",
              f"Figure: {caption(f'USGS DV {SITE_MAMMOTH} + PRISM 30 km basin mean', mammoth)}.", "",
              "## Limitations", "",
              "- Station indices are point measurements; basin indices are a 4 km grid mean (smoother extremes by construction).",
              f"- COOP series 1981+ in this build (cache keyed on station id); the 1948–1980 record is not yet pulled, so the "
              f"{COOP_SID} trend window matches KUNO/basin rather than extending it.",
              f"- {COOP_SID} has 32 gaps > 7 days (qa_report); years failing 90% coverage are NaN, not low. KUNO years before 1998 are NaN by coverage.",
              "- Precip series carry no approval flag; the all/approved-only rule does not apply to the index trends. "
              "It does apply to the coupling (Mammoth flow carries flags) and is reported above. "
              f"Mammoth flow used in coupling: {caption(f'USGS DV {SITE_MAMMOTH}', mammoth)}.",
              "- Lag-correlation CI is a 12-month block bootstrap of the lagged pairs; it preserves within-year "
              "serial correlation but not dependence across block boundaries, so it is mildly optimistic."]
    write_report(DOCS_DIR / "phase6_precip.md", lines)
    print(f"wrote {DOCS_DIR / 'phase6_precip.md'} (lag bootstrap {lag_secs:.0f} s)")


if __name__ == "__main__":
    main()
