"""Recharge-basin geometry and the single entry point for basin-mean precip.

Second edition (2026-08-25): the basin is the MoDNR Mammoth Spring recharge
polygon (docs/gis/mammoth_spring_recharge_modnr.geojson). Three basin-mean
series can be produced for the same polygon question:

- "aorc"          NOAA AORC v1.1, 1 km hourly, masked to the polygon (primary)
- "prism_polygon" PRISM 4 km daily via ACIS GridData, masked to the polygon
- "prism_buffer"  PRISM 4 km daily over the legacy 30 km West Plains bbox

All three return `date, pcpn_in`; daily totals are the 24 h ending 12 UTC.
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd
import shapely
from shapely.geometry import Polygon, shape

from spring_river.config import BASIN_PRECIP_SOURCE, BASIN_SOURCES, RECHARGE_POLYGON_PATH


def load_recharge_polygon(path: Path = RECHARGE_POLYGON_PATH) -> Polygon:
    gj = json.loads(Path(path).read_text())
    feats = gj["features"]
    if len(feats) != 1:
        raise ValueError(f"expected one feature in {path}, found {len(feats)}")
    poly = shape(feats[0]["geometry"])
    if not poly.is_valid:
        poly = poly.buffer(0)
    return poly


def polygon_bbox(poly: Polygon, pad_deg: float = 0.02) -> tuple[float, float, float, float]:
    """(west, south, east, north) of the polygon padded by `pad_deg`."""
    w, s, e, n = poly.bounds
    return (w - pad_deg, s - pad_deg, e + pad_deg, n + pad_deg)


def cell_mask(lats: np.ndarray, lons: np.ndarray, poly: Polygon) -> np.ndarray:
    """Boolean (len(lats), len(lons)) array: True where the cell centre is inside `poly`."""
    lon_grid, lat_grid = np.meshgrid(np.asarray(lons, dtype="float64"), np.asarray(lats, dtype="float64"))
    return shapely.contains_xy(poly, lon_grid, lat_grid)


LABELS = {
    "aorc": "NOAA AORC v1.1 1 km hourly basin mean over the MoDNR Mammoth Spring recharge polygon "
            "(~349 mi²), daily totals 24 h ending 12 UTC",
    "prism_polygon": "PRISM 4 km daily basin mean over the MoDNR Mammoth Spring recharge polygon (~349 mi²)",
    "prism_buffer": "PRISM 4 km daily mean over the legacy 30 km West Plains buffer bbox (first edition)",
}


def basin_label(source: str = BASIN_PRECIP_SOURCE) -> str:
    return LABELS[source]


def get_basin_pcpn(
    start: str, end: str, source: str = BASIN_PRECIP_SOURCE, refresh: bool = False
) -> pd.DataFrame:
    """Daily basin-mean precip (`date`, `pcpn_in`) for the chosen source."""
    # Local import: aorc and prism both import this module's geometry helpers, so a
    # top-level import here would be a cycle resolved only by statement position.
    from spring_river.ingest import aorc, prism

    if source not in BASIN_SOURCES:
        raise ValueError(f"source {source!r} not in {BASIN_SOURCES}")
    if source == "aorc":
        df = aorc.get_basin_pcpn(start, end, refresh=refresh)
    elif source == "prism_polygon":
        df = prism.get_basin_pcpn(start, end, polygon=load_recharge_polygon(), refresh=refresh)
    else:
        df = prism.get_basin_pcpn(start, end, refresh=refresh)
    return df[["date", "pcpn_in"]].assign(date=pd.to_datetime(df["date"])).reset_index(drop=True)
