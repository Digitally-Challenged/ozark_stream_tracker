"""Phase 5 exit artifact: docs/phase5_floods.md (Q2, Q6, Q7, Q8).

Series decisions (data_inventory.md): Imboden annual peaks (WY 1937–2025 in
the NWIS peaks file) is the long frequency series; Hardy WY 2002–2025 (n=24)
is the site series; the 1982-12-03 29.0 ft NWS crest is reported as a
historical exceedance only (no flow; not in the LP3 fit — EMA/PeakFQ
follow-up).
"""
from datetime import date

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from spring_river.analysis.common import approval_variants, caption, fmt_trend, write_report  # noqa: E402
from spring_river.config import (  # noqa: E402
    DOCS_DIR,
    FIGURES_DIR,
    MAJOR_FLOOD_FT,
    PARAM_DISCHARGE,
    PARAM_STAGE,
    REGIONAL_SKEW,
    SITE_HARDY,
    SITE_IMBODEN,
    START_DATE,
    TABLES_DIR,
)
from spring_river.hydro.freq_lp3 import (  # noqa: E402
    LP3Fit,
    bootstrap_quantiles,
    fit_lp3,
    return_period,
    stage_flow_fit,
    stage_to_flow,
)
from spring_river.hydro.interarrival import antecedent_conditions, interarrival_test  # noqa: E402
from spring_river.hydro.pot import annual_counts, dispersion_test, pot_events  # noqa: E402
from spring_river.hydro.wateryear import daily_max_stage, water_year  # noqa: E402
from spring_river.ingest import nwps, prism, usgs  # noqa: E402
from spring_river.ingest.pull_all import IV_START  # noqa: E402
from spring_river.stats.permutation import conditional_rate_test  # noqa: E402
from spring_river.stats.trends import TrendResult, pettitt, trend_test  # noqa: E402

RETURN_PERIODS = (1.25, 2, 5, 10, 25, 50, 100)
STAGE_THRESHOLDS_FT = (8.0, 10.0, 14.0, 16.0, 20.0, 23.0)
POT_THRESHOLDS_FT = (8.0, 10.0, 14.0, 16.0)
QUIET_FT = 8.0
MODERATE_FT = 14.0
HISTORIC_CREST_FT = 29.0
SPLIT_WY = 2008
VERDICT_RP = 10


def _peaks_by_wy(peaks: pd.DataFrame) -> pd.DataFrame:
    """One peak per water year (largest flow), tz-naive dates so they concat with IV-derived dates."""
    dates = pd.to_datetime(peaks["date"])
    if dates.dt.tz is not None:
        dates = dates.dt.tz_localize(None)
    p = peaks.assign(date=dates, wy=water_year(dates))
    return (
        p.sort_values("peak_cfs", ascending=False)
        .drop_duplicates("wy")
        .sort_values("wy")
        .reset_index(drop=True)
    )


def _lp3_table(
    label: str, peaks: pd.DataFrame, lines: list[str], regional_skew: float | None
) -> tuple[pd.DataFrame, LP3Fit]:
    x = peaks["peak_cfs"].dropna().to_numpy()
    fit = fit_lp3(x, regional_skew=regional_skew)
    tbl = bootstrap_quantiles(x, RETURN_PERIODS, regional_skew=regional_skew)
    slug = label.lower().replace(" ", "_").replace("—", "").replace("<", "lt").replace("≥", "ge")
    slug = "_".join(s for s in slug.split("_") if s)
    tbl.to_parquet(TABLES_DIR / f"phase5_lp3_{slug}.parquet")
    lines += [
        f"### {label} (n={fit.n}, WY {int(peaks['wy'].min())}–{int(peaks['wy'].max())}, "
        f"station skew {fit.station_skew:.2f}, weighted skew {fit.weighted_skew:.2f}, "
        f"low outliers dropped {fit.n_dropped} below {fit.low_outlier_threshold_cfs:.0f} cfs)",
        "",
        tbl.round({"q_cfs": 0, "q_lo": 0, "q_hi": 0}).to_markdown(index=False),
        "",
    ]
    return tbl, fit


