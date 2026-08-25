"""Phase 4 exit artifact: docs/phase4_baseflow.md (Q1, Q4, Q5).

Q1 primary series is the Mammoth Spring vent gauge (07069190, DV 1981->present,
no gaps) because the spring IS the river's base flow and Hardy's own record is
WY 2002+ only. Hardy min7 is reported as the secondary series.
"""
from datetime import date

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import statsmodels.api as sm
from matplotlib.ticker import MaxNLocator, NullFormatter, ScalarFormatter
import pandas as pd

from spring_river.analysis.common import (
    approval_variants,
    caption,
    fmt_trend,
    sensitivity_lines,
    write_report,
)
from spring_river.config import (
    BASIN_PRECIP_SOURCE,
    BASIN_SOURCES,
    DOCS_DIR,
    FIGURES_DIR,
    MAJOR_FLOOD_FT,
    NWS_CATEGORY_FT,
    PARAM_DISCHARGE,
    PARAM_STAGE,
    RATING_RECENT_SINCE,
    SITE_HARDY,
    SITE_MAMMOTH,
    START_DATE,
    TABLES_DIR,
)
from spring_river.hydro.baseflow import bfi_by_wy
from spring_river.hydro.freq_lp3 import stage_flow_fit
from spring_river.hydro.lowflow import (
    PREDICTORS,
    AttributionFit,
    attribution_table,
    fit_attribution,
    fit_attribution_precip_only,
    ratio_trend,
)
from spring_river.hydro.postflood import (
    PRE_STATE_DAYS,
    RECESSION_SKIP_DAYS,
    matched_comparison,
    paired_summary,
    placebo_distribution,
    skip_day_sensitivity,
)
from spring_river.ingest import basin as basin_mod, field_measurements as fmeas, oni, usgs
from spring_river.ingest.pull_all import IV_START
from spring_river.qa.rating import (
    FIELD_BAND_CFS,
    FIELD_TARGET_CFS,
    field_stage_at_flow,
    flow_percentile_stages,
    loglog_correlation,
    pair_iv,
    rating_shift_at_events,
    rating_table,
    stage_at_flow,
)
from spring_river.stats.trends import MIN_N, TrendResult, pettitt, trend_test

BFI_METHODS = ("eckhardt", "lyne_hollick")
PLACEBO_TRIALS = 200
Fit = tuple[pd.DataFrame, AttributionFit]


def _trend_or_none(x: np.ndarray, t: np.ndarray) -> TrendResult | None:
    ok = ~np.isnan(x) & ~np.isnan(t)
    return trend_test(x[ok], t[ok]) if ok.sum() >= MIN_N else None


def _fmt_or_short(r: TrendResult | None, unit: str, n: int) -> str:
    return fmt_trend(r, unit) if r is not None else f"not tested (n={n} < {MIN_N})"


def _pettitt_result(tbl: pd.DataFrame) -> tuple[int, float, str]:
    m7 = tbl[tbl["complete"]].dropna(subset=["min7_cfs"])
    pt = pettitt(m7["min7_cfs"].to_numpy())
    wy_change = int(m7["wy"].iloc[pt.change_index])
    return wy_change, pt.p, f"after WY {wy_change} (K={pt.k:.0f}, p={pt.p:.3f}, n={pt.n})"


def _pettitt_line(tbl: pd.DataFrame) -> str:
    return _pettitt_result(tbl)[2]


def _pettitt_changed(tbl_all: pd.DataFrame, tbl_appr: pd.DataFrame) -> bool:
    wy_a, p_a, _ = _pettitt_result(tbl_all)
    wy_b, p_b, _ = _pettitt_result(tbl_appr)
    return wy_a != wy_b or (p_a < 0.05) != (p_b < 0.05)


def _coef_line(fit: AttributionFit, k: str) -> str:
    lo, hi = fit.ci[k]
    return f"{fit.coef[k]:.4f} (95% CI {lo:.4f} to {hi:.4f})"


def _coef_changed(a: AttributionFit, b: AttributionFit, k: str) -> bool:
    def incl0(f: AttributionFit) -> bool:
        lo, hi = f.ci[k]
        return lo <= 0 <= hi

    return (a.coef[k] > 0) != (b.coef[k] > 0) or incl0(a) != incl0(b)


def _fit_section(
    label: str, dv_q: pd.DataFrame, basin: pd.DataFrame, oni_df: pd.DataFrame, lines: list[str]
) -> dict[str, Fit]:
    out: dict[str, Fit] = {}
    for variant, q in approval_variants(dv_q).items():
        tbl = attribution_table(q, basin, oni_df)
        out[variant] = (tbl, fit_attribution(tbl))
    tbl, fit = out["all"]
    tbl_appr, fit_appr = out["approved"]
    tbl.to_parquet(TABLES_DIR / f"phase4_attribution_{label.lower()}.parquet")
    lines += [
        f"### {label}",
        "",
        f"- Series: {caption(f'USGS DV {SITE_MAMMOTH if label == 'Mammoth' else SITE_HARDY} discharge', dv_q)}",
        f"- min7 raw trend (log-cfs): {fmt_trend(fit.min7_trend, 'log-cfs')}",
        f"- Pettitt change-point on min7: {_pettitt_line(tbl)}",
        f"- OLS log(min7) ~ {' + '.join(PREDICTORS)} (HC3): R²={fit.r2:.2f}, n={fit.n}",
    ]
    for k in PREDICTORS:
        lines.append(f"  - {k}: {_coef_line(fit, k)}")
    lines += [
        f"- **Residual trend (non-climatic component): {fmt_trend(fit.residual_trend, 'log-cfs')}**",
        "",
        "Sensitivity (approved-only re-run of the full chain):",
        *sensitivity_lines("residual trend", fit.residual_trend, fit_appr.residual_trend),
        *sensitivity_lines("min7 raw trend", fit.min7_trend, fit_appr.min7_trend),
        f"- Pettitt (approved-only): {_pettitt_line(tbl_appr)}",
        *(["- **CHANGED**: Pettitt change-point year or significance differs between all and approved-only."]
          if _pettitt_changed(tbl, tbl_appr) else []),
        f"- OLS (approved-only): R²={fit_appr.r2:.2f}, n={fit_appr.n}",
    ]
    for k in PREDICTORS:
        lines.append(f"  - {k}: {_coef_line(fit_appr, k)}")
        if _coef_changed(fit, fit_appr, k):
            lines.append(f"  - **CHANGED**: {k} coefficient sign or CI-includes-zero differs between all and approved-only.")
    lines.append("")
    return out


