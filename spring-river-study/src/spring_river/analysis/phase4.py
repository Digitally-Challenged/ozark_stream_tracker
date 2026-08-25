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
from matplotlib.ticker import MaxNLocator
import pandas as pd

from spring_river.analysis.common import (
    approval_variants,
    caption,
    fmt_trend,
    sensitivity_lines,
    write_report,
)
from spring_river.config import (
    DOCS_DIR,
    FIGURES_DIR,
    MAJOR_FLOOD_FT,
    PARAM_DISCHARGE,
    PARAM_STAGE,
    SITE_HARDY,
    SITE_MAMMOTH,
    START_DATE,
    TABLES_DIR,
)
from spring_river.hydro.baseflow import bfi_by_wy
from spring_river.hydro.lowflow import PREDICTORS, AttributionFit, attribution_table, fit_attribution
from spring_river.hydro.postflood import matched_comparison, paired_summary
from spring_river.ingest import oni, prism, usgs
from spring_river.ingest.pull_all import IV_START
from spring_river.qa.rating import pair_iv, rating_shift_at_events, stage_at_flow
from spring_river.stats.trends import MIN_N, TrendResult, pettitt, trend_test

BFI_METHODS = ("eckhardt", "lyne_hollick")
Fit = tuple[pd.DataFrame, AttributionFit]


def _trend_or_none(x: np.ndarray, t: np.ndarray) -> TrendResult | None:
    ok = ~np.isnan(x) & ~np.isnan(t)
    return trend_test(x[ok], t[ok]) if ok.sum() >= MIN_N else None


def _fmt_or_short(r: TrendResult | None, unit: str, n: int) -> str:
    return fmt_trend(r, unit) if r is not None else f"not tested (n={n} < {MIN_N})"


def _fit_section(
    label: str, dv_q: pd.DataFrame, basin: pd.DataFrame, oni_df: pd.DataFrame, lines: list[str]
) -> dict[str, Fit]:
    out: dict[str, Fit] = {}
    for variant, q in approval_variants(dv_q).items():
        tbl = attribution_table(q, basin, oni_df)
        out[variant] = (tbl, fit_attribution(tbl))
    tbl, fit = out["all"]
    tbl.to_parquet(TABLES_DIR / f"phase4_attribution_{label.lower()}.parquet")
    m7 = tbl[tbl["complete"]].dropna(subset=["min7_cfs"])
    pt = pettitt(m7["min7_cfs"].to_numpy())
    wy_change = int(m7["wy"].iloc[pt.change_index])
    lines += [
        f"### {label}",
        "",
        f"- Series: {caption(f'USGS DV {SITE_MAMMOTH if label == 'Mammoth' else SITE_HARDY} discharge', dv_q)}",
        f"- min7 raw trend (log-cfs): {fmt_trend(fit.min7_trend, 'log-cfs')}",
        f"- Pettitt change-point: after WY {wy_change} (K={pt.k:.0f}, p={pt.p:.3f}, n={pt.n})",
        f"- OLS log(min7) ~ {' + '.join(PREDICTORS)} (HC3): R²={fit.r2:.2f}, n={fit.n}",
    ]
    for k in PREDICTORS:
        lo, hi = fit.ci[k]
        lines.append(f"  - {k}: {fit.coef[k]:.4f} (95% CI {lo:.4f} to {hi:.4f})")
    lines += [
        f"- **Residual trend (non-climatic component): {fmt_trend(fit.residual_trend, 'log-cfs')}**",
        "",
        "Sensitivity:",
        *sensitivity_lines("residual trend", fit.residual_trend, out["approved"][1].residual_trend),
        *sensitivity_lines("min7 raw trend", fit.min7_trend, out["approved"][1].min7_trend),
        "",
    ]
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


def _min7_figure(fits: dict[str, dict[str, Fit]], mammoth: pd.DataFrame) -> None:
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
    fig.suptitle(
        f"Q1 base-flow attribution\n{caption(f'USGS DV {SITE_MAMMOTH} + {SITE_HARDY}', mammoth)}", fontsize=9
    )
    fig.tight_layout(rect=(0, 0, 1, 0.94))
    fig.savefig(FIGURES_DIR / "phase4_min7_trend.png", dpi=150)
    plt.close(fig)


