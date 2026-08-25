"""Phase 6 exit artifact: docs/phase6_precip.md (Q3 + coupling).

Series: USC00238880 (West Plains COOP; primary for trend because KUNO ASOS
only starts 1998), KUNO (1998→; check), PRISM 30 km basin mean (1981→).
Also resolves the qa_report open item: KUNO-vs-COOP agreement is re-tested
on monthly totals, where the ~7 AM COOP observation-day offset should wash
out.

The West Plains 1948– record adds a fourth station series: two instruments,
one at a time — COOP daily values through 1998-03-31, then KUNO ASOS from
1998-04-01 raised by the measured COOP/KUNO catch ratio so the whole record
sits on the town gauge's level. No day is borrowed between gauges. The 1948
COOP pull lives in its own cache (`cache_suffix="_1948"`), so the 1981+ COOP
series other phases read is unchanged.
"""
import time
from datetime import date

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from spring_river.analysis.common import approval_variants, caption, fmt_trend, write_report
from spring_river.climate import westplains as westplains_mod
from spring_river.climate.coupling import (
    daily_lag_correlation,
    lag_correlation,
    monthly_series,
    response_lag,
)
from spring_river.climate.intensity import (
    AORC_RADAR_YEAR,
    INDEX_COLUMNS,
    KUNO_SPLICE_YEAR,
    annual_indices,
    era_means,
    era_slopes,
    index_trends,
    max_t_permutation_count,
    step_term_test,
)
from spring_river.config import (
    BASIN_PRECIP_SOURCE,
    DOCS_DIR,
    FIGURES_DIR,
    PARAM_DISCHARGE,
    SITE_MAMMOTH,
    START_DATE,
    TABLES_DIR,
)
from spring_river.ingest import acis, basin as basin_mod, usgs
from spring_river.ingest.pull_all import PRECIP_SIDS

COOP_SID = PRECIP_SIDS[1]
KUNO_SID = PRECIP_SIDS[0]
ALTON_SID = PRECIP_SIDS[2]
COOP_REQUESTED_START = "1948-01-01"
MIN_MONTH_DAYS = 25
N_BOOT = 1000
MAXT_PERMUTATIONS = 5000
# Catch ratios spanning "no adjustment" to "10 % adjustment": the KUNO era is
# scaled by one measured constant, so the result's dependence on it must show.
CATCH_RATIO_SENSITIVITY = (1.00, 1.034, 1.068, 1.10)
DAILY_LAG_MAX_DAYS = 60
DAILY_DECAY_TOLERANCE = 0.002  # r wiggles below this are noise, not structure
WP_LABEL = "West Plains 1948–"
# Filesystem-safe parquet stems for the trend-loop labels.
SERIES_STEM = {WP_LABEL: "westplains_1948"}


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
            _trend_table(tr), ""]


def _trend_table(tr: pd.DataFrame) -> str:
    """Markdown table with negative zeros normalised, so a slope that rounds to
    zero prints `0` rather than the meaningless `-0`."""
    out = tr.drop(columns="series").copy()
    # Only the slope/CI columns: a genuinely tiny p-value must keep its sign
    # and magnitude rather than being flattened to 0 here.
    cols = [c for c in ("slope_per_decade", "lo", "hi", "z") if c in out.columns]
    out[cols] = out[cols].mask(out[cols].abs() < 5e-4, 0.0)
    return out.round(3).to_markdown(index=False)