def _bfi_section(series: dict[str, pd.DataFrame], lines: list[str]) -> None:
    lines += ["### BFI trend (gap-segmented Eckhardt; Lyne-Hollick check)", ""]
    for label, q in series.items():
        for method in BFI_METHODS:
            results = {}
            for variant, qv in approval_variants(q).items():
                s = bfi_by_wy(qv, method=method).dropna()
                results[variant] = trend_test(s.to_numpy(), s.index.to_numpy(dtype="float64"))
            lines.append(f"- {label} BFI ({method}): {fmt_trend(results['all'], 'BFI')}")
            lines += ["  " + ln for ln in sensitivity_lines(f"{label} BFI ({method})", results["all"], results["approved"])]
    lines += [
        "",
        "**What a null BFI trend is not.** BFI is a ratio, and at a spring-fed river it sits near 1, so it is "
        "nearly blind to a change in the absolute base-flow *rate*: base flow and total flow can both rise "
        "together and leave the ratio flat. These nulls are reported as stated, but they are **not evidence "
        "against a base-flow change** and must not be cited as corroboration of one. The min7 series and the "
        "Hardy/Mammoth ratio above carry that question.", ""]


def _residuals(tbl: pd.DataFrame, fit: AttributionFit) -> pd.DataFrame:
    d = tbl[tbl["complete"]].dropna(subset=["min7_cfs", *PREDICTORS])
    d = d[d["min7_cfs"] > 0]
    pred = fit.coef["const"] + sum(fit.coef[k] * d[k] for k in PREDICTORS)
    return d.assign(resid=np.log(d["min7_cfs"]) - pred)


def _both_caption(series: dict[str, pd.DataFrame]) -> str:
    return "; ".join(
        caption(f"USGS DV {SITE_MAMMOTH if label == 'Mammoth' else SITE_HARDY} discharge", q)
        for label, q in series.items()
    )


def _min7_figure(fits: dict[str, dict[str, Fit]], series: dict[str, pd.DataFrame]) -> None:
    fig, axes = plt.subplots(2, 1, figsize=(11, 7), sharex=True)
    for label, color in (("Mammoth", "C0"), ("Hardy", "C1")):
        tbl, _ = fits[label]["all"]
        axes[0].plot(tbl["wy"], tbl["min7_cfs"], marker="o", color=color, label=f"{label} min7")
    axes[0].set_ylabel("7-day low flow (cfs)")
    axes[0].legend()
    tbl, fit = fits["Mammoth"]["all"]
    d = _residuals(tbl, fit)
    r = fit.residual_trend
    axes[1].axhline(0, color="k", lw=0.5)
    axes[1].plot(d["wy"], d["resid"], marker="o", color="C0", lw=0.8, label="OLS residual")
    axes[1].plot(d["wy"], r.intercept + r.slope * d["wy"], "r--", label="Sen residual trend")
    axes[1].set_ylabel("Mammoth OLS residual (log-cfs)")
    axes[1].set_xlabel("water year")
    axes[1].legend()
    fig.suptitle(f"Q1 base-flow attribution\n{_both_caption(series)}", fontsize=8)
    fig.tight_layout(rect=(0, 0, 1, 0.94))
    fig.savefig(FIGURES_DIR / "phase4_min7_trend.png", dpi=150)
    plt.close(fig)