def _fmt_rp(x: float) -> str:
    return ">1000" if not np.isfinite(x) or x > 1000 else f"{x:.1f}"


def _ci_excludes_zero(r: TrendResult) -> bool:
    return r.slope_lo > 0 or r.slope_hi < 0


def _rp_row(tbl: pd.DataFrame, rp: float) -> pd.Series:
    return tbl.loc[tbl["return_period"] == rp].iloc[0]


def _stationarity_verdict(imb_trend: TrendResult, pre: pd.DataFrame, post: pd.DataFrame) -> list[str]:
    """Rule from the plan: non-stationary only if the Imboden peak-trend CI excludes zero
    AND the pre/post split 10-yr quantile CIs do not overlap."""
    a, b = _rp_row(pre, VERDICT_RP), _rp_row(post, VERDICT_RP)
    overlap = bool(a["q_lo"] <= b["q_hi"] and b["q_lo"] <= a["q_hi"])
    trend_sig = _ci_excludes_zero(imb_trend)
    verdict = "non-stationary" if trend_sig and not overlap else "no detectable change in flood frequency"
    return [
        f"**Verdict: {verdict}.**",
        "",
        f"- Imboden peak trend CI excludes zero: {'yes' if trend_sig else 'no'} "
        f"(Sen slope {imb_trend.slope:+.4f} log10-cfs/yr, 95% CI {imb_trend.slope_lo:+.4f} to {imb_trend.slope_hi:+.4f}).",
        f"- Imboden {VERDICT_RP}-yr quantile, WY <{SPLIT_WY}: {a['q_cfs']:,.0f} cfs (5–95% {a['q_lo']:,.0f}–{a['q_hi']:,.0f}); "
        f"WY ≥{SPLIT_WY}: {b['q_cfs']:,.0f} cfs ({b['q_lo']:,.0f}–{b['q_hi']:,.0f}); CIs overlap: {'yes' if overlap else 'no'}.",
        "- Rule: 'non-stationary' requires both a trend CI excluding zero and non-overlapping split-period "
        f"{VERDICT_RP}-yr CIs. Magnitude-tier comparison at Hardy rests on n=24.",
    ]


def _q6_lines(hardy_pk: pd.DataFrame, stage: pd.DataFrame, crests: pd.DataFrame) -> list[str]:
    major_pre = hardy_pk[(hardy_pk["wy"] < SPLIT_WY) & (hardy_pk["gage_ht_ft"] >= MAJOR_FLOOD_FT)]["date"]
    major_post = pot_events(stage, MAJOR_FLOOD_FT)["peak_date"].dt.normalize()
    majors = pd.concat([major_pre, major_post]).sort_values().reset_index(drop=True)
    hist = crests[crests["stage_ft"] >= HISTORIC_CREST_FT]["date"].dt.normalize()
    majors_hist = pd.concat([hist, majors]).sort_values().reset_index(drop=True)
    lines = [
        f"## Q6 inter-arrival of ≥{MAJOR_FLOOD_FT:.0f} ft events",
        "",
        f"Events (annual-peak file for WY <{SPLIT_WY}, 7-day-declustered daily-max IV stage for WY ≥{SPLIT_WY}): "
        + ", ".join(d.strftime("%Y-%m-%d") for d in majors),
        "",
    ]
    for label, ev in (("2002–present", majors), ("with 1982 crest", majors_hist)):
        try:
            r = interarrival_test(ev)
        except ValueError as exc:
            lines.append(f"- {label}: not testable ({exc})")
            continue
        lines.append(
            f"- {label}: n={r['n_events']}, mean gap {r['mean_gap_yr']:.2f} yr, median {r['median_gap_yr']:.2f}, "
            f"CV {r['cv']:.2f}; KS vs exponential {r['ks_stat']:.2f}, bootstrap p={r['p_boot']:.3f}"
        )
    lines += [
        "",
        "A bootstrap p well above 0.05 means the gaps are consistent with a memoryless (Poisson) process — "
        "no evidence of a regular cadence; CV near 1 is the exponential signature, CV well below 1 would indicate regularity.",
        "",
    ]
    return lines