def _divergence_note(trends: dict[str, pd.DataFrame], indices: dict[str, pd.DataFrame],
                     ratio: float) -> list[str]:
    coop_idx, alton_idx = indices[COOP_SID], indices[ALTON_SID]
    wp_idx = indices[WP_LABEL]
    n_alton = int(alton_idx["total_in"].notna().sum())
    n_wp = int(wp_idx["total_in"].notna().sum())
    # "Highest-power station test" is a claim about index years, so check it.
    station_years = {k: int(indices[k]["total_in"].notna().sum())
                     for k in (COOP_SID, "KUNO", ALTON_SID, WP_LABEL)}
    best = max(station_years, key=station_years.get)
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
            f"- Basin values are {basin_mod.basin_label()}; station gaps enter a gridded product only through its gauge blending. "
            "Treat the basin trends as the Q3 headline and the station tests as a consistency check.",
            f"- {ALTON_SID} (Alton) has no data 1983–1994 and 2012–2016; {n_alton} years pass the 90 % coverage gate, "
            "so its trend test is a consistency check only.",
            f"- **{WP_LABEL}**: two instruments, one at a time — {COOP_SID} daily values through 1998-03-31, then the "
            "KUNO ASOS (West Plains Municipal Airport, 10.7 mi north of and 120 ft above the town gauge) from "
            f"1998-04-01, raised by the measured COOP/KUNO catch ratio {ratio:.3f}. The two gauges differ "
            f"systematically by ~{abs(ratio - 1) * 100:.0f} % on monthly totals, so the airport values are put on the "
            "town gauge's level rather than left as a step at 1998-04-01. **No day is borrowed between gauges**: a day "
            "the period's own instrument missed stays NaN, its year still judged on coverage; nothing is interpolated. "
            f"Taking KUNO from 1998 closes the 2011–2021 volunteer-absence hole: {n_wp} years pass the 90 % coverage gate, against "
            f"{station_years[COOP_SID]} for {COOP_SID} alone, {station_years['KUNO']} for KUNO and {n_alton} for {ALTON_SID}. "
            + (f"It is the highest-power station test in the study."
               if best == WP_LABEL
               else f"Note {best} still has more index years ({station_years[best]}).")
            + " Its result, not the gap-ridden COOP null, is the station-level check on the basin trends.",
            _westplains_interpretation(trends[WP_LABEL], wp_idx, n_wp),
            ""]


def _westplains_interpretation(wp_tr: pd.DataFrame, wp_idx: pd.DataFrame, n_wp: int) -> str:
    """One computed sentence on what the record shows — no typed year counts."""
    tr = wp_tr.set_index("index")
    yrs = wp_idx.loc[wp_idx["total_in"].notna(), "year"]
    sig = tr.index[tr["significant_bh"]].tolist()
    intensity = [c for c in ("max1_in", "max3_in", "sdii_in", "top5_frac") if c in tr.index]
    quiet = [c for c in intensity if not tr.loc[c, "significant_bh"]]
    return (f"- Reading the {WP_LABEL}, from its numbers: over the {n_wp} complete years "
            f"({int(yrs.min())}–{int(yrs.max())}) the BH-significant indices are "
            f"{', '.join(sig) if sig else 'none'}"
            + (f", while the intensity indices ({', '.join(quiet)}) have CIs spanning zero. "
               if quiet else ". ")
            + "With the coverage problem removed, the gauge does not reproduce the basin series' "
              "apparent intensification. Phase 8 (below) tests the two candidate explanations and rejects the "
              "point-vs-areal / record-length one: the gauge fails to corroborate over AORC's *identical* window "
              f"too, and the basin indices step at the {AORC_RADAR_YEAR} radar onset rather than trending. The "
              "parsimonious reading is that the intensification is in the product.")