def _rating_section(end: str, majors: pd.Series, dv_q: pd.DataFrame, peaks: pd.DataFrame, lines: list[str]) -> None:
    iv_q = usgs.get_iv(SITE_HARDY, PARAM_DISCHARGE, IV_START, end)
    iv_h = usgs.get_iv(SITE_HARDY, PARAM_STAGE, IV_START, end)
    pairs = pair_iv(iv_q, iv_h)
    sf = stage_at_flow(pairs)
    sf.to_parquet(TABLES_DIR / "phase4_rating_drift.parquet")
    sf_appr = stage_at_flow(pairs[pairs["approved"]].reset_index(drop=True))
    shifts = rating_shift_at_events(pairs, majors)
    no_data = shifts.groupby("event_date")[["n_before", "n_after"]].sum().sum(axis=1) == 0
    dropped = [d for d, flag in no_data.items() if flag]
    shifts = shifts[~shifts["event_date"].isin(dropped)]
    lines += [
        "## Q5 rating drift (stage at fixed discharge, Hardy IV pairs)",
        "",
        f"Pairs: {caption(f'USGS IV {SITE_HARDY} discharge+stage', pairs.rename(columns={'datetime': 'date'}))}; "
        f"n={len(pairs)} matched 15-min pairs.",
        "",
        "Stage at each target flow is a local log-linear fit (stage = a + b·log10 q) over pairs within ±20% of the "
        "target, evaluated at 400 and 1000 cfs, per water year (min 30 pairs per band).",
        "",
        sf.pivot(index="wy", columns="flow_cfs", values="stage_at_flow_ft").round(2).to_markdown(),
        "",
        f"Shift across ≥{MAJOR_FLOOD_FT:.0f} ft events: same local fit on pairs in the 365 days before vs the "
        "365 days after each event date (n_before/n_after = pairs in each band).",
        "",
        shifts.round(2).to_markdown(index=False),
        "",
    ]
    for d in dropped:
        note = f"Event {d.date()} omitted from the shift table: no IV pairs within ±365 days (predates IV_START {IV_START})."
        print(note)
        lines += [note, ""]
    for f in sf["flow_cfs"].unique():
        res = {}
        for variant, frame in (("all", sf), ("approved", sf_appr)):
            s = frame[frame["flow_cfs"] == f].dropna(subset=["stage_at_flow_ft"])
            res[variant] = (_trend_or_none(s["stage_at_flow_ft"].to_numpy(), s["wy"].to_numpy(dtype="float64")), len(s))
        lines.append(f"- stage at {f:.0f} cfs: {_fmt_or_short(res['all'][0], 'ft', res['all'][1])}")
        if res["all"][0] is not None and res["approved"][0] is not None:
            lines += ["  " + ln for ln in sensitivity_lines(f"stage at {f:.0f} cfs", res["all"][0], res["approved"][0])]
        else:
            lines.append(f"  - approved-only: {_fmt_or_short(res['approved'][0], 'ft', res['approved'][1])}")
    _rating_figure(sf, majors, iv_h)
    lines += ["", "![rating](../reports/figures/phase4_rating_drift.png)", ""]
    _field_measurement_section(SITE_HARDY, lines)
    _measured_vs_computed_section(SITE_HARDY, dv_q, lines)
    pairs_cap = caption(f"USGS IV {SITE_HARDY} discharge+stage", pairs.rename(columns={"datetime": "date"}))
    rt, fit, fp = _lookup_tables(pairs, dv_q, peaks)
    _lookup_lines(rt, fit, fp, pairs_cap, lines)
    _rating_curve_figure(pairs, rt, pairs_cap)


def _lookup_tables(pairs: pd.DataFrame, dv_q: pd.DataFrame, peaks: pd.DataFrame) -> tuple[pd.DataFrame, dict, pd.DataFrame]:
    """Write phase4_rating_table (whole_record + recent variants) and phase4_rating_fit parquets."""
    rt = pd.concat(
        [
            rating_table(pairs).assign(variant="whole_record"),
            rating_table(pairs, since=RATING_RECENT_SINCE).assign(variant="recent"),
        ],
        ignore_index=True,
    )
    rt.to_parquet(TABLES_DIR / "phase4_rating_table.parquet")
    a, b, r2 = stage_flow_fit(peaks)
    fit = {**loglog_correlation(pairs), "peak_fit_a": a, "peak_fit_b": b, "peak_fit_r2": r2,
           "peak_n": int(peaks.dropna(subset=["peak_cfs", "gage_ht_ft"]).shape[0]), "recent_since": RATING_RECENT_SINCE}
    pd.DataFrame([fit]).to_parquet(TABLES_DIR / "phase4_rating_fit.parquet")
    fp = flow_percentile_stages(pairs, dv_q["value"], since=RATING_RECENT_SINCE)
    fp.to_parquet(TABLES_DIR / "phase4_rating_percentiles.parquet")
    return rt, fit, fp


def _lookup_lines(rt: pd.DataFrame, fit: dict, fp: pd.DataFrame, pairs_cap: str, lines: list[str]) -> None:
    wide = rt.pivot(index="stage_ft", columns="variant", values=["median_cfs", "n_pairs"])
    side = pd.DataFrame(
        {
            "stage_ft": wide.index,
            "whole_record_median_cfs": wide[("median_cfs", "whole_record")].to_numpy(),
            "recent_median_cfs": wide[("median_cfs", "recent")].to_numpy(),
            "n_whole": wide[("n_pairs", "whole_record")].to_numpy(),
            "n_recent": wide[("n_pairs", "recent")].to_numpy(),
        }
    )
    lines += [
        "### Stage–discharge lookup",
        "",
        f"Pairs: {pairs_cap}. Median (and IQR in the parquet) of discharge over pairs within ±0.05 ft of each "
        f"stage; `recent` = pairs from {RATING_RECENT_SINCE} (WY 2024+); NaN where fewer than 20 pairs.",
        "",
        side.to_markdown(index=False, floatfmt=(".1f", ".0f", ".0f", ".0f", ".0f")),
        "",
        f"Correlation: Pearson r of log10 stage vs log10 discharge = {fit['r_loglog']:.4f}; Spearman rho = "
        f"{fit['spearman']:.4f}; n={fit['n']} pairs. Annual-peak log-log fit log10 Q = {fit['peak_fit_a']:.4f} + "
        f"{fit['peak_fit_b']:.4f}·log10 H (R²={fit['peak_fit_r2']:.3f}, n={fit['peak_n']} peaks).",
        "",
        f"Flow percentile → stage (Hardy DV discharge percentiles; median stage of recent pairs within ±3% of each flow):",
        "",
        fp.round(2).to_markdown(index=False),
        "",
        "![rating_curve](../reports/figures/phase4_rating_curve.png)",
        "",
    ]