def _q7_lines(hardy_pk: pd.DataFrame) -> list[str]:
    ledger_like = (
        hardy_pk.set_index("wy")["gage_ht_ft"]
        .reindex(range(int(hardy_pk["wy"].min()), int(hardy_pk["wy"].max()) + 1))
    )
    major = (ledger_like >= MAJOR_FLOOD_FT).to_numpy()
    quiet = (ledger_like < QUIET_FT).to_numpy()
    q7 = conditional_rate_test(major, quiet)
    return [
        f"## Q7 quiet year (<{QUIET_FT:.0f} ft peak) after a ≥{MAJOR_FLOOD_FT:.0f} ft year",
        "",
        f"- P(quiet | prior major) = {q7.rate_after_major:.2f} vs base rate {q7.base_rate:.2f}; "
        f"difference {q7.diff:+.2f} (bootstrap 95% CI {q7.diff_lo:+.2f} to {q7.diff_hi:+.2f}); "
        f"permutation p={q7.p:.3f}; n_major={q7.n_major}, n_years={q7.n_years}",
        "",
        f"Water years with a missing annual peak count as neither major nor quiet. "
        f"With n_major={q7.n_major} the test has little power; the CI is the honest statement.",
        "",
    ]


def _freq_figure(hardy_tbl: pd.DataFrame, imb_tbl: pd.DataFrame, imb_pk: pd.DataFrame) -> None:
    fig, ax = plt.subplots(figsize=(8, 5))
    for label, tbl in (("Hardy", hardy_tbl), ("Imboden", imb_tbl)):
        ax.plot(tbl["return_period"], tbl["q_cfs"], marker="o", label=label)
        ax.fill_between(tbl["return_period"], tbl["q_lo"], tbl["q_hi"], alpha=0.2)
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel("return period (yr)")
    ax.set_ylabel("peak flow (cfs)")
    ax.legend()
    ax.set_title(
        "LP3 frequency curves, 5–95% bootstrap\n"
        f"source: USGS annual peaks {SITE_HARDY} (WY 2002–2025), {SITE_IMBODEN} "
        f"(WY {int(imb_pk['wy'].min())}–{int(imb_pk['wy'].max())}); peaks file is approved data",
        fontsize=9,
    )
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / "phase5_freq_curves.png", dpi=150)
    plt.close(fig)


def _pot_figure(wys: list[int], counts: dict, stage: pd.DataFrame) -> None:
    fig, ax = plt.subplots(figsize=(10, 4))
    for h in POT_THRESHOLDS_FT:
        ax.plot(wys, counts[("all", h)].to_numpy(), marker="o", label=f"≥{h:.0f} ft")
    ax.set_xlabel("water year")
    ax.set_ylabel("events / yr")
    ax.legend()
    ax.set_title(f"POT event counts\n{caption(f'USGS IV stage {SITE_HARDY} daily max', stage)}", fontsize=9)
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / "phase5_pot_counts.png", dpi=150)
    plt.close(fig)


