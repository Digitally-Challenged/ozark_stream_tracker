"""Phase 1: pull everything into data/raw. Idempotent — cached pulls are skipped.

Note: Imboden (07069500) DV discharge has at-source gaps (not a pull defect)
1995-05-10->2001-10-01 and 2015-10-26->2016-12-15; see Task 9's QA report for
their extent and impact.
"""
import time
from datetime import date

import pandas as pd

from spring_river.config import (
    PARAM_DISCHARGE,
    PARAM_STAGE,
    SITE_HARDY,
    SITE_IMBODEN,
    SITE_MAMMOTH,
    START_DATE,
)
from spring_river.ingest import acis, nwps, prism, usgs

# Decisions from docs/data_inventory.md (Task 7):
# - Primary precip = KUNO (West Plains ASOS); secondary = USC00238880 (West Plains COOP).
PRECIP_SIDS = ["KUNO", "USC00238880"]
# - IV stage (parm 00065) confirmed available at Hardy from 2007-10-01 onward.
IV_START = "2007-10-01"


def _pull_iv(site: str, param: str, start: str, end: str) -> pd.DataFrame:
    """Try a single-range IV pull; fall back to per-year chunks if NWIS rejects it."""
    try:
        return usgs.get_iv(site, param, start, end)
    except Exception as exc:  # noqa: BLE001 - NWIS failure modes vary (HTTP, parse, timeout)
        print(f"iv {site} {param} single-range pull failed ({exc!r}); falling back to per-year loop")
        start_year = pd.Timestamp(start).year
        end_year = pd.Timestamp(end).year
        frames = []
        for year in range(start_year, end_year + 1):
            year_start = max(pd.Timestamp(start), pd.Timestamp(year, 1, 1)).strftime("%Y-%m-%d")
            year_end = min(pd.Timestamp(end), pd.Timestamp(year, 12, 31)).strftime("%Y-%m-%d")
            df = usgs.get_iv(site, param, year_start, year_end)
            print(f"  iv {site} {param} {year}: {len(df)} rows (cache usgs_iv_{site}_{param}_{year}_{year})")
            frames.append(df)
        return pd.concat(frames, ignore_index=True)


def main() -> None:
    # USGS NWIS occasionally returns transient 503s under load; if this run
    # dies partway through, just rerun `make data` — fetch_cached persists
    # each successful pull to data/raw as it completes, so a rerun resumes
    # from the first uncached item rather than redoing prior work.
    start_time = time.monotonic()
    end = date.today().isoformat()

    # Hardy has no daily-stage product (verified 2026-08-24); stage comes from IV.
    for site in (SITE_HARDY, SITE_IMBODEN):
        df = usgs.get_dv(site, PARAM_DISCHARGE, START_DATE, end)
        print(f"dv {site} {PARAM_DISCHARGE}: {len(df)} rows")
        print(f"peaks {site}: {len(usgs.get_peaks(site))} rows")

    # Controller ruling: also pull Mammoth Spring vent gauge daily discharge
    # (continuous 1981-02-25 -> present). No peaks/IV for it.
    df = usgs.get_dv(SITE_MAMMOTH, PARAM_DISCHARGE, START_DATE, end)
    print(f"dv {SITE_MAMMOTH} {PARAM_DISCHARGE}: {len(df)} rows")

    df = _pull_iv(SITE_HARDY, PARAM_STAGE, IV_START, end)
    print(f"iv {SITE_HARDY} stage: {len(df)} rows")

    for sid in PRECIP_SIDS:
        df = acis.get_station_pcpn(sid, START_DATE, end)
        print(f"acis {sid}: {len(df)} rows")

    df = prism.get_basin_pcpn(START_DATE, end)
    print(f"prism basin: {len(df)} rows")

    cats = nwps.flood_categories(nwps.get_gauge_info())
    print(f"nwps flood categories: {cats}")

    elapsed = time.monotonic() - start_time
    print(f"make data: done in {elapsed:.1f}s")


if __name__ == "__main__":
    main()