def _rating_curve_figure(pairs: pd.DataFrame, rt: pd.DataFrame, pairs_cap: str) -> None:
    fig, ax = plt.subplots(figsize=(9, 6))
    p = pairs[(pairs["q_cfs"] > 0) & (pairs["stage_ft"] > 0)]
    hb = ax.hexbin(p["q_cfs"], p["stage_ft"], gridsize=70, xscale="log", yscale="log", bins="log", cmap="Greys", mincnt=1)
    fig.colorbar(hb, ax=ax, label="pairs per cell (log10)")
    for variant, color in (("whole_record", "C0"), ("recent", "C3")):
        d = rt[(rt["variant"] == variant)].dropna(subset=["median_cfs"])
        ax.plot(d["median_cfs"], d["stage_ft"], marker="o", color=color, label=f"{variant} median")
    for name, h in NWS_CATEGORY_FT.items():
        ax.axhline(h, color="grey", lw=0.6, ls=":")
        ax.annotate(f"{name} {h:.0f} ft", (p["q_cfs"].min(), h), fontsize=7, color="grey", va="bottom")
    ax.set_yticks([3, 4, 5, 6, 8, 10, 14, 16, 20])
    ax.yaxis.set_major_formatter(ScalarFormatter())
    ax.yaxis.set_minor_formatter(NullFormatter())
    ax.set_xlabel("discharge (cfs)")
    ax.set_ylabel("stage (ft)")
    ax.legend(loc="lower right")
    ax.set_title(f"Hardy stage–discharge pairs with median rating curves\n{pairs_cap}", fontsize=8)
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / "phase4_rating_curve.png", dpi=150)
    plt.close(fig)


def _rating_figure(sf: pd.DataFrame, majors: pd.Series, iv_h: pd.DataFrame) -> None:
    fig, ax = plt.subplots(figsize=(10, 4))
    for f in sf["flow_cfs"].unique():
        s = sf[sf["flow_cfs"] == f]
        ax.plot(s["wy"], s["stage_at_flow_ft"], marker="o", label=f"{f:.0f} cfs")
    for d in majors:
        ax.axvline(d.year + int(d.month >= 10), color="grey", lw=0.5, ls=":")
    ax.xaxis.set_major_locator(MaxNLocator(integer=True))
    ax.set_ylabel("stage (ft)")
    ax.set_xlabel("water year")
    ax.legend()
    ax.set_title(
        f"Q5 stage at fixed discharge; dotted = ≥{MAJOR_FLOOD_FT:.0f} ft flood WY\n"
        f"{caption(f'USGS IV {SITE_HARDY} stage', iv_h.rename(columns={'datetime': 'date'}))}",
        fontsize=9,
    )
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / "phase4_rating_drift.png", dpi=150)
    plt.close(fig)


def _postflood_section(
    series: dict[str, pd.DataFrame], basin: pd.DataFrame, majors: pd.Series, lines: list[str]
) -> None:
    lines += [
        "## Q4 post-flood base flow vs matched non-flood years",
        "",
        f"Post window: 6 months of Eckhardt base flow starting {RECESSION_SKIP_DAYS} days after the event (past the "
        f"recession limb). Controls: the 3 non-flood years (no ≥{MAJOR_FLOOD_FT:.0f} ft event within ±1 yr) closest in "
        f"standardized distance on same-calendar post-window precip AND antecedent base flow "
        f"(mean over the {PRE_STATE_DAYS} days before the event date). `pre_bf_cfs` / `matched_pre_bf_cfs` show the "
        "antecedent match; precip windows with < 90 % day coverage are NaN and drop out of the match distance.",
        "",
    ]
    fig, axes = plt.subplots(1, len(series), figsize=(11, 4), sharey=True)
    for ax, (label, q) in zip(np.atleast_1d(axes), series.items()):
        cmp = matched_comparison(q, basin, majors)
        cmp.to_parquet(TABLES_DIR / f"phase4_postflood_{label.lower()}.parquet")
        s = paired_summary(cmp)
        s_appr = paired_summary(matched_comparison(q[q["approved"]].reset_index(drop=True), basin, majors))
        lines += [
            f"### {label}",
            "",
            f"Series: {caption(f'USGS DV {SITE_MAMMOTH if label == 'Mammoth' else SITE_HARDY} discharge', q)}",
            "",
            cmp.round(1).to_markdown(index=False),
            "",
            f"- mean post-flood base-flow difference: {s['mean_diff_pct']:.1f}% "
            f"(bootstrap 95% CI {s['lo']:.1f} to {s['hi']:.1f}); n={s['n']} events; "
            f"{s['n_unique_controls']} unique control years",
            f"- approved-only: {s_appr['mean_diff_pct']:.1f}% "
            f"(bootstrap 95% CI {s_appr['lo']:.1f} to {s_appr['hi']:.1f}); n={s_appr['n']} events; "
            f"{s_appr['n_unique_controls']} unique control years",
            "- CI reflects event-to-event variation only; matching uncertainty and control-year reuse are not "
            "propagated — descriptive, not causal.",
            "",
        ]
        ax.axhline(0, color="k", lw=0.5)
        ax.bar(cmp["event_date"].dt.strftime("%Y-%m"), cmp["diff_pct"], color="C3")
        ax.set_title(f"{label}: post-flood vs matched (mean {s['mean_diff_pct']:.0f}%)", fontsize=9)
        ax.set_ylabel("base-flow difference (%)")
        ax.tick_params(axis="x", labelrotation=45, labelsize=8)
    fig.suptitle(
        f"Q4 6-month post-flood Eckhardt base flow (window starts {RECESSION_SKIP_DAYS} d after event) "
        f"vs 3 non-flood years matched on precip + antecedent base flow\n"
        f"{_both_caption(series)}; events from USGS peaks {SITE_HARDY}",
        fontsize=8,
    )
    fig.tight_layout(rect=(0, 0, 1, 0.9))
    fig.savefig(FIGURES_DIR / "phase4_postflood.png", dpi=150)
    plt.close(fig)
    lines += ["![postflood](../reports/figures/phase4_postflood.png)", ""]
    _q4_placebo_section(series, basin, majors, lines)