def main() -> None:
    end = date.today().isoformat()
    TABLES_DIR.mkdir(parents=True, exist_ok=True)
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    hardy_pk = _peaks_by_wy(usgs.get_peaks(SITE_HARDY))
    imb_pk = _peaks_by_wy(usgs.get_peaks(SITE_IMBODEN))
    hardy_dv = usgs.get_dv(SITE_HARDY, PARAM_DISCHARGE, START_DATE, end)
    stage = daily_max_stage(usgs.get_iv(SITE_HARDY, PARAM_STAGE, IV_START, end))
    basin = prism.get_basin_pcpn(START_DATE, end)
    crests = nwps.historic_crests(nwps.get_gauge_info())

    lines = [
        f"# Phase 5 — floods (Q2, Q6, Q7, Q8) — generated {date.today().isoformat()}",
        "",
        "## Q8 LP3 flood frequency (5–95% bootstrap CI)",
        "",
        f"Regional skew {REGIONAL_SKEW} (approximate, see config); the 'station skew only' block is the sensitivity case. "
        "LP3 by method of moments with B17-weighted skew and a Grubbs-Beck low-outlier screen; parametric-bootstrap CIs "
        "(2000 resamples). Not EMA.",
        "",
    ]
    hardy_tbl, fit_h = _lp3_table("Hardy", hardy_pk, lines, REGIONAL_SKEW)
    _lp3_table("Hardy — station skew only", hardy_pk, lines, None)
    imb_tbl, _ = _lp3_table("Imboden", imb_pk, lines, REGIONAL_SKEW)

    # stage thresholds -> flow -> return period (Hardy)
    a, b, r2 = stage_flow_fit(hardy_pk)
    n_wy = len(hardy_pk)
    rows = []
    for h in STAGE_THRESHOLDS_FT:
        q = stage_to_flow(a, b, h)
        emp = int((hardy_pk["gage_ht_ft"] >= h).sum())
        hist_n = int((crests["stage_ft"] >= h).sum())
        rows.append(
            {
                "stage_ft": h,
                "flow_cfs": q,
                "lp3_return_period_yr": return_period(fit_h, q),
                "empirical_exceedances_2002_2025": emp,
                "empirical_return_period_yr": n_wy / emp if emp else float("inf"),
                "nws_crests_ge_stage_1982_2025": hist_n,
            }
        )
    rp = pd.DataFrame(rows)
    rp.to_parquet(TABLES_DIR / "phase5_return_periods_stage.parquet")
    rp_show = rp.assign(
        flow_cfs=rp["flow_cfs"].round(0),
        lp3_return_period_yr=rp["lp3_return_period_yr"].map(_fmt_rp),
        empirical_return_period_yr=rp["empirical_return_period_yr"].map(_fmt_rp),
    )
    lines += [
        "### Stage thresholds at Hardy",
        "",
        f"Stage→flow from the {n_wy} annual-peak (stage, flow) pairs: log10 Q = {a:.3f} + {b:.3f}·log10 H (R²={r2:.3f}). "
        "NWS categories: action 8, minor 10, moderate 14, major 16 ft.",
        "",
        rp_show.to_markdown(index=False),
        "",
        f"NWS crest count includes the 1982-12-03 {HISTORIC_CREST_FT:.1f} ft record; the Hardy systematic record is WY 2002+. "
        "Empirical return period = n_years / exceedances of the annual-peak stage.",
        "",
    ]

    # Q2 stationarity
    lines += ["## Q2 stationarity", ""]
    trends: dict[str, TrendResult] = {}
    for label, pk in (("Hardy", hardy_pk), ("Imboden", imb_pk)):
        x = np.log10(pk["peak_cfs"].to_numpy(dtype="float64"))
        wy = pk["wy"].to_numpy(dtype="float64")
        r = trend_test(x, wy)
        pt = pettitt(x)
        trends[label] = r
        lines.append(
            f"- {label} annual peaks (log10 cfs): {fmt_trend(r, 'log10-cfs')}; "
            f"Pettitt change after WY {int(pk['wy'].iloc[pt.change_index])} (p={pt.p:.3f})"
        )
    pre = imb_pk[imb_pk["wy"] < SPLIT_WY]
    post = imb_pk[imb_pk["wy"] >= SPLIT_WY]
    lines += ["", f"Imboden LP3 split at WY {SPLIT_WY}:", ""]
    pre_tbl, _ = _lp3_table(f"Imboden WY <{SPLIT_WY}", pre, lines, REGIONAL_SKEW)
    post_tbl, _ = _lp3_table(f"Imboden WY ≥{SPLIT_WY}", post, lines, REGIONAL_SKEW)

    # POT (Hardy daily max stage, WY 2008+)
    lines += ["## Partial-duration series (Hardy daily max IV stage, 7-day declustering)", ""]
    wys = sorted(set(water_year(stage["date"])))
    counts: dict[tuple[str, float], pd.Series] = {}
    for variant, st in approval_variants(stage).items():
        for h in POT_THRESHOLDS_FT:
            c = annual_counts(pot_events(st, h), wys)
            counts[(variant, h)] = c
            if variant == "all":
                dt = dispersion_test(c)
                r = trend_test(c.to_numpy(dtype="float64"), np.array(wys, dtype="float64"))
                lines.append(
                    f"- ≥{h:.0f} ft: {int(c.sum())} events over WY {wys[0]}–{wys[-1]}; mean {dt['mean']:.2f}/yr; "
                    f"dispersion {dt['dispersion']:.2f} (p={dt['p']:.3f}); count trend {fmt_trend(r, 'events')}"
                )
    pot_tbl = pd.DataFrame({f"ge_{int(h)}ft_{v}": c for (v, h), c in counts.items()})
    pot_tbl.to_parquet(TABLES_DIR / "phase5_pot_counts.parquet")
    lines += [
        "",
        f"Dispersion index = variance/mean of annual counts (1 under Poisson; >1 clustered). "
        f"WY {wys[-1]} is partial (stage through {stage['date'].max().date()}). "
        "Sensitivity (approved-only days) totals: "
        + ", ".join(f"≥{int(h)} ft {int(c.sum())}" for (v, h), c in counts.items() if v == "approved"),
        "",
        pot_tbl.to_markdown(),
        "",
    ]

    lines += _q6_lines(hardy_pk, stage, crests)
    lines += _q7_lines(hardy_pk)

    # antecedent conditions before >=14 ft
    mod = hardy_pk[hardy_pk["gage_ht_ft"] >= MODERATE_FT]["date"]
    ante = antecedent_conditions(hardy_dv, basin, mod)
    lines += [
        f"## Antecedent conditions before ≥{MODERATE_FT:.0f} ft annual peaks (60-day BFI, 30-day basin precip)",
        "",
        ante.round(2).to_markdown(index=False),
        "",
        "BFI from segmented Eckhardt on Hardy DV discharge; precip is the PRISM 30 km-buffer basin mean. "
        "Windows exclude the event day.",
        "",
    ]

    _freq_figure(hardy_tbl, imb_tbl, imb_pk)
    _pot_figure(wys, counts, stage)
    lines += ["![freq](../reports/figures/phase5_freq_curves.png)", "", "![pot](../reports/figures/phase5_pot_counts.png)", ""]

    lines += ["## Stationarity verdict", ""]
    lines += _stationarity_verdict(trends["Imboden"], pre_tbl, post_tbl)
    lines += [
        "",
        "## Limitations",
        "",
        "- LP3/MOM with weighted skew, not EMA; 1982 historical crest not in the fit. Regional skew approximate.",
        "- Hardy n=24; return periods beyond ~50 yr are extrapolation — the CIs say so.",
        "- Stage↔flow mapping is a log-log fit to annual-peak pairs, not the USGS rating; rating shifts (Q5) propagate here.",
        "- POT and Q6 post-2008 events use daily MAX IV stage (upper bound vs a daily-mean product).",
        f"- Imboden peaks file in NWIS begins WY {int(imb_pk['wy'].min())}; the split at WY {SPLIT_WY} leaves n={len(post)} in the post period.",
    ]
    write_report(DOCS_DIR / "phase5_floods.md", lines)
    print(f"wrote {DOCS_DIR / 'phase5_floods.md'}")


if __name__ == "__main__":
    main()
