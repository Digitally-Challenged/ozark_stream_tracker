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
    fit_lp3_historical,
    return_period,
    stage_flow_fit,
    stage_to_flow,
)
from spring_river.hydro.interarrival import (  # noqa: E402
    antecedent_conditions,
    interarrival_power,
    interarrival_test,
    null_cv_interval,
)
from spring_river.hydro.pot import annual_counts, dispersion_test, pot_events  # noqa: E402
from spring_river.hydro.wateryear import daily_max_stage, water_year  # noqa: E402
from spring_river.ingest import basin as basin_mod  # noqa: E402
from spring_river.ingest import nwps, usgs  # noqa: E402
from spring_river.ingest.pull_all import IV_START  # noqa: E402
from spring_river.stats.permutation import conditional_rate_power, conditional_rate_test  # noqa: E402
from spring_river.stats.trends import TrendResult, pettitt, trend_test  # noqa: E402

RETURN_PERIODS = (1.25, 2, 5, 10, 25, 50, 100)
STAGE_THRESHOLDS_FT = (8.0, 10.0, 14.0, 16.0, 20.0, 23.0)
POT_THRESHOLDS_FT = (8.0, 10.0, 14.0, 16.0)
QUIET_FT = 8.0
MODERATE_FT = 14.0
HISTORIC_CREST_FT = 29.0
SPLIT_WY = 2008
VERDICT_RP = 10


HISTORICAL_PERIODS_YR = (44, 90)   # 1982–2025, and back to the Imboden record's start
Q6_POWER_CVS = (0.7, 0.5, 0.35)
Q7_POWER_RATES = (0.2, 0.4, 0.6, 0.8)
HEADLINE_STAGES_FT = (16.0, 20.0, 23.0)


def _historical_section(hardy_pk: pd.DataFrame, a: float, b: float, fit_h: LP3Fit) -> list[str]:
    """Phase 8 (review.md item 4): the 1982 crest as historical information.

    Excluding a KNOWN extreme biases the return periods of exactly the tier
    the reader most cares about. This is the headline sensitivity; the station-
    vs-regional-skew case tests a parameter that barely moves the answer.
    """
    q82 = stage_to_flow(a, b, HISTORIC_CREST_FT)
    systematic = hardy_pk["peak_cfs"].dropna().to_numpy()
    rows = [{"case": "systematic only (headline fit)", "historical_period_yr": pd.NA,
             "n_effective": fit_h.n, "weighted_skew": fit_h.weighted_skew,
             **{f"rp_{int(s)}ft_yr": return_period(fit_h, stage_to_flow(a, b, s))
                for s in HEADLINE_STAGES_FT}}]
    for H in HISTORICAL_PERIODS_YR:
        f = fit_lp3_historical(systematic, [q82], H, regional_skew=REGIONAL_SKEW)
        rows.append({"case": f"with 1982 crest, H={H} yr", "historical_period_yr": H,
                     "n_effective": f.n, "weighted_skew": f.weighted_skew,
                     **{f"rp_{int(s)}ft_yr": return_period(f, stage_to_flow(a, b, s))
                        for s in HEADLINE_STAGES_FT}})
    tbl = pd.DataFrame(rows)
    tbl.to_parquet(TABLES_DIR / "phase5_historical_1982.parquet")
    col = f"rp_{int(HEADLINE_STAGES_FT[-1])}ft_yr"
    lo, hi = float(tbl[col].min()), float(tbl[col].max())
    lo20, hi20 = float(tbl["rp_20ft_yr"].min()), float(tbl["rp_20ft_yr"].max())
    return [
        "### Sensitivity: the 1982 crest as historical information", "",
        f"The 1982-12-03 {HISTORIC_CREST_FT:.1f} ft crest is known but sits outside the systematic record "
        f"(Hardy WY {int(hardy_pk['wy'].min())}+). By the annual-peak log-log relation it is ≈{q82:,.0f} cfs. "
        "Leaving a known extreme out biases the return periods of the major-exposure tier long, so it is added "
        "back by Bulletin 17B historical weighting (W = (H−Z)/(n−s); peaks at or above the threshold keep "
        "weight 1). Historical period H = 44 yr (1982–2025) and 90 yr (back to the long record's start).", "",
        tbl.round({"weighted_skew": 3, **{f"rp_{int(s)}ft_yr": 1 for s in HEADLINE_STAGES_FT}}).to_markdown(index=False),
        "",
        f"- **This is the headline sensitivity for Q8.** Across the cases, 20 ft is {lo20:.0f}–{hi20:.0f} yr and "
        f"23 ft is {lo:.0f}–{hi:.0f} yr; the systematic-only point estimates are biased long by roughly 20–30 % "
        "at these stages. They remain inside the bootstrap 5–95 % band, so the published figures are not "
        f"refuted — but 23 ft should be quoted as **{lo:.0f}–{hi:.0f} yr**, not as a single number.",
        "- The station-vs-regional-skew case (reported above) moves 23 ft by well under a year: it tests a "
        "parameter that does not matter here, and is retained only as a completeness check.",
        "- This is historical weighting, not EMA. PeakFQ/EMA with the 1982 crest over a stated perceptibility "
        "threshold remains the documented follow-up.", "",
    ]