def _hardy_ratio_section(fits: dict[str, dict[str, Fit]], series: dict[str, pd.DataFrame],
                         oni_df: pd.DataFrame) -> list[str]:
    """Phase 8 (review.md item 5): the Hardy low-flow rise, led by the evidence
    that needs no precipitation model at all."""
    tbl_h = fits["Hardy"]["all"][0]
    tbl_m = fits["Mammoth"]["all"][0]
    t, s = ratio_trend(tbl_h[tbl_h["complete"]], tbl_m)
    s.to_parquet(TABLES_DIR / "phase4_hardy_mammoth_ratio.parquet")
    pt = pettitt(s["log_ratio"].to_numpy(dtype="float64"))
    pt_wy = int(s["wy"].iloc[pt.change_index])

    rows = []
    for src in BASIN_SOURCES:
        b = basin_mod.get_basin_pcpn(START_DATE, series["Hardy"]["date"].max().date().isoformat(), source=src)
        for label, q in series.items():
            f = fit_attribution_precip_only(attribution_table(q, b, oni_df))
            r = f.residual_trend
            rows.append({"series": label, "basin_source": src, "n": f.n, "r2": f.r2,
                         "resid_slope": r.slope, "lo": r.slope_lo, "hi": r.slope_hi, "p": r.p})
    po = pd.DataFrame(rows)
    po.to_parquet(TABLES_DIR / "phase4_precip_only_fits.parquet")
    hardy_po = po[po["series"] == "Hardy"]
    n_sig = int((hardy_po["lo"] > 0).sum())

    return [
        "## Q1c Hardy low-flow rise: evidence without a precipitation model", "",
        "The published Hardy residual is source-dependent, which was reported as a reason not to call it a "
        "finding. Two checks say otherwise, and neither depends on a gridded precipitation product.", "",
        "### Hardy against Mammoth Spring (no precipitation model)", "",
        "Mammoth Spring is the best available climate control for Hardy: the same recharge climate, absorbing "
        "precipitation, ENSO, PET and any gridded-precip bias at once. If Hardy's rise were climate, it would "
        "vanish against Mammoth.", "",
        f"- **log(Hardy min7 / Mammoth min7) trend: {fmt_trend(t, 'log-ratio')}**",
        f"- Pettitt change-point on the log ratio: after WY {pt_wy} (K={pt.k:.0f}, p={pt.p:.3f}, n={pt.n})",
        f"- the ratio rises by a factor {float(np.exp(t.slope * (s['wy'].max() - s['wy'].min()))):.2f} across "
        f"WY {int(s['wy'].min())}–{int(s['wy'].max())}.", "",
        "### Precip-only fits (the ONI term dropped)", "",
        "At n≈24 the never-significant ONI regressor costs a degree of freedom for nothing. Dropping it:", "",
        po.round(4).to_markdown(index=False), "",
        f"- Hardy's residual rise has a CI excluding zero on {n_sig} of {len(hardy_po)} basin sources; "
        "the source-dependence of the published figure was one weak regressor, not a fragile signal.",
        "- **The rise is therefore reported as a finding, not as a source artefact.** Its cause is Q1c/Q5: the "
        "channel at Hardy degraded (see the field-measurement trend below), and the reach gains water the "
        "spring alone does not account for.", "",
    ]


def _field_measurement_section(site: str, lines: list[str]) -> None:
    """Phase 8 (review.md item 6): stage at a fixed discharge from FIELD
    measurements — neither side rating-derived, so this answers the
    circularity attack on the IV-based Q5 figure."""
    fm = fmeas.get_field_measurements(site)
    pairs = fmeas.measured_pairs(fm)
    ch = fmeas.get_channel_measurements(site)
    loc = fmeas.get_monitoring_location(site)
    fsf = field_stage_at_flow(pairs)
    fsf.to_parquet(TABLES_DIR / "phase4_field_stage_at_flow.parquet")
    pairs.to_parquet(TABLES_DIR / "phase4_field_pairs.parquet")

    lines += [
        "### Field-measured stage at fixed discharge (independent of the rating)", "",
        f"Source: USGS OGC API `field-measurements` and `channel-measurements` "
        f"(`api.waterdata.usgs.gov/ogcapi/v0`), site {site}; {len(fm)} readings over "
        f"{pairs['field_visit_id'].nunique()} visits with both a measured discharge and a measured stage, "
        f"{pairs['time'].min().date()}–{pairs['time'].max().date()}; {len(ch)} channel surveys.", "",
        "Both numbers in each pair are *measured at the visit* — the discharge by wading or ADCP, not computed "
        "from the stage — so a decline here cannot be rating drift. Stage is normalised to "
        f"{FIELD_TARGET_CFS:.0f} cfs along a single log-linear fit through the "
        f"{FIELD_BAND_CFS[0]:.0f}–{FIELD_BAND_CFS[1]:.0f} cfs band, then averaged per water year.", "",
    ]
    if len(fsf) >= MIN_N:
        t = trend_test(fsf["stage_at_flow_ft"].to_numpy(dtype="float64"),
                       fsf["wy"].to_numpy(dtype="float64"))
        lines += [
            f"- **field-measured stage at {FIELD_TARGET_CFS:.0f} cfs: {fmt_trend(t, 'ft')}**",
            f"- water years covered: {int(fsf['wy'].min())}–{int(fsf['wy'].max())} "
            f"({len(fsf)} with a qualifying visit; {int(fsf['n_visits'].sum())} visits).",
            f"- total fall over the record: {float(fsf['stage_at_flow_ft'].iloc[0] - fsf['stage_at_flow_ft'].iloc[-1]):.2f} ft.",
            "- This is steeper than the IV-derived figure and four years longer, and it brackets the 2006-09-23 "
            "event the shift table has to omit. It retires both the 'IV-derived only' limitation and the "
            "'events before IV_START have no pairs' gap: **the channel really degraded; the rating followed it.**",
            "",
            fsf.round(3).to_markdown(index=False), "",
        ]
    else:
        lines += [f"- not tested: only {len(fsf)} water years have a qualifying visit.", ""]
    if len(loc):
        r = loc.iloc[0]
        lines += [
            "### Gauge datum", "",
            f"- current datum: {r['altitude']:.2f} ft {r['vertical_datum']} "
            f"(±{r['altitude_accuracy']}, {r['altitude_method_name']}), from the `monitoring-locations` endpoint.",
            "- The datum elevation carries **two revisions** (340.91→342.49 ft before Dec 2022; 342.49→342.73 ft "
            "between Dec 2022 and Dec 2024 — the value above). Both are post-2022 bookkeeping of the datum "
            "elevation: **no site move, and nothing at WY2008**, so neither can explain the low-flow step. "
            "`time-series-revisions` returns no rows for this site.", "",
        ]


