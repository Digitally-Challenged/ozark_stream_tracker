"""Phase 7 exit artifact: docs/phase7_seasonality.md (peak timing + recession).

Peak timing uses circular statistics on three series: Hardy POT >=10 ft event
dates (daily-max IV stage, WY 2008+), Hardy annual peaks (WY 2002+) and the
long Imboden annual-peak series (WY 1937+). Recession constants come from
Hardy DV discharge (min peak 10,000 cfs) and, as the aquifer-side check, the
Mammoth Spring vent gauge (min peak = 90th percentile of its DV).
"""
import textwrap
import warnings
from datetime import date

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from spring_river.analysis.common import (  # noqa: E402
    approval_variants,
    caption,
    fmt_trend,
    sensitivity_lines,
    write_report,
)
from spring_river.analysis.phase5 import _peaks_by_wy  # noqa: E402
from spring_river.climate.seasonal import (  # noqa: E402
    ALL_PERIOD,
    circular_se_days,
    peak_timing_by_period,
    watson_williams,
)
from spring_river.config import (  # noqa: E402
    DOCS_DIR,
    FIGURES_DIR,
    PARAM_DISCHARGE,
    PARAM_STAGE,
    SITE_HARDY,
    SITE_IMBODEN,
    SITE_MAMMOTH,
    START_DATE,
    TABLES_DIR,
)
from spring_river.hydro.pot import pot_events  # noqa: E402
from spring_river.hydro.recession import (  # noqa: E402
    DEFAULT_SKIP_DAYS,
    event_k_table,
    master_recession,
    recession_segments,
)
from spring_river.hydro.wateryear import daily_max_stage, water_year  # noqa: E402
from spring_river.ingest import usgs  # noqa: E402
from spring_river.ingest.pull_all import IV_START  # noqa: E402
from spring_river.stats.trends import MIN_N, TrendResult, pettitt, trend_test  # noqa: E402

POT_STAGE_FT = 10.0
POT_START_WY = 2008
HARDY_MIN_PEAK_CFS = 10_000.0
MAMMOTH_PEAK_QUANTILE = 0.90
DECADE_YEARS = 10
MRC_MIN_RUNS = 3
# Below this r2 a single-exponential recession fit describes the event poorly;
# such fits are flagged, not dropped, and their long k inflates the IQR.
MIN_RECESSION_R2 = 0.75
MONTH_LABELS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
REPORT_PATH = DOCS_DIR / "phase7_seasonality.md"
TimingSeries = tuple[str, pd.Series, str]  # (label, dates, caption)


def _decade_start(year: int) -> int:
    return year - year % DECADE_YEARS


def _pot_dates(stage: pd.DataFrame) -> pd.Series:
    ev = pot_events(stage, POT_STAGE_FT)["peak_date"].dt.normalize()
    return ev[water_year(ev) >= POT_START_WY].reset_index(drop=True)


def _timing_series(stage: pd.DataFrame, hardy_pk: pd.DataFrame, imb_pk: pd.DataFrame) -> list[TimingSeries]:
    pot = _pot_dates(stage)
    return [
        (
            f"Hardy POT ≥{POT_STAGE_FT:.0f} ft events (WY {POT_START_WY}+)",
            pot,
            caption(f"USGS IV stage {SITE_HARDY} daily max, 7-day declustered", stage),
        ),
        (
            f"Hardy annual peaks (WY {int(hardy_pk['wy'].min())}+)",
            hardy_pk["date"],
            f"source: USGS annual peaks {SITE_HARDY}; period WY {int(hardy_pk['wy'].min())}–"
            f"{int(hardy_pk['wy'].max())}; peaks file is approved data",
        ),
        (
            f"Imboden annual peaks (WY {int(imb_pk['wy'].min())}+)",
            imb_pk["date"],
            f"source: USGS annual peaks {SITE_IMBODEN}; period WY {int(imb_pk['wy'].min())}–"
            f"{int(imb_pk['wy'].max())}; peaks file is approved data",
        ),
    ]