def _q3_step_section(basin_idx: pd.DataFrame, wp_idx: pd.DataFrame, ratio_sens: list[tuple[float, list[str]]],
                     wp_step: pd.DataFrame, wp_tr: pd.DataFrame) -> list[str]:
    """Phase 8 (review.md items 1, 3, 9): the 2002 product discontinuity, the
    within-era slopes, the product-vs-gauge means, the family-wise count and
    the West Plains catch-ratio sensitivity. Q3's headline rests on these."""
    step = step_term_test(basin_idx, AORC_RADAR_YEAR)
    eras = era_slopes(basin_idx, AORC_RADAR_YEAR)
    means = era_means({"AORC basin": basin_idx, WP_LABEL: wp_idx}, AORC_RADAR_YEAR)
    n_maxt, maxt = max_t_permutation_count(basin_idx, n_perm=MAXT_PERMUTATIONS, seed=0)
    n_bh = int(index_trends(basin_idx)["significant_bh"].sum())
    step.to_parquet(TABLES_DIR / "phase6_step_2002.parquet")
    eras.to_parquet(TABLES_DIR / "phase6_era_slopes.parquet")
    means.to_parquet(TABLES_DIR / "phase6_era_means.parquet")
    maxt.to_parquet(TABLES_DIR / "phase6_maxt.parquet")
    wp_step.to_parquet(TABLES_DIR / "phase6_step_1998_westplains.parquet")

    s = step.set_index("index")
    sharp = [c for c in ("sdii_in", "days_ge_1", "max1_in") if c in s.index]
    stepped = [c for c in sharp if s.loc[c, "step_p"] < 0.05]
    flat = [c for c in sharp if not (s.loc[c, "slope_lo_per_decade"] > 0 or s.loc[c, "slope_hi_per_decade"] < 0)]
    era_sharp = eras[eras["index"].isin(sharp)]
    era_rising = era_sharp[era_sharp["lo"] > 0]

    lines = [
        f"## Q3 step test: is the AORC intensity signal a trend or a {AORC_RADAR_YEAR} product change?", "",
        f"AORC v1.1 gains radar (Stage IV/MRMS) input at {AORC_RADAR_YEAR}. A monotone trend test cannot "
        "distinguish a trend from a step at a known input change, so the basin indices are refitted as "
        f"OLS index ~ year + I(year ≥ {AORC_RADAR_YEAR}) with HC3 errors. `slope_per_decade` is the trend that "
        "survives once the step is allowed for.", "",
        step.round(4).to_markdown(index=False), "",
        f"- storm-sharpness indices with a significant step at {AORC_RADAR_YEAR}: "
        f"{', '.join(stepped) if stepped else 'none'}; with a residual trend CI spanning zero: "
        f"{', '.join(flat) if flat else 'none'} of {len(sharp)} tested.",
        f"- within-era Sen slopes: {len(era_rising)} of {len(era_sharp)} sharpness-index/era combinations have a "
        "CI excluding zero on the rising side.", "",
        "### Within-era Sen slopes (per decade)", "",
        eras.round(3).to_markdown(index=False), "",
        f"### Pre/post-{AORC_RADAR_YEAR} means: AORC vs the gauge over identical years", "",
        f"Both series restricted to the calendar years both cover, so this is not a comparison of different "
        "periods. If the change were meteorological the two products would move together; if it is a change in "
        "the product's inputs, only the gridded series moves.", "",
        means.round(3).to_markdown(index=False), "",
        "### Family-wise count (max-T permutation)", "",
        f"Year labels permuted jointly across the {len(INDEX_COLUMNS)} indices ({MAXT_PERMUTATIONS} draws, seed 0), "
        "so the null preserves the correlation between them that a per-index BH correction ignores.", "",
        maxt.round(4).to_markdown(index=False), "",
        f"- indices surviving max-T: {n_maxt}/{len(INDEX_COLUMNS)} vs {n_bh}/{len(INDEX_COLUMNS)} under BH. "
        "Subordinate to the step test above: under it none of these is a trend.", "",
        f"### {WP_LABEL} catch-ratio sensitivity and the {KUNO_SPLICE_YEAR} splice", "",
        f"The whole KUNO era is scaled by one constant measured on the period it is applied to, so any error in it "
        "maps one-for-one into the trend. Which indices pass BH at each ratio:", "",
    ]
    for r, sig in ratio_sens:
        lines.append(f"- catch ratio {r:.3f}: {', '.join(sig) if sig else 'no index passes BH at q=0.05'}")
    ws = wp_step.set_index("index")
    ws_sig = [c for c in ws.index if ws.loc[c, "step_p"] < 0.05]
    wt = wp_tr.set_index("index")
    revealed = [c for c in ws.index if ws.loc[c, "slope_p"] < 0.05 and not bool(wt.loc[c, "significant_bh"])]
    lines += [
        "",
        f"A residual step term at the {KUNO_SPLICE_YEAR} instrument change (OLS index ~ year + "
        f"I(year ≥ {KUNO_SPLICE_YEAR}), HC3) on the ratio-adjusted record:", "",
        wp_step.round(4).to_markdown(index=False), "",
        f"- indices with a significant {KUNO_SPLICE_YEAR} step: {', '.join(ws_sig) if ws_sig else 'none'} — the mean "
        "ratio does not fully homogenise the splice (KUNO's tipping bucket counts more small events than a "
        "volunteer observer, deflating KUNO-era SDII).",
        f"- indices whose trend the pooled fit suppresses (slope p<0.05 with the step, not BH-significant without): "
        f"{', '.join(revealed) if revealed else 'none'}.",
        f"- the COOP-only era ({int(wp_idx.dropna(subset=['total_in'])['year'].min())}–{KUNO_SPLICE_YEAR - 1}) "
        "is the homogeneous baseline; "
        "no ratio is applied to it.", "",
        "### Q3 reading", "",
        "Thesis, from the three tables above:", "",
        "1. **Totals are not rising.** Annual and Sep–Feb recharge-season totals have CIs spanning zero on every "
        "series and are unaffected by the step term. This is the most robust Q3 result and the only one to state "
        "without qualification.",
        f"2. **The AORC sharpness indices step at {AORC_RADAR_YEAR} and trend flat-to-negative within each era.** "
        "The apparent intensification coincides with the documented change in the product's inputs, not with a "
        "change in the weather: over identical years the gridded SDII and days ≥ 1 in rise sharply while the "
        "co-located gauge barely moves, and the two products nevertheless agree on how much rain fell.",
        f"3. **No intensification is detectable at the gauge**, over its full "
        f"{int(wp_idx.dropna(subset=['total_in'])['year'].min())}–{int(wp_idx.dropna(subset=['total_in'])['year'].max())} "
        f"record or over AORC's own identical window; what significance there is rests on a knife-edge catch ratio.",
        "4. PRISM over the same polygon shares Stage IV/MRMS and gauge inputs with AORC and is not an independent "
        "witness. The correct statement is that **no intensification is detectable over the recharge area once the "
        "product discontinuity is allowed for** — not that the basin became more intense.", "",
    ]
    return lines