def _q4_placebo_section(series: dict[str, pd.DataFrame], basin: pd.DataFrame,
                        majors: pd.Series, lines: list[str]) -> None:
    """Phase 8 (review.md item 3): does the matching pipeline manufacture the
    post-flood effect, and does it survive a later post-window start?"""
    lines += [
        "### Placebo and skip-day sensitivity", "",
        f"With n={len(majors)} events, three nearest controls each and heavy control-year reuse, the procedure "
        "itself may produce an effect. The placebo runs the identical pipeline on random NON-flood pseudo-events "
        "keeping the real events' days-of-year, so what it returns is what 'no flood' looks like through this "
        "machinery. The skip-day sensitivity asks whether the effect is recession water still present in the "
        "post window rather than a change in base flow.", "",
    ]
    rows, skips = [], []
    for label, q in series.items():
        p = placebo_distribution(q, basin, majors, n_trials=PLACEBO_TRIALS, seed=0)
        rows.append({"series": label, **{k: p[k] for k in
                     ("real", "mean", "sd", "p95", "frac_ge_real", "corrected", "n_trials")}})
        skips.append(skip_day_sensitivity(q, basin, majors).assign(series=label))
    pl = pd.DataFrame(rows).rename(columns={"mean": "placebo_mean", "sd": "placebo_sd",
                                            "p95": "placebo_p95", "real": "real_diff_pct"})
    sk = pd.concat(skips, ignore_index=True)
    pl.to_parquet(TABLES_DIR / "phase4_postflood_placebo.parquet")
    sk.to_parquet(TABLES_DIR / "phase4_postflood_skip_days.parquet")
    lines += [f"Placebo: {PLACEBO_TRIALS} trials per series, seed 0.", "",
              pl.round(2).to_markdown(index=False), "",
              "Skip-day sensitivity (post window starts this many days after the event):", "",
              sk.round(1).to_markdown(index=False), ""]
    for _, r in pl.iterrows():
        d = sk[sk["series"] == r["series"]].set_index("skip_days")
        far = d.loc[d.index.max()]
        survives = far["lo"] > 0
        lines.append(
            f"- **{r['series']}**: placebo mean {r['placebo_mean']:+.1f}% (sd {r['placebo_sd']:.1f}); "
            f"{r['frac_ge_real']:.1%} of placebo trials reach the real {r['real_diff_pct']:+.1f}%; "
            f"placebo-corrected effect {r['corrected']:+.1f}%. At a {int(d.index.max())}-day skip the effect is "
            f"{far['mean_diff_pct']:+.1f}% (CI {far['lo']:.1f} to {far['hi']:.1f})"
            + ("." if survives else " — the CI spans zero."))
    lines += [
        "",
        "Reading: an effect worth reporting must sit far outside its own placebo distribution AND survive a "
        "later window start. Where the placebo is centred near zero and the effect holds at a long skip, the "
        "result stands and is stronger than the bootstrap CI alone suggests. Where a material fraction of "
        "placebo trials reach the reported figure and the effect decays as the window moves later, part of it "
        "is procedural and part is recession water: report the placebo-corrected value with this sensitivity, "
        "not the raw percentage.", "",
    ]


MEASURED_VS_COMPUTED_ERAS = ((2001, 2007), (2008, 2014), (2015, 2025), (2026, 2026))
LOW_FLOW_CFS = 800.0
# Trailing-precip windows for the Mammoth cross-source check. 365 d is the
# study's convention; a karst spring with a ~188-day recession constant may
# remember rain for longer, so 730 d is the defensible alternative.
CROSS_SOURCE_WINDOWS = (365, 730)