def _timing_table(series: list[TimingSeries]) -> pd.DataFrame:
    frames = []
    for label, dates, _ in series:
        start = _decade_start(int(pd.to_datetime(dates).dt.year.min()))
        tbl = peak_timing_by_period(dates, DECADE_YEARS, start_year=start)
        frames.append(tbl.assign(series=label))
    out = pd.concat(frames, ignore_index=True)
    return out[["series", "period", "n", "mean_doy", "mean_date_label", "R", "rayleigh_p"]]


def _timing_lines(series: list[TimingSeries], tbl: pd.DataFrame) -> list[str]:
    lines = [
        "## Peak timing (circular statistics by calendar decade)",
        "",
        "Mean date is the circular mean of day-of-year; R is the mean resultant length (0 = uniform through the "
        "year, 1 = every peak on the same day); Rayleigh p tests uniformity (Zar approximation, adequate for n ≥ 3; "
        "blank below that). Decades are calendar decades, so the first row of each series is partial.",
        "",
    ]
    for label, _, cap in series:
        part = tbl[tbl["series"] == label].drop(columns="series")
        show = part.assign(
            mean_doy=part["mean_doy"].round(1), R=part["R"].round(3), rayleigh_p=part["rayleigh_p"].round(4)
        )
        whole = part[part["period"] == ALL_PERIOD].iloc[0]
        lines += [
            f"### {label}",
            "",
            f"{cap}",
            "",
            show.to_markdown(index=False),
            "",
            f"Whole series: n={int(whole['n'])}, mean date {whole['mean_date_label']}, R={whole['R']:.3f}, "
            f"Rayleigh p={whole['rayleigh_p']:.4f}.",
            "",
        ]
    return lines


def _drift_test_lines(series: list[TimingSeries], tbl: pd.DataFrame) -> list[str]:
    """Phase 8 (review.md item 13): 'no decadal drift' was asserted, not
    tested. Watson–Williams across decades tests it, and the circular standard
    error says how much a decade mean can swing on n≈10 alone."""
    rows = []
    for label, dates, _ in series:
        d = pd.Series(pd.to_datetime(dates)).dropna()
        groups = [g for _, g in d.groupby(d.dt.year.map(_decade_start))]
        r = watson_williams(groups)
        part = tbl[(tbl["series"] == label) & (tbl["period"] != ALL_PERIOD)]
        ses = [circular_se_days(int(x["n"]), float(x["R"])) for _, x in part.iterrows()
               if x["n"] > 0 and pd.notna(x["R"])]
        rows.append({"series": label, "decades_tested": r["k"], "n_events": r["N"],
                     "F": r["F"], "df1": r["df1"], "df2": r["df2"], "p": r["p"],
                     "r_bar": r["r_bar"],
                     "median_decade_se_days": float(np.median(ses)) if ses else float("nan")})
    out = pd.DataFrame(rows)
    out.to_parquet(TABLES_DIR / "phase7_timing_drift_test.parquet")
    sig = out.loc[out["p"] < 0.05, "series"].tolist()
    long_series = out.loc[out["n_events"].idxmax()]
    return [
        "### Is the decadal movement a drift? (Watson–Williams)", "",
        "Decade mean dates swing widely, but with n≈10 events per decade so does the mean of a stationary "
        "process. Watson–Williams tests a common circular mean across decades; `median_decade_se_days` is the "
        "typical circular standard error of one decade's mean, i.e. how far it can move on sampling alone.", "",
        out.round({"F": 3, "p": 4, "r_bar": 3, "median_decade_se_days": 1}).to_markdown(index=False), "",
        (f"- **{', '.join(sig)} rejects a common decadal mean** (p<0.05), so 'no drift' does not hold "
         "universally and the earlier blanket assertion was wrong. Note what this does and does not license: "
         f"on the long {long_series['series']} series — the only one with enough decades to speak to a "
         f"century-scale drift — the test does NOT reject (p={long_series['p']:.2f}, "
         f"{int(long_series['decades_tested'])} decades, n={int(long_series['n_events'])}). The short Hardy "
         "series covers three decades, one of them partial, and a significant difference among three decade "
         "means is not a direction of travel."
         if sig else
         "- **No series rejects a common decadal mean.** The decade-to-decade movement is within what "
         "sampling noise produces at this n, so 'no drift' is now a tested statement rather than an "
         "assertion."),
        "- Either way this is a test of no *difference*, not proof of stability: with a decade mean's standard "
        f"error around {out['median_decade_se_days'].median():.0f} days, only a large drift would be detected.",
        "- Watson–Williams assumes a shared concentration and is reliable for R̄ above ~0.45; `r_bar` is "
        "reported so the reader can judge whether that holds.", "",
    ]


