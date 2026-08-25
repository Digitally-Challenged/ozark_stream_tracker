"""Phase 2 exit artifact: docs/qa_report.md with gap maps and cross-checks."""
from datetime import date

import matplotlib
import pandas as pd

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from spring_river.config import (
    DOCS_DIR,
    FIGURES_DIR,
    PARAM_DISCHARGE,
    PARAM_STAGE,
    SITE_HARDY,
    SITE_IMBODEN,
    SITE_MAMMOTH,
    START_DATE,
)
from spring_river.hydro.wateryear import daily_max_stage
from spring_river.ingest import acis, usgs
from spring_river.ingest.pull_all import IV_START, PRECIP_SIDS
from spring_river.qa.crosscheck import hardy_vs_imboden, precip_overlap
from spring_river.qa.gaps import approval_summary, find_gaps


def main() -> None:
    end = date.today().isoformat()
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    lines = [f"# QA report — generated {date.today().isoformat()}", ""]

    series = {}
    checks = [
        (SITE_HARDY, "Hardy", "discharge", lambda: usgs.get_dv(SITE_HARDY, PARAM_DISCHARGE, START_DATE, end)),
        (SITE_IMBODEN, "Imboden", "discharge", lambda: usgs.get_dv(SITE_IMBODEN, PARAM_DISCHARGE, START_DATE, end)),
        (SITE_HARDY, "Hardy", "stage (daily max of IV)", lambda: daily_max_stage(usgs.get_iv(SITE_HARDY, PARAM_STAGE, IV_START, end))),
        (SITE_MAMMOTH, "Mammoth Spring vent", "discharge", lambda: usgs.get_dv(SITE_MAMMOTH, PARAM_DISCHARGE, START_DATE, end)),
    ]
    for site, label, pname, load in checks:
        df = load()
        series[(label, pname)] = df
        # find_gaps reports gap_start/gap_end as the first/last MISSING day
        # of each run (not the last-good/next-good days bracketing it) — see
        # the "Limitations and deferred QA items" section below for the
        # stated convention.
        gaps = find_gaps(df)
        appr = approval_summary(df)
        lines += [
            f"## {label} {pname}",
            "",
            f"- rows: {len(df)}; span {df['date'].min().date()} → {df['date'].max().date()}",
            f"- approved fraction: {appr['approved_frac']:.3f}; provisional from {appr['provisional_from']}",
            f"- gaps > 7 days: {len(gaps)}",
            "",
            gaps.to_markdown(index=False) if len(gaps) else "(none)",
            "",
        ]

    xc = hardy_vs_imboden(
        series[("Hardy", "discharge")], series[("Imboden", "discharge")]
    )
    hardy_appr = approval_summary(series[("Hardy", "discharge")])
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(xc["date"], xc["residual"], lw=0.5)
    ax.set_title(
        f"Hardy ({SITE_HARDY}) vs Imboden ({SITE_IMBODEN}) log-discharge "
        "regression residuals\n"
        f"source: USGS DV discharge; period {xc['date'].min().date()}–"
        f"{xc['date'].max().date()}; Hardy approved {hardy_appr['approved_frac']:.0%}"
        + (
            f", provisional from {hardy_appr['provisional_from'].date()}"
            if hardy_appr["provisional_from"] is not None
            else ""
        ),
        fontsize=9,
    )
    ax.set_ylabel("log10 residual")
    fig.savefig(FIGURES_DIR / "qa_hardy_imboden_residuals.png", dpi=150)
    z = (xc["residual"] - xc["residual"].mean()) / xc["residual"].std()
    flagged = xc.loc[z.abs() > 4]
    lines += [
        "## Hardy vs Imboden cross-check",
        "",
        f"- overlap days: {len(xc)}; |z| > 4 flagged days: {len(flagged)}",
        "",
        "![residuals](../reports/figures/qa_hardy_imboden_residuals.png)",
        "",
        flagged.to_markdown(index=False) if len(flagged) else "(no flagged days)",
        "",
    ]

    if len(PRECIP_SIDS) >= 2:
        precip_series = {}
        lines += ["## Precip homogeneity", ""]
        for sid in PRECIP_SIDS:
            df = acis.get_station_pcpn(sid, START_DATE, end)
            precip_series[sid] = df
            gap_df = df.rename(columns={"pcpn_in": "value"})[["date", "value"]]
            gaps = find_gaps(gap_df)
            n_nan = int(gap_df["value"].isna().sum())
            lines += [
                f"### {sid}",
                "",
                f"- rows: {len(df)}; span {df['date'].min().date()} → {df['date'].max().date()}",
                f"- NaN days: {n_nan}",
                f"- gaps > 7 days: {len(gaps)}",
                "",
                gaps.to_markdown(index=False) if len(gaps) else "(none)",
                "",
            ]

        overlap = precip_overlap(precip_series[PRECIP_SIDS[0]], precip_series[PRECIP_SIDS[1]])
        lines += [
            f"### {PRECIP_SIDS[0]} vs {PRECIP_SIDS[1]} overlap",
            "",
            f"- overlap days: {overlap['n_days']}",
            f"- correlation: {overlap['corr']:.2f}",
            f"- mean ratio ({PRECIP_SIDS[1]}/{PRECIP_SIDS[0]}): {overlap['mean_ratio']:.2f}",
            "",
            (
                "Daily correlation between an ASOS calendar-day series and a COOP "
                "station whose observation day ends ~7 AM is expected to be depressed "
                "by the observation-time offset; Phase 4 should compare on multi-day "
                "or monthly aggregates before treating this as a data-quality problem."
            ),
            "",
        ]
    else:
        lines += [
            "## Precip homogeneity",
            "",
            "Single precip station configured — homogeneity check skipped; documented per spec risk #6.",
            "",
        ]

    lines += [
        "## Limitations and deferred QA items",
        "",
        "- **USGS datum and rating-shift history** (spec §2.1 / risk #4) has "
        "NOT yet been obtained for Hardy. Stage-discharge rating changes over "
        "1981–2026 could alter the stage-to-flow relationship independent of "
        "any hydrologic trend; Q5 (any claim relating stage thresholds to "
        "flow) currently rests solely on IV-derived stage-at-flow readings, "
        "not on the official rating history. Any conclusion sensitive to "
        "rating shifts must be flagged provisional until this is obtained.",
        "- **Hardy daily stage** has no USGS daily-stage product. This report "
        "uses the daily MAX of instantaneous (IV) stage readings "
        f"(`daily_max_stage`), defined only for WY {pd.Timestamp(IV_START).year + 1}"
        " onward (IV_START = "
        f"{IV_START}). A daily max is systematically greater than or equal to "
        "a daily mean, so Hardy stage-threshold day-counts in this report "
        "are an upper bound relative to a mean-based daily-stage product.",
        "- **Gap boundary convention**: every gap table in this report "
        "(`find_gaps`) reports `gap_start`/`gap_end` as the first and last "
        "MISSING day of the run — not the last good day before the gap or "
        "the next good day after it. Stated once here; `find_gaps` itself is "
        "unchanged.",
        "- **Precipitation gap detection is series-bounded**: gap tables for "
        "each ACIS precip series are computed only within that series' own "
        "first-to-last observed date range. A station with a later start "
        "date (e.g. KUNO, ASOS from 1998) is not flagged as 'gapped' for the "
        "years before its record begins — that absence is a coverage limit, "
        "not a gap, and must be read from the station's stated span above, "
        "not from its gap table.",
        "",
    ]

    (DOCS_DIR / "qa_report.md").write_text("\n".join(lines))
    print("wrote docs/qa_report.md")


if __name__ == "__main__":
    main()