def _mammoth_cross_source_section(dv_q: pd.DataFrame, oni_df: pd.DataFrame, end: str,
                                  lines: list[str]) -> None:
    """Phase 8 (review.md item 7): the Mammoth residual across basin sources
    and trailing-window lengths. '≈0 on all three sources' overstates the
    unanimity — the PRISM fits are consistently, marginally negative."""
    import spring_river.hydro.lowflow as lf
    from spring_river.hydro.lowflow import _daily_precip, _trailing_precip

    rows = []
    for src in BASIN_SOURCES:
        b = basin_mod.get_basin_pcpn(START_DATE, end, source=src)
        daily = _daily_precip(b)
        tbl = attribution_table(dv_q, b, oni_df)
        for w in CROSS_SOURCE_WINDOWS:
            original = lf.TRAILING_DAYS
            try:
                lf.TRAILING_DAYS = w
                cur = [_trailing_precip(daily, d, 7, 0.9) for d in tbl["min7_end_date"]]
                prev = [_trailing_precip(daily, d, 7 + w, 0.9) for d in tbl["min7_end_date"]]
            finally:
                lf.TRAILING_DAYS = original
            # Build the predictor columns on the FULL table (the lists are in
            # its row order), then filter to complete water years.
            d = tbl.assign(p_cur=cur, p_prev=prev)
            d = d[d["complete"]].dropna(subset=["min7_cfs", "p_cur", "p_prev"])
            d = d[d["min7_cfs"] > 0]
            y = np.log(d["min7_cfs"].to_numpy(dtype="float64"))
            X = sm.add_constant(d[["p_cur", "p_prev"]].to_numpy(dtype="float64"))
            res = sm.OLS(y, X).fit(cov_type="HC3")
            t = trend_test(np.asarray(res.resid), d["wy"].to_numpy(dtype="float64"))
            rows.append({"basin_source": src, "window_days": w, "n": t.n, "r2": float(res.rsquared),
                         "resid_slope": t.slope, "lo": t.slope_lo, "hi": t.slope_hi, "p": t.p})
    cs = pd.DataFrame(rows)
    cs.to_parquet(TABLES_DIR / "phase4_mammoth_cross_source.parquet")
    neg = cs[cs["hi"] < 0]
    lines += [
        "### Mammoth residual across basin sources and trailing windows", "",
        "The 365-day predictor window is a convention. A karst spring with a ~188-day recession constant may "
        "remember rain for longer, so each source is refitted at 730 days as well (precip-only, ONI dropped).", "",
        cs.round(5).to_markdown(index=False), "",
        f"- specifications whose CI excludes zero (all on the negative side): {len(neg)} of {len(cs)}"
        + (f" — {', '.join(f'{r.basin_source} at {int(r.window_days)} d (p={r.p:.3f})' for r in neg.itertuples())}."
           if len(neg) else "."),
        "- **Correction to the published wording.** The Mammoth conclusion survives on the primary series, but "
        "'≈0 on all three sources' claims a unanimity the numbers do not support: the PRISM fits are "
        "consistently, marginally negative, and one specification's CI excludes zero. State it that way, with "
        "the same candour applied to Hardy.",
        "- Settling it needs a basin series independent of PRISM's gauge network (Stage IV/MRMS 2002→, Livneh, "
        "nClimGrid-Daily) and a window pre-registered from spring recession or tracer transit rather than "
        "from convention.", "",
    ]


def _measured_vs_computed_section(site: str, dv_q: pd.DataFrame, lines: list[str]) -> None:
    """Phase 8 (review.md item 5): the '~1 % agreement in every era' figure,
    recomputed against same-day daily values and reported WITH its scatter.

    USGS shifts the rating *to* the wading measurements, so close agreement
    proves only that the rating tracks them — this table is reported for
    completeness, not as evidence. The independent evidence is the measured
    stage decline above.
    """
    pairs = fmeas.measured_pairs(fmeas.get_field_measurements(site))
    dv = dv_q.assign(date=pd.to_datetime(dv_q["date"])).set_index("date")["value"]
    p = pairs.assign(day=pairs["time"].dt.normalize())
    p = p.assign(dv_cfs=p["day"].map(dv)).dropna(subset=["dv_cfs"])
    p = p[(p["dv_cfs"] > 0) & (p["q_cfs"] < LOW_FLOW_CFS)]
    p = p.assign(pct=100.0 * (p["q_cfs"] - p["dv_cfs"]) / p["dv_cfs"], year=p["time"].dt.year)
    rows = []
    for lo, hi in MEASURED_VS_COMPUTED_ERAS:
        e = p[(p["year"] >= lo) & (p["year"] <= hi)]
        if e.empty:
            continue
        rows.append({"era": f"{lo}–{hi}" if lo != hi else str(lo), "n": len(e),
                     "mean_pct": float(e["pct"].mean()), "median_pct": float(e["pct"].median()),
                     "sd_pct": float(e["pct"].std(ddof=1)) if len(e) > 1 else float("nan")})
    tbl = pd.DataFrame(rows)
    tbl.to_parquet(TABLES_DIR / "phase4_measured_vs_computed.parquet")
    lines += [
        "### Measured vs computed low flow, by era", "",
        f"Field-measured discharge below {LOW_FLOW_CFS:.0f} cfs against the same day's published daily value "
        f"(n={len(p)} visits). Reported with its scatter: the era means are a few per cent either side of zero "
        "with a standard deviation several times larger, not '~1 % in every era'.", "",
        tbl.round(1).to_markdown(index=False), "",
        "This agreement is **not independent evidence**: USGS shifts the rating to these very measurements, so "
        "close agreement shows only that the rating tracks them. The rating-independent evidence is the "
        "measured-stage decline above and the Hardy/Mammoth ratio in Q1c.", "",
    ]


