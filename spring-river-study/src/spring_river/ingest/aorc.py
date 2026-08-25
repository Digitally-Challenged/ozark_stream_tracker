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

The basin mean is unweighted over the cell centres inside the polygon; over the
polygon's 0.33° latitude span the cos-latitude area bias between the northern
and southern cells is under 0.5 %, so area weighting would not move the mean.

The bucket carries whole calendar years and lags the present by months (2025
was the latest store on 2026-08-25); the daily series therefore ends on 31 Dec
of the latest store. The bucket is listed only when a requested year is not
already cached, so a fully cached basin series needs no network.
"""
import functools
import re
import warnings
from datetime import date
from pathlib import Path

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
from spring_river.ingest import cache
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
    # Local import: keeps the module importable, and the tests fast, without the S3 stack.
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
    if not frames:
        raise RuntimeError(f"AORC {year}.zarr returned no hours in the polygon bbox")
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
    label = (t - pd.Timedelta(day_end_hour_utc, unit="h")).dt.ceil("D")
    g = hourly.assign(date=label).groupby("date")["pcpn_mm"].agg(["sum", "count"])
    pcpn_in = (g["sum"] / MM_PER_IN).where(g["count"] == HOURS_PER_DAY)
    return pd.DataFrame({"date": g.index, "pcpn_in": pcpn_in.to_numpy(dtype="float64")}).reset_index(drop=True)


@functools.lru_cache(maxsize=1)
def available_years() -> tuple[int, ...]:
    """Calendar years with a `{year}.zarr` store in the AORC bucket (one S3 listing, memoized)."""
    # Local import: keeps the module importable, and the tests fast, without the S3 stack.
    import s3fs

    fs = s3fs.S3FileSystem(anon=True)
    years = []
    for path in fs.ls(AORC_BUCKET):
        name = path.rsplit("/", 1)[-1]
        if name.endswith(".zarr") and name[:-5].isdigit():
            years.append(int(name[:-5]))
    if not years:
        raise RuntimeError(f"no {{year}}.zarr stores listed in s3://{AORC_BUCKET}")
    return tuple(sorted(years))


def _cached_year_path(year: int) -> Path:
    return cache.RAW_DIR / f"aorc_basin_hourly_{year}.parquet"


def _newest_cached_year() -> int | None:
    """Newest year with a cached hourly parquet in `RAW_DIR`, or None if there is none."""
    years = [
        int(m.group(1))
        for p in cache.RAW_DIR.glob("aorc_basin_hourly_*.parquet")
        if (m := re.fullmatch(r"aorc_basin_hourly_(\d{4})", p.stem))
    ]
    return max(years) if years else None


def _latest_year(y0: int, y1_req: int) -> int:
    """Clamp the requested last year to what is available, without listing S3 when
    every requested year is already cached (so `make analysis` runs offline)."""
    if all(_cached_year_path(y).exists() for y in range(y0, y1_req + 1)):
        return y1_req
    try:
        return min(y1_req, available_years()[-1])
    except Exception as exc:
        newest = _newest_cached_year()
        if newest is None:
            raise
        warnings.warn(
            f"AORC bucket listing failed ({exc!r}); falling back to the newest cached "
            f"year {newest} in {cache.RAW_DIR}",
            stacklevel=2,
        )
        return min(y1_req, newest)


def get_basin_pcpn(start: str, end: str, refresh: bool = False) -> pd.DataFrame:
    y0 = max(pd.Timestamp(start).year, AORC_FIRST_YEAR)
    y1_req = min(pd.Timestamp(end).year, date.today().year)
    y1 = _latest_year(y0, y1_req)
    if y0 > y1:
        raise ValueError(f"requested {start}..{end} lies outside AORC availability {AORC_FIRST_YEAR}..{y1}")
    hourly = pd.concat([get_basin_hourly(y, refresh=refresh) for y in range(y0, y1 + 1)], ignore_index=True)
    daily = daily_from_hourly(hourly)
    keep = (daily["date"] >= pd.Timestamp(start)) & (daily["date"] <= pd.Timestamp(end))
    return daily[keep].reset_index(drop=True)
