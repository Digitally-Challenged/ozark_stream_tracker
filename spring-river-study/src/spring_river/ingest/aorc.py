"""NOAA AORC v1.1 basin-mean precipitation over the MoDNR recharge polygon.

Source: s3://noaa-nws-aorc-v1-1-1km/{year}.zarr (anonymous), `APCP_surface`
in mm/hr, hourly UTC, 1 km. One zarr store per calendar year; each year's
polygon-masked hourly basin mean is cached as
data/raw/aorc_basin_hourly_{year}.parquet (`time_utc`, `pcpn_mm`). Daily totals
are the 24 h ending `AORC_DAY_END_HOUR_UTC` (12 UTC — the PRISM day) labelled
with the date of the window end; a day with fewer than 24 hours present is NaN.

AORC before 2002 has no radar input (gauge + reanalysis blend); its sub-daily
advantage is 2002→. It shares Stage IV/MRMS and gauge inputs with PRISM, so the
two are not methodologically independent.
"""
from datetime import date

import numpy as np
import pandas as pd

from spring_river.config import (
    AORC_BUCKET,
    AORC_DAY_END_HOUR_UTC,
    AORC_FIRST_YEAR,
    AORC_VAR,
    RECHARGE_POLYGON_PATH,
)
from spring_river.ingest.basin import cell_mask, load_recharge_polygon, polygon_bbox
from spring_river.ingest.cache import fetch_cached

MM_PER_IN = 25.4
HOURS_PER_DAY = 24


def _basin_hourly_mean(da, mask: np.ndarray) -> pd.DataFrame:
    """Unweighted mean over masked cells for every hour. `da` dims (time, latitude, longitude)."""
    values = np.asarray(da.values, dtype="float64")
    if mask.shape != values.shape[1:]:
        raise ValueError(f"mask {mask.shape} does not match grid {values.shape[1:]}")
    masked = values[:, mask]
    mean = np.nanmean(masked, axis=1)
    t = pd.to_datetime(np.asarray(da["time"].values))
    if t.tz is not None:
        t = t.tz_convert("UTC").tz_localize(None)
    return pd.DataFrame({"time_utc": t, "pcpn_mm": mean})


def _open_year_subset(year: int, bbox: tuple[float, float, float, float]):
    import s3fs
    import xarray as xr

    fs = s3fs.S3FileSystem(anon=True)
    ds = xr.open_zarr(fs.get_mapper(f"{AORC_BUCKET}/{year}.zarr"), consolidated=True)
    w, s, e, n = bbox
    return ds[AORC_VAR].sel(latitude=slice(s, n), longitude=slice(w, e))


def _fetch_year(year: int) -> pd.DataFrame:
    poly = load_recharge_polygon(RECHARGE_POLYGON_PATH)
    da = _open_year_subset(year, polygon_bbox(poly))
    mask = cell_mask(da["latitude"].values, da["longitude"].values, poly)
    if mask.sum() == 0:
        raise RuntimeError(f"no AORC cells inside the recharge polygon for {year}")
    frames = []
    for month in range(1, 13):
        chunk = da.sel(time=f"{year}-{month:02d}")
        if chunk.sizes["time"] == 0:
            continue
        frames.append(_basin_hourly_mean(chunk.load(), mask))
    out = pd.concat(frames, ignore_index=True)
    return out.sort_values("time_utc").drop_duplicates("time_utc").reset_index(drop=True)


def get_basin_hourly(year: int, refresh: bool = False) -> pd.DataFrame:
    poly = load_recharge_polygon(RECHARGE_POLYGON_PATH)
    meta = {
        "source": f"NOAA AORC v1.1 {AORC_VAR} (mm/hr) via s3://{AORC_BUCKET}/{year}.zarr, anonymous",
        "basin": "MoDNR Mammoth Spring recharge polygon, unweighted mean of 1 km cells with centre inside",
        "polygon": str(RECHARGE_POLYGON_PATH.name),
        "bbox": polygon_bbox(poly),
        "year": year,
    }
    return fetch_cached(f"aorc_basin_hourly_{year}", lambda: _fetch_year(year), meta, refresh=refresh)


def daily_from_hourly(hourly: pd.DataFrame, day_end_hour_utc: int = AORC_DAY_END_HOUR_UTC) -> pd.DataFrame:
    """24 h ending `day_end_hour_utc`, labelled with the window-end date; NaN unless all 24 hours present."""
    t = pd.to_datetime(hourly["time_utc"])
    label = (t - pd.Timedelta(hours=day_end_hour_utc)).dt.ceil("D")
    g = hourly.assign(date=label).groupby("date")["pcpn_mm"].agg(["sum", "count"])
    pcpn_in = (g["sum"] / MM_PER_IN).where(g["count"] == HOURS_PER_DAY)
    return pd.DataFrame({"date": g.index, "pcpn_in": pcpn_in.to_numpy(dtype="float64")}).reset_index(drop=True)


def get_basin_pcpn(start: str, end: str, refresh: bool = False) -> pd.DataFrame:
    y0 = max(pd.Timestamp(start).year, AORC_FIRST_YEAR)
    y1 = min(pd.Timestamp(end).year, date.today().year)
    hourly = pd.concat([get_basin_hourly(y, refresh=refresh) for y in range(y0, y1 + 1)], ignore_index=True)
    daily = daily_from_hourly(hourly)
    # A day labelled D covers the 24h window ending 12 UTC on D, so it can carry
    # data from the last calendar day of `end`'s year even when labelled D = end+1.
    keep = (daily["date"] >= pd.Timestamp(start)) & (daily["date"] <= pd.Timestamp(end) + pd.Timedelta(days=1))
    return daily[keep].reset_index(drop=True)
