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
from spring_river.hydro.lowflow import PREDICTORS, AttributionFit, attribution_table, fit_attribution
from spring_river.hydro.postflood import (
    PRE_STATE_DAYS,
    RECESSION_SKIP_DAYS,
    matched_comparison,
    paired_summary,
)
from spring_river.ingest import basin as basin_mod, oni, usgs
from spring_river.ingest.pull_all import IV_START
from spring_river.qa.rating import (
    flow_percentile_stages,
    loglog_correlation,
    pair_iv,
    rating_shift_at_events,
    rating_table,
    stage_at_flow,
)
from spring_river.stats.trends import MIN_N, TrendResult, pettitt, trend_test

BFI_METHODS = ("eckhardt", "lyne_hollick")
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
    lines.append("")


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
        "antecedent match.",
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
        "day before that WY's min7 end date; `p_trailing_prev_in` = the 365 days before that; `oni_trailing` = mean "
        "ONI over the 6 months ending the month before the min7 end date. (The earlier fixed Sep–Feb recharge total "
        "leaked precipitation that fell after most years' min7.) Precip predictors require ≥90% day coverage; ONI ≥4 "
        "of 6 months. Incomplete water years are excluded from the fit.",
        "",
    ]
    fits = {label: _fit_section(label, q, basin, oni_df, lines) for label, q in series.items()}
    _bfi_section(series, lines)
    _min7_figure(fits, series)
    lines += ["![min7](../reports/figures/phase4_min7_trend.png)", ""]
    _rating_section(end, majors, series["Hardy"], peaks, lines)
    _postflood_section(series, basin, majors, lines)
    lines += [
        "## Limitations",
        "",
        "- Regional-skew, datum and USGS rating-shift records remain unobtained; Q5 rests on IV-derived stage-at-flow only.",
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