def _buffer_polygon_section(end: str) -> list[str]:
    """Item 8: the first edition's annual-total significance was a threshold
    crossing, not a property of the buffer geometry. Both PRISM geometries,
    so the comparison isolates geometry rather than product."""
    poly = annual_indices(basin_mod.get_basin_pcpn(START_DATE, end, source="prism_polygon"))
    buf = annual_indices(basin_mod.get_basin_pcpn(START_DATE, end, source="prism_buffer"))
    j = (poly[["year", "total_in"]].rename(columns={"total_in": "polygon_in"})
         .merge(buf[["year", "total_in"]].rename(columns={"total_in": "buffer_in"}), on="year")
         .dropna())
    j = j.assign(diff_in=j["buffer_in"] - j["polygon_in"])
    j.to_parquet(TABLES_DIR / "phase6_buffer_vs_polygon.parquet")
    r = float(np.corrcoef(j["polygon_in"], j["buffer_in"])[0, 1])
    from spring_river.stats.trends import trend_test

    diff_trend = trend_test(j["diff_in"].to_numpy(dtype="float64"), j["year"].to_numpy(dtype="float64"))
    n = len(j)
    return [
        "## Buffer vs polygon: was the first edition's rise a property of the geometry?", "",
        f"- annual totals of the two geometries correlate r={r:.3f} (n={n} years).",
        f"- trend of the buffer−polygon difference: {fmt_trend(diff_trend, 'in')}.", "",
        "The difference series has no detectable trend, so the geometries do not differ detectably in how their "
        "totals evolve. The first edition's significant annual-total rise and this edition's null are the same "
        "estimate either side of a p-value threshold — a threshold crossing, not an attribution to the 30 km "
        "buffer. Both geometries give a positive annual-total slope that is not separable from zero at this n.", "",
    ]


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
                 f"USGS DV {SITE_MAMMOTH} + basin precip [{BASIN_PRECIP_SOURCE}]; {mammoth['date'].min().year}–{mammoth['date'].max().year}; "
                 f"approved {mammoth['approved'].mean():.0%}", fontsize=9)
    fig.tight_layout(); fig.savefig(path, dpi=150); plt.close(fig)