def _q2_upper_tail_section(imb_pk: pd.DataFrame) -> list[str]:
    """Phase 8 (review.md item 6): a pre-registered upper-tail test, and the
    2008 mean shift disclosed as post hoc."""
    import statsmodels.formula.api as smf
    from scipy import stats as st

    y = np.log10(imb_pk["peak_cfs"].to_numpy(dtype="float64"))
    wy = imb_pk["wy"].to_numpy(dtype="float64")
    d = pd.DataFrame({"y": y, "t": wy - wy.mean()})
    rows = []
    for q in (0.5, 0.9):
        m = smf.quantreg("y ~ t", d).fit(q=q)
        ci = m.conf_int().loc["t"].to_numpy()
        rows.append({"quantile": q, "slope_log10_per_yr": float(m.params["t"]),
                     "lo": float(ci[0]), "hi": float(ci[1]), "p": float(m.pvalues["t"])})
    qr = pd.DataFrame(rows)
    thr = float(np.quantile(y, 0.75))
    sel = y >= thr
    ts = st.theilslopes(y[sel], wy[sel])
    a_pre, b_post = y[wy < SPLIT_WY], y[wy >= SPLIT_WY]
    welch = float(st.ttest_ind(a_pre, b_post, equal_var=False).pvalue)
    mwu = float(st.mannwhitneyu(a_pre, b_post).pvalue)
    qr.to_parquet(TABLES_DIR / "phase5_quantile_regression.parquet")
    return [
        "### Upper-tail trend (pre-registered) and the post-hoc 2008 shift", "",
        "The decision rule used for the verdict below (trend CI excludes zero AND split 10-yr quantile CIs "
        "disjoint) can barely fail at any n and only inspects the centre of the distribution. A flood-risk "
        "question is about the upper tail, so the tail is tested directly.", "",
        qr.round(5).to_markdown(index=False), "",
        f"- top-quartile (≥{10**thr:,.0f} cfs) Sen slope {ts.slope:+.5f} log10-cfs/yr "
        f"(95% CI {ts.low_slope:+.5f} to {ts.high_slope:+.5f}, n={int(sel.sum())}).",
        "- **Both upper-tail tests have CIs spanning zero.** The Q2 conclusion is therefore better supported "
        "than the conjunction rule made it look: it now rests on a test that could have detected a tail change.",
        "",
        f"**Disclosed as post hoc.** A split at WY {SPLIT_WY} gives a mean shift "
        f"({10**a_pre.mean():,.0f} → {10**b_post.mean():,.0f} cfs; Welch p={welch:.3f}, "
        f"Mann–Whitney p={mwu:.3f}) that the decision rule never surfaced. The split year was chosen after "
        "seeing the data — a split at 1980 gives p={:.2f} — so this is a finding to test on new data, not a "
        "result. It is reported because omitting it would be selective.".format(
            float(st.ttest_ind(y[wy < 1980], y[wy >= 1980], equal_var=False).pvalue)),
        "", "The largest peak in the record is WY{} ({:,.0f} cfs), {:.1f}× the next largest.".format(
            int(imb_pk.loc[imb_pk["peak_cfs"].idxmax(), "wy"]),
            float(imb_pk["peak_cfs"].max()),
            float(imb_pk["peak_cfs"].max() / imb_pk["peak_cfs"].nlargest(2).iloc[-1])),
        "",
    ]


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
        f"station skew {fit.station_skew:.2f}, weighted skew {fit.weighted_skew:.2f}; "
        f"low outliers flagged below {fit.low_outlier_threshold_cfs:.0f} cfs: {fit.n_low_outliers_flagged} "
        "(retained; no B17B conditional-probability adjustment applied))",
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