def _rose_axis(ax: plt.Axes, dates: pd.Series, label: str) -> None:
    months = pd.to_datetime(dates).dt.month.to_numpy()
    counts = np.bincount(months, minlength=13)[1:]
    theta = np.deg2rad(np.arange(12) * 30.0 + 15.0)
    ax.bar(theta, counts, width=np.deg2rad(30), bottom=0.0, alpha=0.75, edgecolor="black", linewidth=0.5)
    doy = pd.to_datetime(dates).dt.dayofyear.to_numpy(dtype="float64")
    ang = 2 * np.pi * (doy - 1) / 365.25
    c, s = np.cos(ang).mean(), np.sin(ang).mean()
    r = float(np.hypot(c, s))
    ax.annotate(
        "", xy=(float(np.arctan2(s, c) % (2 * np.pi)), r * counts.max()), xytext=(0, 0),
        arrowprops={"arrowstyle": "-|>", "color": "crimson", "lw": 2},
    )
    ax.set_theta_zero_location("N")
    ax.set_theta_direction(-1)
    ax.set_xticks(np.deg2rad(np.arange(12) * 30.0 + 15.0))
    ax.set_xticklabels(MONTH_LABELS)
    ax.set_yticklabels([])
    ax.set_title(f"{label}\nn={len(dates)}, R={r:.2f}", fontsize=9)


def _timing_figure(series: list[TimingSeries]) -> None:
    fig, axes = plt.subplots(1, len(series), figsize=(5 * len(series), 5.6), subplot_kw={"projection": "polar"})
    for ax, (label, dates, _) in zip(axes, series):
        _rose_axis(ax, dates, label)
    fig.suptitle(
        "Peak timing by month (bars = count; red arrow = circular mean, length ∝ R)\n"
        + "\n".join(cap for _, _, cap in series),
        fontsize=8,
    )
    fig.tight_layout(rect=(0, 0, 1, 0.86))
    fig.savefig(FIGURES_DIR / "phase7_peak_timing.png", dpi=150)
    plt.close(fig)


def _k_trend(tbl: pd.DataFrame) -> TrendResult | None:
    ok = tbl.dropna(subset=["k_days"])
    if len(ok) < MIN_N:
        return None
    return trend_test(ok["k_days"].to_numpy(dtype="float64"), ok["wy"].to_numpy(dtype="float64"))


def _pettitt_line(tbl: pd.DataFrame) -> str:
    ok = tbl.dropna(subset=["k_days"]).sort_values("peak_date")
    if len(ok) < MIN_N:
        return f"not tested (n={len(ok)} < {MIN_N})"
    pt = pettitt(ok["k_days"].to_numpy(dtype="float64"))
    return f"after {ok['peak_date'].iloc[pt.change_index].date()} (WY {int(ok['wy'].iloc[pt.change_index])}; K={pt.k:.0f}, p={pt.p:.3f}, n={pt.n})"


def _trend_or_short(r: TrendResult | None, tbl: pd.DataFrame) -> str:
    n = int(tbl["k_days"].notna().sum())
    return fmt_trend(r, "days") if r is not None else f"not tested (n={n} < {MIN_N})"


def _mrc(dv: pd.DataFrame, min_peak: float) -> pd.DataFrame:
    """Master recession curve trimmed to days reached by at least MRC_MIN_RUNS runs."""
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", RuntimeWarning)
        mrc = master_recession(recession_segments(dv, min_peak))
    return mrc[mrc["n"] >= MRC_MIN_RUNS].reset_index(drop=True)