def _change_point_note(fits: dict[str, dict[str, Fit]], lines: list[str]) -> None:
    """Phase 8 (review.md item 12): Pettitt p-values beside their years, and
    the unexplained difference-vs-ratio change-point discrepancy."""
    out = {}
    for label in ("Mammoth", "Hardy"):
        tbl = fits[label]["all"][0]
        out[label] = _pettitt_result(tbl)
    tbl_h, tbl_m = fits["Hardy"]["all"][0], fits["Mammoth"]["all"][0]
    # Complete water years only, on both sides: an incomplete final year's
    # min7 is not comparable and would shift the change-point.
    a = tbl_h[tbl_h["complete"]].set_index("wy")["min7_cfs"]
    b = tbl_m[tbl_m["complete"]].set_index("wy")["min7_cfs"]
    diff = (a - b).dropna()
    pt_d = pettitt(diff.to_numpy(dtype="float64"))
    diff_wy = int(diff.index[pt_d.change_index])
    ratio = np.log((a / b).replace([np.inf, -np.inf], np.nan).dropna())
    pt_r = pettitt(ratio.to_numpy(dtype="float64"))
    ratio_wy = int(ratio.index[pt_r.change_index])
    lines += [
        "## Change-points: what steps, and when", "",
        *[f"- {label} min7: {out[label][2]}"
          + ("" if out[label][1] < 0.05 else " — **not significant**; it must not be read as a step, and in "
             "particular must not be set beside a significant one as if the two agreed.")
          for label in out],
        f"- Hardy−Mammoth min7 **difference**: after WY {diff_wy} (K={pt_d.k:.0f}, p={pt_d.p:.3f}, n={pt_d.n}).",
        f"- log(Hardy/Mammoth) **ratio**: after WY {ratio_wy} (K={pt_r.k:.0f}, p={pt_r.p:.3f}, n={pt_r.n}).",
        "",
        (f"The difference series steps at WY {diff_wy} while the ratio changes at WY {ratio_wy}. "
         "**This discrepancy is unexplained.** A difference is dominated by the high-flow years and a ratio by "
         "the proportional change, so the two can legitimately locate different years, but which is the "
         "physically meaningful date is not settled by anything in this study."
         if diff_wy != ratio_wy else
         f"The difference and the ratio both locate the change at WY {diff_wy}, so on complete water years the "
         "two framings agree; the earlier WY2008-vs-WY2013 discrepancy was an artefact of including an "
         "incomplete final year.")
        + " Synoptic seepage runs (Mammoth → South Fork → Hardy at low flow) are what would settle the cause.",
        "",
    ]


def _major_flood_dates(peaks: pd.DataFrame) -> pd.Series:
    d = pd.to_datetime(peaks["date"])
    if d.dt.tz is not None:
        d = d.dt.tz_localize(None)
    return d[peaks["gage_ht_ft"] >= MAJOR_FLOOD_FT].reset_index(drop=True)


def main() -> None:
    end = date.today().isoformat()
    TABLES_DIR.mkdir(parents=True, exist_ok=True)
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    basin = basin_mod.get_basin_pcpn(START_DATE, end)
    oni_df = oni.get_oni()
    series = {
        "Mammoth": usgs.get_dv(SITE_MAMMOTH, PARAM_DISCHARGE, START_DATE, end),
        "Hardy": usgs.get_dv(SITE_HARDY, PARAM_DISCHARGE, START_DATE, end),
    }
    peaks = usgs.get_peaks(SITE_HARDY)
    majors = _major_flood_dates(peaks)

    lines = [
        f"# Phase 4 — base flow (Q1, Q4, Q5) — generated {date.today().isoformat()}",
        "",
        "Every trend line reports Sen slope, 95% CI, MK z/p and n; every analysis is repeated on "
        "approved-only data and flagged **CHANGED** if the conclusion differs.",
        "",
        "## Q1 attribution",
        "",
        f"Basin precip: {basin_mod.basin_label()} [{BASIN_PRECIP_SOURCE}], {basin['date'].min().date()}–{basin['date'].max().date()}; "
        f"ONI: CPC, {oni_df['date'].min().date()}–{oni_df['date'].max().date()}.",
        "",
        "Model: OLS log(min7) ~ p_trailing_in + p_trailing_prev_in + oni_trailing (HC3). Predictors are strictly "
        "antecedent to each water year's own min7 window: `p_trailing_in` = basin precip over the 365 days ending the "
        "day before that WY's 7-day min7 window STARTS (its end date minus 7 days); `p_trailing_prev_in` = the 365 "
        "days before that; `oni_trailing` = mean ONI over the 6 center-months ending in the month before that same "
        "window-start day (end date minus 7 days). (The earlier fixed Sep–Feb recharge total "
        "leaked precipitation that fell after most years' min7.) Precip predictors require ≥90% day coverage; ONI ≥4 "
        "of 6 months. Incomplete water years are excluded from the fit.",
        "",
    ]
    fits = {label: _fit_section(label, q, basin, oni_df, lines) for label, q in series.items()}
    lines += _hardy_ratio_section(fits, series, oni_df)
    _mammoth_cross_source_section(series["Mammoth"], oni_df, end, lines)
    _bfi_section(series, lines)
    _min7_figure(fits, series)
    lines += ["![min7](../reports/figures/phase4_min7_trend.png)", ""]
    _rating_section(end, majors, series["Hardy"], peaks, lines)
    _postflood_section(series, basin, majors, lines)
    _change_point_note(fits, lines)
    lines += [
        "## Limitations",
        "",
        "- Regional-skew values and the USGS rating-shift tables remain unobtained. Q5 no longer rests on "
        "IV-derived stage-at-flow alone: the field-measurement trend above is independent of the rating, and "
        "the gauge datum records have now been reviewed (two post-2022 revisions, no site move, nothing at "
        "WY2008).",
        "- Hardy series is WY 2002+ (n≤24); Mammoth Spring vent carries the 1981+ record.",
        f"- Q4 n equals the number of ≥{MAJOR_FLOOD_FT:.0f} ft events in the Hardy peak file; CI is a bootstrap on a handful "
        "of events and excludes matching uncertainty and control-year reuse (descriptive, not causal).",
        f"- Q5 shifts use ±365-day windows around each event; events before IV_START ({IV_START}) have no pairs and are omitted.",
        f"- Basin precip: {basin_mod.basin_label()}. The polygon excludes recharge shared with Bill Mac and Greer springs (separate MoDNR layers). AORC before 2002 has no radar input and shares gauge/Stage IV inputs with PRISM, so the two grids are not independent.",
    ]
    write_report(DOCS_DIR / "phase4_baseflow.md", lines)
    print(f"wrote {DOCS_DIR / 'phase4_baseflow.md'}")


if __name__ == "__main__":
    main()
