"""Phase 3: annual ledger — one row per water year (spec Phase 3 exit).

Controller ruling (2026-08-24): per-WY BFI (`bfi` column) is a descriptive
number computed on gap-dropped flow via `hydro.baseflow.bfi(q)` on
`grp["value"].dropna().to_numpy()` — the Eckhardt filter state carries across
any gaps that fall inside a water year. This is fine for a descriptive annual
ledger value but is NOT a trend-safe estimate: Phase 4 must use gap-segmented
filtering (reset the filter state at each gap boundary) before making any
claim about a BFI trend over time.

Controller ruling on `precip_cal_in`: `PRECIP_SIDS[0]` (KUNO) only starts in
1998, which would leave `precip_cal_in` NaN/zero-biased for water years
before then. This column instead uses `PRECIP_SIDS[1]` (USC00238880, West
Plains COOP station, 1948-present) so the calendar-year precip total is
populated across the full period of record. `precip_recharge_in` continues to
use the PRISM basin-average grid (Task 5), as in the original brief.
"""
from datetime import date

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

from spring_river.config import (
    FIGURES_DIR,
    PARAM_DISCHARGE,
    PARAM_STAGE,
    PROCESSED_DIR,
    SITE_HARDY,
    START_DATE,
)
from spring_river.hydro.baseflow import bfi
from spring_river.hydro.wateryear import min7, water_year

DEFAULT_THRESHOLDS = {"action": 8.0, "minor": 10.0, "moderate": 14.0, "major": 16.0}


def build_ledger(
    dv_q: pd.DataFrame,
    dv_stage: pd.DataFrame,
    peaks: pd.DataFrame,
    precip: pd.DataFrame,
    basin_precip: pd.DataFrame,
    thresholds: dict[str, float],
) -> pd.DataFrame:
    th = {**DEFAULT_THRESHOLDS, **thresholds}
    q = dv_q.assign(wy=water_year(dv_q["date"]))
    stage = dv_stage.assign(wy=water_year(dv_stage["date"]))
    pk = peaks.assign(wy=water_year(peaks["date"]))

    rows = []
    for wy, grp in q.groupby("wy"):
        st = stage[stage["wy"] == wy]["value"]
        pk_wy = pk[pk["wy"] == wy]
        qv = grp["value"].dropna().to_numpy()
        # recharge season = Sep(wy-1) .. Feb(wy); "< Mar 1" handles leap years
        recharge = basin_precip[
            (basin_precip["date"] >= pd.Timestamp(wy - 1, 9, 1))
            & (basin_precip["date"] < pd.Timestamp(wy, 3, 1))
        ]["pcpn_in"]
        cal = precip[precip["date"].dt.year == wy]["pcpn_in"]
        rows.append(
            {
                "wy": wy,
                "peak_cfs": pk_wy["peak_cfs"].max() if len(pk_wy) else pd.NA,
                "peak_stage_ft": pk_wy["gage_ht_ft"].max() if len(pk_wy) else pd.NA,
                "days_ge_8ft": int((st >= th["action"]).sum()),
                "days_ge_10ft": int((st >= th["minor"]).sum()),
                "days_ge_14ft": int((st >= th["moderate"]).sum()),
                "days_ge_16ft": int((st >= th["major"]).sum()),
                "min7_cfs": min7(grp[["date", "value"]]).get(wy, pd.NA),
                "bfi": bfi(qv) if len(qv) > 30 else pd.NA,
                "precip_cal_in": cal.sum() if len(cal) else pd.NA,
                "precip_recharge_in": recharge.sum() if len(recharge) else pd.NA,
            }
        )
    return pd.DataFrame(rows).sort_values("wy").reset_index(drop=True)


def main() -> None:
    from spring_river.ingest import acis, nwps, prism, usgs
    from spring_river.ingest.pull_all import IV_START, PRECIP_SIDS
    from spring_river.hydro.wateryear import daily_max_stage

    end = date.today().isoformat()
    dv_q = usgs.get_dv(SITE_HARDY, PARAM_DISCHARGE, START_DATE, end)
    # no USGS daily-stage product at Hardy: daily max of IV stage (WY 2008+)
    dv_stage = daily_max_stage(usgs.get_iv(SITE_HARDY, PARAM_STAGE, IV_START, end))
    peaks = usgs.get_peaks(SITE_HARDY)
    # precip_cal_in uses PRECIP_SIDS[1] (USC00238880, 1948-present) rather than
    # PRECIP_SIDS[0] (KUNO, 1998-present) so the column is populated across
    # the full period of record — see module docstring.
    precip = acis.get_station_pcpn(PRECIP_SIDS[1], START_DATE, end)
    basin = prism.get_basin_pcpn(START_DATE, end)
    thresholds = nwps.flood_categories(nwps.get_gauge_info())

    ledger = build_ledger(dv_q, dv_stage, peaks, precip, basin, thresholds)
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    ledger.to_parquet(PROCESSED_DIR / "annual_ledger.parquet")

    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    fig, axes = plt.subplots(3, 1, figsize=(11, 9), sharex=True)
    axes[0].bar(ledger["wy"], pd.to_numeric(ledger["peak_stage_ft"], errors="coerce"))
    axes[0].set_ylabel("peak stage (ft)")
    axes[1].plot(
        ledger["wy"], pd.to_numeric(ledger["min7_cfs"], errors="coerce"), marker="o"
    )
    axes[1].set_ylabel("7-day low flow (cfs)")
    axes[2].bar(
        ledger["wy"], pd.to_numeric(ledger["precip_recharge_in"], errors="coerce")
    )
    axes[2].set_ylabel("recharge-season precip (in)")
    axes[2].set_xlabel("water year")
    fig.suptitle(
        "Spring River at Hardy — annual ledger\n"
        "source: USGS discharge/stage/peaks, PRISM basin recharge precip, "
        "ACIS USC00238880 calendar precip",
        fontsize=11,
    )
    fig.tight_layout(rect=(0, 0, 1, 0.94))
    fig.savefig(FIGURES_DIR / "annual_ledger.png", dpi=150)
    print(f"wrote {PROCESSED_DIR / 'annual_ledger.parquet'} ({len(ledger)} water years)")


if __name__ == "__main__":
    main()