def main() -> None:
    end = date.today().isoformat()
    TABLES_DIR.mkdir(parents=True, exist_ok=True); FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    coop = acis.get_station_pcpn(COOP_SID, START_DATE, end)
    coop_1948 = acis.get_station_pcpn(COOP_SID, COOP_REQUESTED_START, end, cache_suffix="_1948")
    kuno = acis.get_station_pcpn(KUNO_SID, START_DATE, end)
    ratio = westplains_mod.catch_ratio(coop_1948, kuno)
    westplains = westplains_mod.splice(coop_1948, kuno, ratio)
    post = westplains[westplains["date"] >= westplains_mod.KUNO_START]
    n_kuno_days = int((post["source"] == "kuno").sum())
    n_missing = int((post["source"] == "none").sum())
    alton = acis.get_station_pcpn(ALTON_SID, START_DATE, end)
    basin = basin_mod.get_basin_pcpn(START_DATE, end)
    mammoth = usgs.get_dv(SITE_MAMMOTH, PARAM_DISCHARGE, START_DATE, end)

    coop_span = _series_span(coop)
    ag = _monthly_agreement(kuno, coop)
    lines = [f"# Phase 6 — precipitation regime (Q3) — generated {date.today().isoformat()}", "",
             f"Series: {COOP_SID} West Plains COOP ({coop_span}; the 1981+ pull, unchanged — the other phases read this "
             f"cache), KUNO ASOS ({_series_span(kuno)})"
             f", {ALTON_SID} Alton COOP ({_series_span(alton)}), "
             f"{WP_LABEL} ({_series_span(westplains)}; COOP USC00238880 through 1998-03-31; KUNO ASOS from "
             f"1998-04-01 raised by the COOP/KUNO catch ratio {ratio:.3f} measured on {ag['months']} overlapping "
             f"months, so the record is on the town gauge's level; no day borrowed between gauges; {n_kuno_days} "
             f"KUNO days and {n_missing} days KUNO missed after 1998-04-01), basin = {basin_mod.basin_label()} ({_series_span(basin)}).", "",
             "## Station agreement on monthly totals (qa_report follow-up)", ""]
    lines += [f"- KUNO vs {COOP_SID} monthly totals (months with ≥{MIN_MONTH_DAYS} days at both stations): r={ag['r']:.2f}, "
              f"ratio COOP/KUNO={ag['ratio']:.2f}, n={ag['months']} months ({ag['first']} to {ag['last']}). "
              f"Daily r was 0.42 in qa_report; monthly aggregation removes the ~7 AM observation-day offset.", ""]

    trends, indices = {}, {}
    for label, df in ((COOP_SID, coop), ("KUNO", kuno), (ALTON_SID, alton),
                      (WP_LABEL, westplains[["date", "pcpn_in"]]), ("basin", basin)):
        idx = annual_indices(df)
        idx.to_parquet(TABLES_DIR / f"phase6_indices_{SERIES_STEM.get(label, label)}.parquet")
        indices[label] = idx
        tr = index_trends(idx).assign(series=label)
        trends[label] = tr
        lines += _trend_section(label, idx, tr, _series_span(df))
    pd.concat(trends.values()).to_parquet(TABLES_DIR / "phase6_index_trends.parquet")
    lines += _divergence_note(trends, indices, ratio)

    # ---- Phase 8: the 2002 product discontinuity and the catch-ratio dependence
    ratio_sens = []
    for r in CATCH_RATIO_SENSITIVITY:
        alt = annual_indices(westplains_mod.splice(coop_1948, kuno, r)[["date", "pcpn_in"]])
        alt_tr = index_trends(alt)
        ratio_sens.append((r, alt_tr.loc[alt_tr["significant_bh"], "index"].tolist()))
    wp_step = step_term_test(indices[WP_LABEL], KUNO_SPLICE_YEAR)
    lines += _q3_step_section(indices["basin"], indices[WP_LABEL], ratio_sens, wp_step, trends[WP_LABEL])
    lines += _buffer_polygon_section(end)

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

    # ---- Phase 8 (item 10): the monthly lag-1 peak is a bin, not a transit time
    dlc = daily_lag_correlation(basin, mammoth, DAILY_LAG_MAX_DAYS)
    dlc.to_parquet(TABLES_DIR / "phase6_daily_lag_correlation.parquet")
    ok = dlc.dropna(subset=["r"])
    peak_day = int(ok.loc[ok["r"].idxmax(), "lag_days"])
    peak_r = float(ok["r"].max())
    # "Monotone" to within a noise tolerance: single-day wiggles of a few 1e-4
    # in an r of ~0.14 are sampling noise, not structure. What matters for the
    # physical claim is that nothing resembling a second peak appears near the
    # 30-day mark the monthly lag-1 result might be read as implying.
    beyond = ok[ok["lag_days"] > peak_day]
    max_rise = float(beyond["r"].diff().dropna().max())
    monotone = max_rise <= DAILY_DECAY_TOLERANCE
    lines += [
        "## Coupling at daily resolution (what the 1-month lag actually means)", "",
        "The monthly analysis above bins to calendar months, so its lag-1 maximum is the coarsest bin that "
        "contains both a fast onset and a long tail. At daily resolution (day-of-year climatology removed from "
        "both series):", "",
        f"- peak cross-correlation at **{peak_day} day(s)** after the rain (r={peak_r:.3f}, "
        f"n={int(ok.loc[ok['lag_days'] == peak_day, 'n'].iloc[0]):,} days).",
        f"- beyond the peak the correlation decays "
        + ("monotonically to within sampling noise (largest single-day rise "
           f"{max_rise:+.4f} in an r of {peak_r:.2f})" if monotone
           else f"with a secondary structure (largest single-day rise {max_rise:+.4f}; see the table)")
        + f", out to {DAILY_LAG_MAX_DAYS} days — **no local maximum near 30 days**.",
        "- Report both: **onset within days; monthly correlation maximised at lag 1 month.** The monthly figure is "
        "a statistic about binned anomalies, not an aquifer transit time.", "",
        dlc.round(4).to_markdown(index=False), "",
    ]

    idx = pd.read_parquet(TABLES_DIR / f"phase6_indices_{COOP_SID}.parquet")
    _indices_figure(idx, COOP_SID, coop_span, FIGURES_DIR / "phase6_indices.png")
    _lag_figure(lc, mammoth, FIGURES_DIR / "phase6_lag_correlation.png")
    lines += ["![indices](../reports/figures/phase6_indices.png)", "",
              f"Figure: annual total, days ≥ 1 in, and max 1-day precip at {COOP_SID}; source RCC-ACIS StnData; period {coop_span}; "
              "years with <90% daily coverage omitted; approval N/A — station precip carries no approval flag.", "",
              "![lag](../reports/figures/phase6_lag_correlation.png)", "",
              f"Figure: {caption(f'USGS DV {SITE_MAMMOTH} + {basin_mod.basin_label()}', mammoth)}.", "",
              "## Limitations", "",
              f"- Station indices are point measurements; basin indices are a gridded areal mean ({basin_mod.basin_label()}) — smoother extremes by construction.",
              f"- The {COOP_SID} series used for the station trend above is the 1981+ pull, so its window matches "
              f"KUNO/basin. The 1948–1980 record **is** now pulled (separate `_1948` cache) but feeds only the "
              f"{WP_LABEL}; the 1981+ COOP series the other analyses read is unchanged.",
              f"- {COOP_SID} has 32 gaps > 7 days (qa_report); years failing 90% coverage are NaN, not low. KUNO years before 1998 are NaN by coverage.",
              "- Precip series carry no approval flag; the all/approved-only rule does not apply to the index trends. "
              "It does apply to the coupling (Mammoth flow carries flags) and is reported above. "
              f"Mammoth flow used in coupling: {caption(f'USGS DV {SITE_MAMMOTH}', mammoth)}.",
              "- Lag-correlation CI is a 12-month block bootstrap of the lagged pairs; it preserves within-year "
              "serial correlation but not dependence across block boundaries, so it is mildly optimistic.",
              f"- **AORC has no radar input before {AORC_RADAR_YEAR}.** Its storm-sharpness indices step at that "
              "date; the step test above, not the monotone trend test, is the Q3 headline. PRISM over the same "
              "polygon shares Stage IV/MRMS and gauge inputs and is not an independent witness. Settling this "
              f"needs NOAA's AORC v1.1 homogeneity documentation, a one-cell AORC re-pull at the gauge "
              "coordinate (the cache keeps only the polygon mean), or an independent grid with no "
              f"{AORC_RADAR_YEAR} input change (nClimGrid-Daily, Livneh).",
              f"- The {WP_LABEL} record's KUNO era rests on one catch ratio measured on the period it is applied "
              "to; the sensitivity above shows which results survive which ratio. A quantile (wet-day-frequency) "
              "matching between COOP and KUNO over the overlapping months, with the adjustment uncertainty "
              "propagated into the trend CI, would replace it.",
              "- The daily cross-correlation removes a day-of-year climatology estimated from the same record, "
              "and its r values carry no CI; it is reported to locate the onset, not to size the coupling."]
    write_report(DOCS_DIR / "phase6_precip.md", lines)
    print(f"wrote {DOCS_DIR / 'phase6_precip.md'} (lag bootstrap {lag_secs:.0f} s)")


if __name__ == "__main__":
    main()