def _recession_site(label: str, slug: str, site: str, dv: pd.DataFrame, min_peak: float) -> tuple[list[str], pd.DataFrame]:
    variants = approval_variants(dv)
    tables = {v: event_k_table(d, min_peak) for v, d in variants.items()}
    tables["all"].to_parquet(TABLES_DIR / f"phase7_recession_k_{slug}.parquet")
    mrc = _mrc(variants["all"], min_peak)
    mrc.to_parquet(TABLES_DIR / f"phase7_master_recession_{slug}.parquet")
    k_all = tables["all"]["k_days"].dropna()
    trends = {v: _k_trend(t) for v, t in tables.items()}
    fitted = tables["all"].dropna(subset=["k_days"])
    # Events cluster within wet years, so the number of events overstates
    # independence. The count of DISTINCT water years is the effective n for
    # a trend against water year.
    n_events, n_blocks = len(fitted), int(fitted["wy"].nunique())
    poor = fitted[fitted["r2"] < MIN_RECESSION_R2]
    show = tables["all"].assign(peak_date=tables["all"]["peak_date"].dt.date).round({"k_days": 1, "r2": 3})
    if len(poor):
        show = show.assign(low_r2=show["r2"] < MIN_RECESSION_R2)
    lines = [
        f"### {label} (min peak {min_peak:,.0f} cfs, skip {DEFAULT_SKIP_DAYS} days, ≥10-day runs, ≤2% daily rise)",
        "",
        caption(f"USGS DV discharge {site}", dv),
        "",
        f"- events: {len(tables['all'])} (k fitted for {len(k_all)}); median k {k_all.median():.1f} days "
        f"(IQR {k_all.quantile(0.25):.1f}–{k_all.quantile(0.75):.1f}); median r² "
        f"{tables['all']['r2'].median():.3f}",
        f"- k trend vs water year: {_trend_or_short(trends['all'], tables['all'])}",
        f"- **effective n: {n_blocks} water-year blocks** carry the {n_events} fitted events "
        f"({n_events / n_blocks:.1f} per block). The trend test treats each event as independent, but events "
        f"cluster within wet years, so its n={n_events} overstates the information: read the trend against "
        f"n≈{n_blocks}, not n={n_events}.",
        (f"- **{len(poor)} fits have r² < {MIN_RECESSION_R2}** (k "
         f"{poor['k_days'].min():,.0f}–{poor['k_days'].max():,.0f} days), flagged `low_r2` in the table below. "
         "A single-exponential fit describes these events poorly and their long k inflates the IQR; the "
         f"median k over the {len(fitted) - len(poor)} well-fitted events alone is "
         f"{fitted.loc[fitted['r2'] >= MIN_RECESSION_R2, 'k_days'].median():.1f} days."
         if len(poor) else f"- all fitted events have r² ≥ {MIN_RECESSION_R2}."),
        f"- Pettitt change-point in k: {_pettitt_line(tables['all'])}",
        "",
        "Sensitivity (approved-only DV days; recession runs are re-extracted within approved-only gap-free segments):",
        "",
    ]
    if trends["all"] is not None and trends["approved"] is not None:
        lines += sensitivity_lines(f"{label} k (days/yr)", trends["all"], trends["approved"])
        if len(tables["all"]) == len(tables["approved"]):
            lines.append("- Identical event sets: no qualifying peak falls in the provisional period.")
    else:
        lines += [f"- approved-only: {_trend_or_short(trends['approved'], tables['approved'])}; sensitivity not comparable."]
    lines += ["", show.to_markdown(index=False), ""]
    return lines, mrc


def _mrc_figure(mrcs: dict[str, pd.DataFrame], caps: dict[str, str]) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.5))
    for ax, (label, mrc) in zip(axes, mrcs.items()):
        ax.plot(mrc["t_days"], mrc["ln_ratio_median"], color="navy", label="median")
        ax.fill_between(mrc["t_days"], mrc["ln_ratio_q25"], mrc["ln_ratio_q75"], color="navy", alpha=0.2, label="IQR")
        ax.set_xlabel(f"days after peak (normalised at day {DEFAULT_SKIP_DAYS})")
        ax.set_ylabel("ln(q / q_skip)")
        ax.set_title(f"{label}\n{textwrap.fill(caps[label], 70)}", fontsize=8)
        ax.legend(loc="lower left")
    fig.suptitle(
        f"Master recession curves (matching-strip approximation; days with ≥{MRC_MIN_RUNS} runs; n per day in tables)",
        fontsize=9,
    )
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / "phase7_master_recession.png", dpi=150)
    plt.close(fig)


