"""Basin-averaged daily precip from the PRISM 4 km grid served by ACIS GridData.

Two basin definitions (second edition, 2026-08-25):
- polygon=<shapely Polygon>: request the polygon's bbox with grid lat/lon
  metadata and average only cells whose centre falls inside the polygon
  (cache `prism_basin_pcpn_polygon`).
- polygon=None: legacy bbox around a `buffer_km` circle centred on West
  Plains, MO (cache `prism_basin_pcpn_{buffer_km}km`); kept for comparison.
PRISM daily values are the 24 h ending 12 UTC.
"""
import math

import numpy as np
import pandas as pd
import requests
from shapely.geometry import Polygon

from spring_river.config import RECHARGE_BUFFER_KM, WEST_PLAINS_LATLON
from spring_river.ingest.basin import cell_mask, polygon_bbox
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
        {"date": pd.Series([], dtype="datetime64[ns]"), "pcpn_in": pd.Series([], dtype="float64")}
    )


def _year_chunks(start: str, end: str) -> list[tuple[str, str]]:
    start_ts = pd.Timestamp(start)
    end_ts = pd.Timestamp(end)
    if end_ts < start_ts:
        raise ValueError(f"end ({end}) is before start ({start})")
    chunks = []
    for year in range(start_ts.year, end_ts.year + 1):
        year_start = max(start_ts, pd.Timestamp(year, 1, 1))
        year_end = min(end_ts, pd.Timestamp(year, 12, 31))
        chunks.append((year_start.strftime("%Y-%m-%d"), year_end.strftime("%Y-%m-%d")))
    return chunks


def _grid_latlon(payload: dict) -> tuple[np.ndarray, np.ndarray]:
    meta = payload.get("meta") or {}
    if "lat" not in meta or "lon" not in meta:
        raise RuntimeError("GridData payload has no meta.lat/meta.lon — request must include meta: ['ll']")
    return np.asarray(meta["lat"], dtype="float64"), np.asarray(meta["lon"], dtype="float64")


def _polygon_mask_from_meta(payload: dict, poly: Polygon) -> np.ndarray:
    """ACIS grids are regular in lat/lon: row i has one latitude, column j one longitude."""
    lat, lon = _grid_latlon(payload)
    return cell_mask(lat[:, 0], lon[0, :], poly)


def _mean_grid_series(payload: dict, mask: np.ndarray | None = None) -> pd.DataFrame:
    rows = payload["data"]
    if not rows:
        return _empty_grid_frame()
    dates, means = [], []
    for date_str, grid in rows:
        arr = np.asarray(grid, dtype="float64")
        arr[arr <= -998] = np.nan
        if mask is not None:
            if mask.shape != arr.shape:
                raise ValueError(f"mask {mask.shape} does not match grid {arr.shape}")
            arr = arr[mask]
        dates.append(date_str)
        means.append(np.nan if np.all(np.isnan(arr)) else float(np.nanmean(arr)))
    return pd.DataFrame({"date": pd.to_datetime(dates), "pcpn_in": means})


def _post(body: dict) -> dict:
    resp = requests.post(GRIDDATA_URL, json=body, timeout=300)
    resp.raise_for_status()
    payload = resp.json()
    if "error" in payload:
        raise RuntimeError(f"GridData error: {payload['error']}")
    return payload


def get_basin_pcpn(
    start: str,
    end: str,
    buffer_km: float = RECHARGE_BUFFER_KM,
    polygon: Polygon | None = None,
    refresh: bool = False,
) -> pd.DataFrame:
    if polygon is None:
        lat, lon = WEST_PLAINS_LATLON
        bbox = _bbox_around(lat, lon, buffer_km)
        name = f"prism_basin_pcpn_{int(buffer_km)}km"
        approximation = f"bbox around {int(buffer_km)}km-radius circle centred on West Plains, MO"
    else:
        bbox = polygon_bbox(polygon)
        name = "prism_basin_pcpn_polygon"
        approximation = "cells with centre inside the MoDNR Mammoth Spring recharge polygon"

    def fetch() -> pd.DataFrame:
        frames = []
        mask = None
        for chunk_start, chunk_end in _year_chunks(start, end):
            body = {
                "bbox": ",".join(f"{v:.4f}" for v in bbox),
                "sdate": chunk_start,
                "edate": chunk_end,
                "grid": PRISM_GRID,
                "elems": [{"name": "pcpn"}],
                "meta": ["ll"],
            }
            payload = _post(body)
            if polygon is not None and mask is None:
                mask = _polygon_mask_from_meta(payload, polygon)
                meta["cells_in_polygon"] = int(mask.sum())
                meta["cells_in_bbox"] = int(mask.size)
            frames.append(_mean_grid_series(payload, mask))
        out = pd.concat(frames, ignore_index=True).drop_duplicates("date")
        return out.sort_values("date").reset_index(drop=True)

    meta = {
        "source": "PRISM 4km daily pcpn via ACIS GridData (grid 21)",
        "bbox": bbox,
        "buffer_km": None if polygon is not None else buffer_km,
        "approximation": approximation,
        "start": start,
        "end": end,
    }
    return fetch_cached(name, fetch, meta, refresh=refresh)