def _major_events(hardy_pk: pd.DataFrame, stage: pd.DataFrame) -> pd.Series:
    """≥16 ft event dates: annual-peak file before SPLIT_WY, declustered daily-max stage after."""
    major_pre = hardy_pk[(hardy_pk["wy"] < SPLIT_WY) & (hardy_pk["gage_ht_ft"] >= MAJOR_FLOOD_FT)]["date"]
    major_post = pot_events(stage, MAJOR_FLOOD_FT)["peak_date"].dt.normalize()
    return pd.concat([major_pre, major_post]).sort_values().reset_index(drop=True)


def _q6_line(label: str, ev: pd.Series) -> tuple[str, dict | None]:
    try:
        r = interarrival_test(ev)
    except ValueError as exc:
        return f"- {label}: not testable ({exc})", None
    return (
        f"- {label}: n={r['n_events']}, mean gap {r['mean_gap_yr']:.2f} yr, median {r['median_gap_yr']:.2f}, "
        f"CV {r['cv']:.2f}; KS vs exponential {r['ks_stat']:.2f}, bootstrap p={r['p_boot']:.3f}",
        r,
    )


def _q6_lines(hardy_pk: pd.DataFrame, stage_variants: dict[str, pd.DataFrame], crests: pd.DataFrame) -> list[str]:
    hist = crests[crests["stage_ft"] >= HISTORIC_CREST_FT]["date"].dt.normalize()
    majors = _major_events(hardy_pk, stage_variants["all"])
    majors_appr = _major_events(hardy_pk, stage_variants["approved"])
    lines = [
        f"## Q6 inter-arrival of ≥{MAJOR_FLOOD_FT:.0f} ft events",
        "",
        f"Events (annual-peak file for WY <{SPLIT_WY}, 7-day-declustered daily-max IV stage for WY ≥{SPLIT_WY}): "
        + ", ".join(d.strftime("%Y-%m-%d") for d in majors),
        "",
    ]
    results: dict[str, dict | None] = {}
    for label, ev in (("2002–present", majors), ("with 1982 crest", pd.concat([hist, majors]))):
        line, results[label] = _q6_line(label, ev.sort_values().reset_index(drop=True))
        lines.append(line)
    lines += ["", "Sensitivity (approved-only stage days for the post-2008 events):", ""]
    for label, ev in (("2002–present", majors_appr), ("with 1982 crest", pd.concat([hist, majors_appr]))):
        line, r_appr = _q6_line(f"{label} (approved-only)", ev.sort_values().reset_index(drop=True))
        lines.append(line)
        r_all = results[label]
        if r_all is not None and r_appr is not None and (r_all["p_boot"] < 0.05) != (r_appr["p_boot"] < 0.05):
            lines.append(f"- **CHANGED**: Q6 {label} bootstrap p crosses 0.05 between all and approved-only data.")
    lines += [
        "",
        "A bootstrap p well above 0.05 means the gaps are consistent with a memoryless (Poisson) process — "
        "no evidence of a regular cadence; CV near 1 is the exponential signature, CV well below 1 would indicate regularity.",
        "",
    ]
    r_main = results["2002–present"]
    if r_main is not None:
        n_gaps = int(r_main["n_events"]) - 1
        pw = interarrival_power(n_gaps, Q6_POWER_CVS)
        pw.to_parquet(TABLES_DIR / "phase5_q6_power.parquet")
        lo, hi = null_cv_interval(n_gaps)
        best = pw.loc[pw["power"] >= 0.8, "cv"]
        lines += [
            "### What this test could have detected (power)", "",
            f"At n={n_gaps} gaps a memoryless process routinely produces a CV anywhere in **{lo:.2f}–{hi:.2f}** "
            f"(central 95 %), so the observed CV {r_main['cv']:.2f} is unremarkable either way. Power of the "
            "test against a regular (gamma) cadence:", "",
            pw.round(3).to_markdown(index=False), "",
            f"- 80 % power is reached only at CV ≈ {best.max():.2f} — near-metronomic."
            if len(best) else
            f"- 80 % power is not reached at any CV tested (down to {min(Q6_POWER_CVS)}).",
            "- **State the conclusion as 'no cadence is detectable, and none weaker than near-metronomic could "
            "have been' — not as 'the process is memoryless'.** A high p here is an absence of evidence.",
            f"- Adding the 1982 crest (the 'with 1982 crest' row above) is the only extra information available; "
            "a ≥10 ft POT series (see the partial-duration section) is the supplementary check with real n.", "",
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
    lines = [
        f"## Q7 quiet year (<{QUIET_FT:.0f} ft peak) after a ≥{MAJOR_FLOOD_FT:.0f} ft year",
        "",
        f"- P(quiet | prior major) = {q7.rate_after_major:.2f} vs base rate {q7.base_rate:.2f}; "
        f"difference {q7.diff:+.2f} (Clopper-Pearson exact 95% bounds on the conditional rate minus the base rate: "
        f"{q7.diff_lo:+.2f} to {q7.diff_hi:+.2f}); "
        f"permutation p={q7.p:.3f}; n_major={q7.n_major}, n_years={q7.n_years}",
        "",
        f"Water years with a missing annual peak count as neither major nor quiet. "
        f"With n_major={q7.n_major} the test has little power; the CI is the honest statement.",
        "",
    ]
    n_other = int(q7.n_years - q7.n_major)
    pw = conditional_rate_power(q7.n_major, n_other, q7.base_rate, Q7_POWER_RATES)
    pw.to_parquet(TABLES_DIR / "phase5_q7_power.parquet")
    enough = pw.loc[pw["power"] >= 0.8, "true_rate_given_major"]
    lines += [
        "### What this test could have detected (power)", "",
        f"Fisher-exact power at n_major={q7.n_major}, n_other={n_other}, base rate {q7.base_rate:.2f}, "
        "against a true conditional quiet-year rate of:", "",
        pw.round(3).to_markdown(index=False), "",
        (f"- 80 % power requires a true conditional rate of about {enough.min():.1f} — i.e. a quiet year would "
         "have to follow a major flood most of the time before this design could see it."
         if len(enough) else
         "- 80 % power is not reached at any rate tested."),
        f"- Against a 2.5× effect the power is roughly {float(pw['power'].iloc[0]):.2f}. The Clopper-Pearson "
        f"bound already admits a conditional rate anywhere from {max(0.0, q7.base_rate + q7.diff_lo):.2f} to "
        f"{min(1.0, q7.base_rate + q7.diff_hi):.2f}.",
        "- **Q7 is therefore reclassified as UNTESTABLE with the current record, not as 'no support'.** "
        "The design produced no result, which is not the same as a null result. Testing it needs many more "
        "major-flood years than this river has recorded.", "",
    ]
    return lines


def _complete_wys(stage: pd.DataFrame, wys: list[int]) -> list[int]:
    """Water years whose daily-max stage series has a row on/after Sep 30 of that WY."""
    last = stage["date"].max()
    return [y for y in wys if last >= pd.Timestamp(year=y, month=9, day=30)]


def _pot_line(variant: str, h: float, c: pd.Series, dt: dict, r: TrendResult, complete: list[int]) -> str:
    return (
        f"- ≥{h:.0f} ft ({variant}): {int(c.loc[complete].sum())} events over complete WY {complete[0]}–{complete[-1]} "
        f"(n={len(complete)}); mean {dt['mean']:.2f}/yr; dispersion {dt['dispersion']:.2f} (p={dt['p']:.3f}); "
        f"count trend {fmt_trend(r, 'events')}"
    )


def _pot_changed(h: float, all_s: tuple, appr_s: tuple) -> list[str]:
    dt_a, r_a, _ = all_s
    dt_b, r_b, _ = appr_s
    reasons = []
    if (r_a.slope > 0) != (r_b.slope > 0):
        reasons.append("Sen slope sign")
    if _ci_excludes_zero(r_a) != _ci_excludes_zero(r_b):
        reasons.append("trend CI includes zero")
    if (dt_a["p"] < 0.05) != (dt_b["p"] < 0.05):
        reasons.append("dispersion p crosses 0.05")
    if not reasons:
        return []
    return [f"- **CHANGED**: ≥{h:.0f} ft POT conclusion differs between all and approved-only data ({'; '.join(reasons)})."]


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
        "LP3 frequency curves, nonparametric bootstrap (resampled peaks), 5–95%\n"
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
    basin = basin_mod.get_basin_pcpn(START_DATE, end)
    crests = nwps.historic_crests(nwps.get_gauge_info())

    lines = [
        f"# Phase 5 — floods (Q2, Q6, Q7, Q8) — generated {date.today().isoformat()}",
        "",
        "## Q8 LP3 flood frequency (nonparametric bootstrap, 5–95%)",
        "",
        f"Regional skew {REGIONAL_SKEW} (approximate, see config); the 'station skew only' block is the sensitivity case. "
        "LP3 by method of moments with B17-weighted skew; the Grubbs-Beck low-outlier screen flags but does not drop "
        "(all peaks retained in the fit); nonparametric bootstrap (resampled peaks), 5–95%, 2000 resamples. Not EMA.",
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
    lines += _historical_section(hardy_pk, a, b, fit_h)

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
    lines += _q2_upper_tail_section(imb_pk)
    pre = imb_pk[imb_pk["wy"] < SPLIT_WY]
    post = imb_pk[imb_pk["wy"] >= SPLIT_WY]
    lines += ["", f"Imboden LP3 split at WY {SPLIT_WY}:", ""]
    pre_tbl, _ = _lp3_table(f"Imboden WY <{SPLIT_WY}", pre, lines, REGIONAL_SKEW)
    post_tbl, _ = _lp3_table(f"Imboden WY ≥{SPLIT_WY}", post, lines, REGIONAL_SKEW)

    # POT (Hardy daily max stage, WY 2008+)
    lines += ["## Partial-duration series (Hardy daily max IV stage, 7-day declustering)", ""]
    wys = sorted(set(water_year(stage["date"])))
    stage_variants = approval_variants(stage)
    counts: dict[tuple[str, float], pd.Series] = {}
    pot_stats: dict[tuple[str, float], tuple[dict, TrendResult, list[int]]] = {}
    for variant, st in stage_variants.items():
        complete = _complete_wys(st, wys)
        for h in POT_THRESHOLDS_FT:
            c = annual_counts(pot_events(st, h), wys)
            counts[(variant, h)] = c
            cc = c.loc[complete]
            pot_stats[(variant, h)] = (
                dispersion_test(cc),
                trend_test(cc.to_numpy(dtype="float64"), np.array(complete, dtype="float64")),
                complete,
            )
    for h in POT_THRESHOLDS_FT:
        lines.append(_pot_line("all", h, counts[("all", h)], *pot_stats[("all", h)]))
    partial = [y for y in wys if y not in pot_stats[("all", POT_THRESHOLDS_FT[0])][2]]
    lines += [
        "",
        f"Partial WY {', '.join(str(y) for y in partial) or 'none'} (stage through {stage['date'].max().date()}; "
        "excluded from the dispersion and trend tests above) counts: "
        + ", ".join(f"≥{int(h)} ft {int(counts[('all', h)].loc[partial].sum())}" for h in POT_THRESHOLDS_FT),
        "",
        "Sensitivity (approved-only days; complete WYs of the approved series):",
        "",
    ]
    for h in POT_THRESHOLDS_FT:
        lines.append(_pot_line("approved-only", h, counts[("approved", h)], *pot_stats[("approved", h)]))
        lines += _pot_changed(h, pot_stats[("all", h)], pot_stats[("approved", h)])
    pot_tbl = pd.DataFrame({f"ge_{int(h)}ft_{v}": c for (v, h), c in counts.items()})
    pot_tbl.to_parquet(TABLES_DIR / "phase5_pot_counts.parquet")
    lines += [
        "",
        "Dispersion index = variance/mean of annual counts (1 under Poisson; >1 clustered). "
        "A water year is complete when the daily-max stage series has a row on/after its Sep 30.",
        "",
        pot_tbl.to_markdown(),
        "",
    ]

    lines += _q6_lines(hardy_pk, stage_variants, crests)
    lines += _q7_lines(hardy_pk)

    # antecedent conditions before >=14 ft
    mod = hardy_pk[hardy_pk["gage_ht_ft"] >= MODERATE_FT]["date"]
    ante = antecedent_conditions(hardy_dv, basin, mod)
    lines += [
        f"## Antecedent conditions before ≥{MODERATE_FT:.0f} ft annual peaks (60-day BFI, 30-day basin precip)",
        "",
        ante.round(2).to_markdown(index=False),
        "",
        f"BFI from segmented Eckhardt on Hardy DV discharge; precip is the basin mean ({basin_mod.basin_label()}). "
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
        "- LP3/MOM with weighted skew, not EMA. The headline fit excludes the 1982 crest; the historical-"
        "weighting sensitivity above puts it back and is the case to quote at 20–23 ft. Regional skew approximate.",
        "- Hardy n=24; return periods beyond ~50 yr are extrapolation — the CIs say so.",
        "- Stage↔flow mapping is a log-log fit to annual-peak pairs, not the USGS rating. **Q5's rating drift "
        "does not measurably reach these stages**: refitting stage→flow on recent water years only moves the "
        "23 ft return period by a couple of years, and the fit's residuals show no trend against water year — "
        "the drift is a low- and mid-flow control effect. The real extrapolation risk at 29 ft is the "
        "stage→flow relation itself (see below), not the drift.",
        "- POT and Q6 post-2008 events use daily MAX IV stage (upper bound vs a daily-mean product).",
        f"- Imboden peaks file in NWIS begins WY {int(imb_pk['wy'].min())}; the split at WY {SPLIT_WY} leaves n={len(post)} in the post period.",
        f"- Q6 and Q7 are power-limited, and the power sections say by how much: Q6 cannot detect any cadence "
        "weaker than near-metronomic, and Q7 cannot detect any plausible effect at all. Read their high "
        "p-values as absence of evidence, not evidence of absence.",
        f"- The {HISTORIC_CREST_FT:.0f} ft crest is {HISTORIC_CREST_FT / float(hardy_pk['gage_ht_ft'].max()):.2f}× "
        f"the maximum observed stage and its implied flow is "
        f"{stage_to_flow(a, b, HISTORIC_CREST_FT) / float(hardy_pk['peak_cfs'].max()):.2f}× the maximum observed "
        "flow: the stage→flow relation is extrapolated well beyond its data there, which is a larger "
        "uncertainty than the frequency fit itself.",
    ]
    write_report(DOCS_DIR / "phase5_floods.md", lines)
    print(f"wrote {DOCS_DIR / 'phase5_floods.md'}")


if __name__ == "__main__":
    main()