def _rating_section(end: str, majors: pd.Series, lines: list[str]) -> None:
    iv_q = usgs.get_iv(SITE_HARDY, PARAM_DISCHARGE, IV_START, end)
    iv_h = usgs.get_iv(SITE_HARDY, PARAM_STAGE, IV_START, end)
    pairs = pair_iv(iv_q, iv_h)
    sf = stage_at_flow(pairs)
    sf.to_parquet(TABLES_DIR / "phase4_rating_drift.parquet")
    sf_appr = stage_at_flow(pairs[pairs["approved"]].reset_index(drop=True))
    shifts = rating_shift_at_events(sf, majors)
    lines += [
        "## Q5 rating drift (stage at fixed discharge, Hardy IV pairs)",
        "",
        f"Pairs: {caption(f'USGS IV {SITE_HARDY} discharge+stage', pairs.rename(columns={'datetime': 'date'}))}; "
        f"n={len(pairs)} matched 15-min pairs.",
        "",
        sf.pivot(index="wy", columns="flow_cfs", values="stage_median_ft").round(2).to_markdown(),
        "",
        f"Shift across ≥{MAJOR_FLOOD_FT:.0f} ft events (WY of event → WY+1):",
        "",
        shifts.round(2).to_markdown(index=False),
        "",
    ]
    for f in sf["flow_cfs"].unique():
        res = {}
        for variant, frame in (("all", sf), ("approved", sf_appr)):
            s = frame[frame["flow_cfs"] == f].dropna(subset=["stage_median_ft"])
            res[variant] = (_trend_or_none(s["stage_median_ft"].to_numpy(), s["wy"].to_numpy(dtype="float64")), len(s))
        lines.append(f"- stage at {f:.0f} cfs: {_fmt_or_short(res['all'][0], 'ft', res['all'][1])}")
        if res["all"][0] is not None and res["approved"][0] is not None:
            lines += ["  " + ln for ln in sensitivity_lines(f"stage at {f:.0f} cfs", res["all"][0], res["approved"][0])]
        else:
            lines.append(f"  - approved-only: {_fmt_or_short(res['approved'][0], 'ft', res['approved'][1])}")
    _rating_figure(sf, majors, iv_h)
    lines += ["", "![rating](../reports/figures/phase4_rating_drift.png)", ""]


def _rating_figure(sf: pd.DataFrame, majors: pd.Series, iv_h: pd.DataFrame) -> None:
    fig, ax = plt.subplots(figsize=(10, 4))
    for f in sf["flow_cfs"].unique():
        s = sf[sf["flow_cfs"] == f]
        ax.plot(s["wy"], s["stage_median_ft"], marker="o", label=f"{f:.0f} cfs")
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
    lines += ["## Q4 post-flood base flow vs precip-matched years", ""]
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
            f"(bootstrap 95% CI {s['lo']:.1f} to {s['hi']:.1f}); n={s['n']} events",
            f"- approved-only: {s_appr['mean_diff_pct']:.1f}% "
            f"(bootstrap 95% CI {s_appr['lo']:.1f} to {s_appr['hi']:.1f}); n={s_appr['n']} events",
            "",
        ]
        ax.axhline(0, color="k", lw=0.5)
        ax.bar(cmp["event_date"].dt.strftime("%Y-%m"), cmp["diff_pct"], color="C3")
        ax.set_title(f"{label}: post-flood vs matched (mean {s['mean_diff_pct']:.0f}%)", fontsize=9)
        ax.set_ylabel("base-flow difference (%)")
        ax.tick_params(axis="x", labelrotation=45, labelsize=8)
    fig.suptitle(
        f"Q4 6-month post-flood Eckhardt base flow vs 3 precip-matched non-flood years\n"
        f"{caption(f'USGS DV {SITE_MAMMOTH} + {SITE_HARDY}', series['Mammoth'])}; events from USGS peaks {SITE_HARDY}",
        fontsize=9,
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
    basin = prism.get_basin_pcpn(START_DATE, end)
    oni_df = oni.get_oni()
    series = {
        "Mammoth": usgs.get_dv(SITE_MAMMOTH, PARAM_DISCHARGE, START_DATE, end),
        "Hardy": usgs.get_dv(SITE_HARDY, PARAM_DISCHARGE, START_DATE, end),
    }
    majors = _major_flood_dates(usgs.get_peaks(SITE_HARDY))

    lines = [
        f"# Phase 4 — base flow (Q1, Q4, Q5) — generated {date.today().isoformat()}",
        "",
        "Every trend line reports Sen slope, 95% CI, MK z/p and n; every analysis is repeated on "
        "approved-only data and flagged **CHANGED** if the conclusion differs.",
        "",
        "## Q1 attribution",
        "",
        f"Basin precip: PRISM 30 km buffer around West Plains, {basin['date'].min().date()}–{basin['date'].max().date()}; "
        f"ONI: CPC, {oni_df['date'].min().date()}–{oni_df['date'].max().date()}.",
        "",
    ]
    fits = {label: _fit_section(label, q, basin, oni_df, lines) for label, q in series.items()}
    _bfi_section(series, lines)
    _min7_figure(fits, series["Mammoth"])
    lines += ["![min7](../reports/figures/phase4_min7_trend.png)", ""]
    _rating_section(end, majors, lines)
    _postflood_section(series, basin, majors, lines)
    lines += [
        "## Limitations",
        "",
        "- Regional-skew, datum and USGS rating-shift records remain unobtained; Q5 rests on IV-derived stage-at-flow only.",
        "- Hardy series is WY 2002+ (n≤24); Mammoth Spring vent carries the 1981+ record.",
        f"- Q4 n equals the number of ≥{MAJOR_FLOOD_FT:.0f} ft events in the Hardy peak file; CI is a bootstrap on a handful of events.",
        "- Basin precip is the 30 km West Plains PRISM buffer, not a dye-traced recharge polygon.",
    ]
    write_report(DOCS_DIR / "phase4_baseflow.md", lines)
    print(f"wrote {DOCS_DIR / 'phase4_baseflow.md'}")


if __name__ == "__main__":
    main()
