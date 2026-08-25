"""Phase 2 exit artifact: docs/qa_report.md with gap maps and cross-checks."""
from datetime import date

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from spring_river.config import (
    DOCS_DIR,
    FIGURES_DIR,
    PARAM_DISCHARGE,
    PARAM_STAGE,
    SITE_HARDY,
    SITE_IMBODEN,
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
    ]
    for site, label, pname, load in checks:
        df = load()
        series[(label, pname)] = df
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
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(xc["date"], xc["residual"], lw=0.5)
    ax.set_title("Hardy vs Imboden log-discharge regression residuals")
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
        a = acis.get_station_pcpn(PRECIP_SIDS[0], START_DATE, end)
        b = acis.get_station_pcpn(PRECIP_SIDS[1], START_DATE, end)
        lines += [
            "## Precip homogeneity",
            "",
            f"- {PRECIP_SIDS[0]} vs {PRECIP_SIDS[1]}: {precip_overlap(a, b)}",
            "",
        ]
    else:
        lines += [
            "## Precip homogeneity",
            "",
            "Single precip station configured — homogeneity check skipped; documented per spec risk #6.",
            "",
        ]

    (DOCS_DIR / "qa_report.md").write_text("\n".join(lines))
    print("wrote docs/qa_report.md")


if __name__ == "__main__":
    main()