def _limitations(imb_pk: pd.DataFrame, mammoth_min: float) -> list[str]:
    return [
        "## Limitations",
        "",
        "- Hardy POT events use daily MAX IV stage (an upper bound relative to a daily-mean product); event dates "
        "are the day of the declustered maximum.",
        f"- Recession k depends on the min-peak and skip choices (Hardy {HARDY_MIN_PEAK_CFS:,.0f} cfs, Mammoth "
        f"{mammoth_min:,.0f} cfs = {MAMMOTH_PEAK_QUANTILE:.0%} quantile of its DV; skip {DEFAULT_SKIP_DAYS} days). "
        "A single-exponential fit ignores multi-store behaviour; r² is reported per event.",
        "- The k trend treats each event as a sample; events cluster within wet years, so n overstates independence.",
        f"- Imboden annual peaks in NWIS begin WY {int(imb_pk['wy'].min())}; decade rows before that are absent "
        f"and the {_decade_start(int(imb_pk['wy'].min()))}s row is partial.",
        "- Rayleigh tests uniformity only; a bimodal (spring/autumn) pattern can give low R without being uniform.",
        "- Master recession curves are unweighted medians across events, truncated at the last day reached by "
        f"≥{MRC_MIN_RUNS} runs; the late IQR band rests on few long runs.",
    ]


def main() -> None:
    end = date.today().isoformat()
    TABLES_DIR.mkdir(parents=True, exist_ok=True)
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    hardy_pk = _peaks_by_wy(usgs.get_peaks(SITE_HARDY))
    imb_pk = _peaks_by_wy(usgs.get_peaks(SITE_IMBODEN))
    hardy_dv = usgs.get_dv(SITE_HARDY, PARAM_DISCHARGE, START_DATE, end)
    mammoth_dv = usgs.get_dv(SITE_MAMMOTH, PARAM_DISCHARGE, START_DATE, end)
    stage = daily_max_stage(usgs.get_iv(SITE_HARDY, PARAM_STAGE, IV_START, end))

    series = _timing_series(stage, hardy_pk, imb_pk)
    timing = _timing_table(series)
    timing.to_parquet(TABLES_DIR / "phase7_peak_timing.parquet")
    _timing_figure(series)

    lines = [f"# Phase 7 — seasonality and recession — generated {date.today().isoformat()}", ""]
    lines += _timing_lines(series, timing)
    lines += _drift_test_lines(series, timing)
    lines += ["![peak timing](../reports/figures/phase7_peak_timing.png)", "", "## Recession constants", ""]
    lines += [
        "k (days) from OLS ln q = a − t/k on each recession run after the quickflow crest; runs are extracted only "
        "within gap-free segments. Trend test is Mann-Kendall / Sen on k vs water year of the peak.",
        "",
    ]
    mammoth_min = float(mammoth_dv["value"].quantile(MAMMOTH_PEAK_QUANTILE))
    h_lines, h_mrc = _recession_site("Hardy", "hardy", SITE_HARDY, hardy_dv, HARDY_MIN_PEAK_CFS)
    m_lines, m_mrc = _recession_site("Mammoth Spring", "mammoth", SITE_MAMMOTH, mammoth_dv, mammoth_min)
    lines += h_lines + m_lines
    _mrc_figure(
        {"Hardy": h_mrc, "Mammoth Spring": m_mrc},
        {"Hardy": caption(f"USGS DV {SITE_HARDY}", hardy_dv), "Mammoth Spring": caption(f"USGS DV {SITE_MAMMOTH}", mammoth_dv)},
    )
    lines += ["![master recession](../reports/figures/phase7_master_recession.png)", ""]
    lines += _limitations(imb_pk, mammoth_min)
    write_report(REPORT_PATH, lines)
    print(f"wrote {REPORT_PATH}")


if __name__ == "__main__":
    main()
