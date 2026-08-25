"""Basin-averaged daily precip from the PRISM 4 km grid served by ACIS GridData.

Recharge basin approximation: bounding box around a 30 km radius centred on
West Plains, MO (see spec §1.2). State this wherever the series is used.
"""
import math

import numpy as np
import pandas as pd
import requests

from spring_river.config import RECHARGE_BUFFER_KM, WEST_PLAINS_LATLON
from spring_river.ingest.cache import fetch_cached

GRIDDATA_URL = "https://data.rcc-acis.org/GridData"
PRISM_GRID = "21"
KM_PER_DEG_LAT = 111.32


def _bbox_around(lat: float, lon: float, km: float) -> tuple[float, float, float, float]:
    dlat = km / KM_PER_DEG_LAT
    dlon = km / (KM_PER_DEG_LAT * math.cos(math.radians(lat)))
    return (lon - dlon, lat - dlat, lon + dlon, lat + dlat)


def _empty_grid_frame() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "date": pd.Series([], dtype="datetime64[ns]"),
            "pcpn_in": pd.Series([], dtype="float64"),
        }
    )


def _mean_grid_series(payload: dict) -> pd.DataFrame:
    rows = payload["data"]
    if not rows:
        return _empty_grid_frame()
    dates, means = [], []
    for date_str, grid in rows:
        arr = np.asarray(grid, dtype="float64")
        arr[arr <= -998] = np.nan
        dates.append(date_str)
        means.append(np.nan if np.all(np.isnan(arr)) else float(np.nanmean(arr)))
    return pd.DataFrame({"date": pd.to_datetime(dates), "pcpn_in": means})


def get_basin_pcpn(
    start: str,
    end: str,
    buffer_km: float = RECHARGE_BUFFER_KM,
    refresh: bool = False,
) -> pd.DataFrame:
    lat, lon = WEST_PLAINS_LATLON
    bbox = _bbox_around(lat, lon, buffer_km)
    name = f"prism_basin_pcpn_{int(buffer_km)}km"

    def fetch() -> pd.DataFrame:
        frames = []
        for year_start in pd.date_range(start, end, freq="YS").union(
            pd.DatetimeIndex([pd.Timestamp(start)])
        ):
            year_end = min(
                pd.Timestamp(year_start.year, 12, 31), pd.Timestamp(end)
            )
            body = {
                "bbox": ",".join(f"{v:.4f}" for v in bbox),
                "sdate": year_start.strftime("%Y-%m-%d"),
                "edate": year_end.strftime("%Y-%m-%d"),
                "grid": PRISM_GRID,
                "elems": [{"name": "pcpn"}],
            }
            resp = requests.post(GRIDDATA_URL, json=body, timeout=300)
            resp.raise_for_status()
            payload = resp.json()
            if "error" in payload:
                raise RuntimeError(f"GridData error: {payload['error']}")
            frames.append(_mean_grid_series(payload))
        out = pd.concat(frames, ignore_index=True).drop_duplicates("date")
        return out.sort_values("date").reset_index(drop=True)

    meta = {
        "source": "PRISM 4km daily pcpn via ACIS GridData (grid 21)",
        "bbox": bbox,
        "buffer_km": buffer_km,
        "approximation": "bbox around 30km-radius circle centred on West Plains, MO",
        "start": start,
        "end": end,
    }
    return fetch_cached(name, fetch, meta, refresh=refresh)
