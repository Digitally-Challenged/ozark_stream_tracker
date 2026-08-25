# Spring River study — precipitation second edition (MoDNR polygon + AORC) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the 30 km West Plains PRISM buffer with the MoDNR Mammoth Spring recharge polygon and NOAA AORC v1.1 as the basin precipitation series, add the Alton COOP station, re-run the precipitation-dependent analyses (ledger, Phase 4 Q1/Q4, Phase 6 Q3/coupling), publish a comparison of the three basin series, and republish both artifacts as a second edition.

**Architecture:** A new `ingest/basin.py` owns the polygon geometry (load, bbox, cell mask) and a single dispatcher `get_basin_pcpn(start, end, source)` returning the same `date, pcpn_in` frame for `source ∈ {"aorc", "prism_polygon", "prism_buffer"}`. `ingest/aorc.py` reads the anonymous S3 zarr one year at a time, masks to the polygon, caches the hourly basin mean per year, and derives 12–12 UTC daily totals. `prism.get_basin_pcpn` gains a `polygon` argument that requests the polygon bbox from ACIS GridData with grid lat/lon metadata and masks locally. Every consumer (`hydro/ledger.py`, `analysis/phase4.py`, `analysis/phase6.py`) calls the dispatcher and gets its prose from `basin_label(source)`; the default source is `config.BASIN_PRECIP_SOURCE = "aorc"` (env-overridable). A new `analysis/compare_sources.py` runs the four precipitation-dependent results under all three sources and writes one comparison table that the report's new section reads.

**Tech Stack:** Python 3.12 / `uv`, pandas, numpy, xarray + zarr + s3fs (AORC), shapely (polygon mask), requests (ACIS), pytest, Quarto 1.10.18 (`~/.local/bin/quarto`).

**Spec:** `spring-river-study/docs/handoffs/2026-08-25-precip-edition.md` (task + sequence) and `spring-river-study/docs/precip_sources.md` (source evaluation, access snippet, verdicts). Read both.

## Global Constraints

- Work in the worktree `~/orca/workspaces/ozark_stream_tracker/goatfish` on branch `study/precip-edition` (already created off `origin/main`). All paths below are relative to `spring-river-study/` unless they start with `docs/superpowers`.
- Python `>=3.12,<3.13`; run everything with `uv run …` from `spring-river-study/`. Test gate: `uv run pytest -q` (141 tests pass at start; must stay green).
- Never edit `data/raw`. Never call `refresh=True` on the USGS or existing ACIS caches (`usgs.get_dv`, `acis.get_station_pcpn` for KUNO/USC00238880) — their outputs feed QA/ledger numbers that must not move in this edition.
- Study conventions (`spring-river-study/CLAUDE.md`): water year Oct–Sep; recharge season Sep–Feb; every figure caption carries source, period, approval status; every trend claim carries test, effect size, CI, n; all/approved-only sensitivity with **CHANGED** flags; never interpolate across gaps > 7 days.
- `reports/report.qmd` parses `docs/phase*.md` with asserting regexes (`section`, `doc_re`, `doc_trend`, and `re.search(r"Figure: ([^\n]*)")` captions). Phase-doc wording that the regexes anchor on (listed in Task 5) must not change; anything else may.
- Stage by explicit filename (`git add path/file`); never `git add -A`. The repo has a husky/lint-staged pre-commit hook that runs prettier on HTML — edit `reports/brief.html` in place.
- Conventional commits (`feat(study):`, `fix(study):`, `docs(study):`, `test(study):`). Commit after every task.
- Day definition for gridded daily totals: **the 24 h ending 12:00 UTC**, labelled with the calendar date of the window end (this is PRISM's daily convention; COOP obs days end ~07:00 local = 13:00 UTC).
- Polygon: `docs/gis/mammoth_spring_recharge_modnr.geojson` (one Polygon feature, EPSG:4326; bounds lon −91.954…−91.463, lat 36.496…36.823; MoDNR states 361.08 mi², equal-area recompute ≈ 349 mi²). Cite as "Missouri DNR / Missouri Geological Survey, *Revised Recharge Areas of Selected Springs in the Big Four Region of the Ozarks*, layer modified 2022-09-14".
- AORC: `s3://noaa-nws-aorc-v1-1-1km/{year}.zarr`, anonymous, variable `APCP_surface` in mm/hr, coordinates `time` (hourly UTC), `latitude` ascending, `longitude`. Verified 2026-08-25: bbox subset `latitude=slice(36.45, 36.85), longitude=slice(-91.96, -91.45)` → (8784, 48, 62) for 2020.

---

## File structure

| Path | Responsibility |
|---|---|
| `src/spring_river/config.py` (modify) | `RECHARGE_POLYGON_PATH`, `BASIN_PRECIP_SOURCE`, `BASIN_SOURCES`, `AORC_*` constants, `ALTON_SID` |
| `src/spring_river/ingest/basin.py` (create) | polygon load / bbox / cell mask; `get_basin_pcpn` dispatcher; `basin_label` |
| `src/spring_river/ingest/aorc.py` (create) | AORC S3 zarr → per-year hourly basin mean (cached) → daily 12–12 UTC totals |
| `src/spring_river/ingest/prism.py` (modify) | `get_basin_pcpn(..., polygon=None)`: polygon bbox request with `meta: ["ll"]`, local mask |
| `src/spring_river/ingest/pull_all.py` (modify) | Alton in `PRECIP_SIDS`; pull all three basin sources |
| `src/spring_river/hydro/ledger.py`, `analysis/phase4.py`, `analysis/phase6.py` (modify) | consume the dispatcher; prose from `basin_label` |
| `src/spring_river/analysis/compare_sources.py` (create) | run Q1 / Q4 / Q3 / coupling under each source → `reports/tables/precip_source_comparison.parquet`, `docs/precip_comparison.md`, `reports/figures/precip_sources_annual.png` |
| `tests/test_basin.py`, `tests/test_aorc.py`, `tests/test_compare_sources.py` (create); `tests/test_prism.py`, `tests/test_config.py` (modify) | unit tests, no network |
| `Makefile`, `pyproject.toml` (modify) | `compare` target in `analysis`; new deps |
| `reports/report.qmd`, `reports/brief.html`, `spring_river_research.md`, `CLAUDE.md`, `docs/data_inventory.md` (modify) | second-edition text |

Interfaces shared by every task (defined in Task 1 and Task 2):

```python
# spring_river.ingest.basin
def load_recharge_polygon(path: Path = RECHARGE_POLYGON_PATH) -> shapely.geometry.Polygon
def polygon_bbox(poly, pad_deg: float = 0.02) -> tuple[float, float, float, float]   # (west, south, east, north)
def cell_mask(lats: np.ndarray, lons: np.ndarray, poly) -> np.ndarray               # bool, shape (len(lats), len(lons))
def get_basin_pcpn(start: str, end: str, source: str = BASIN_PRECIP_SOURCE, refresh: bool = False) -> pd.DataFrame  # columns date (datetime64[ns]), pcpn_in (float64)
def basin_label(source: str = BASIN_PRECIP_SOURCE) -> str

# spring_river.ingest.aorc
def daily_from_hourly(hourly: pd.DataFrame, day_end_hour_utc: int = AORC_DAY_END_HOUR_UTC) -> pd.DataFrame  # in: time_utc, pcpn_mm → out: date, pcpn_in
def get_basin_hourly(year: int, refresh: bool = False) -> pd.DataFrame       # time_utc (UTC-naive datetime64[ns]), pcpn_mm
def get_basin_pcpn(start: str, end: str, refresh: bool = False) -> pd.DataFrame  # date, pcpn_in
```

---

### Task 1: Polygon geometry and config constants

**Files:**
- Modify: `src/spring_river/config.py`
- Create: `src/spring_river/ingest/basin.py` (geometry half; the dispatcher is added in Task 5)
- Test: `tests/test_basin.py`, `tests/test_config.py`
- Modify: `pyproject.toml` (add `shapely`)

**Interfaces:**
- Produces: `load_recharge_polygon`, `polygon_bbox`, `cell_mask`; config `RECHARGE_POLYGON_PATH`, `BASIN_PRECIP_SOURCE`, `BASIN_SOURCES`, `AORC_BUCKET`, `AORC_VAR`, `AORC_DAY_END_HOUR_UTC`, `AORC_FIRST_YEAR`, `ALTON_SID`.

- [ ] **Step 1: Add the dependency**

Run from `spring-river-study/`: `uv add "shapely>=2.0,<3"`
Expected: `pyproject.toml` dependencies gain `"shapely>=2.0,<3"`, `uv.lock` updates.

- [ ] **Step 2: Write the failing tests**

`tests/test_basin.py`:

```python
import numpy as np
import pytest
from shapely.geometry import Polygon

from spring_river.config import RECHARGE_POLYGON_PATH
from spring_river.ingest.basin import cell_mask, load_recharge_polygon, polygon_bbox


def test_load_recharge_polygon_bounds_match_modnr_layer():
    poly = load_recharge_polygon(RECHARGE_POLYGON_PATH)
    w, s, e, n = poly.bounds
    assert -91.96 < w < -91.95 and -91.47 < e < -91.46
    assert 36.49 < s < 36.50 and 36.82 < n < 36.83
    assert poly.is_valid


def test_polygon_bbox_pads_bounds():
    poly = Polygon([(-91.9, 36.5), (-91.5, 36.5), (-91.5, 36.8), (-91.9, 36.8)])
    w, s, e, n = polygon_bbox(poly, pad_deg=0.02)
    assert (w, s, e, n) == pytest.approx((-91.92, 36.48, -91.48, 36.82))


def test_cell_mask_marks_centres_inside_only():
    poly = Polygon([(-91.9, 36.5), (-91.5, 36.5), (-91.5, 36.8), (-91.9, 36.8)])
    lats = np.array([36.4, 36.6, 36.9])
    lons = np.array([-92.0, -91.7, -91.4])
    m = cell_mask(lats, lons, poly)
    assert m.shape == (3, 3)
    assert m.sum() == 1 and m[1, 1]


def test_cell_mask_area_roughly_349_sq_mi():
    poly = load_recharge_polygon(RECHARGE_POLYGON_PATH)
    lats = np.arange(36.45, 36.85, 0.01)
    lons = np.arange(-91.96, -91.45, 0.01)
    m = cell_mask(lats, lons, poly)
    # 0.01° cell ≈ 1.113 km × 0.893 km at 36.66° N ≈ 0.994 km²; 349–361 mi² = 904–935 km²
    km2 = m.sum() * 1.113 * 0.893
    assert 850 < km2 < 990
```

Append to `tests/test_config.py`:

```python
def test_basin_source_default_and_choices():
    from spring_river import config

    assert config.BASIN_PRECIP_SOURCE in config.BASIN_SOURCES
    assert config.BASIN_SOURCES == ("aorc", "prism_polygon", "prism_buffer")
    assert config.RECHARGE_POLYGON_PATH.name == "mammoth_spring_recharge_modnr.geojson"
    assert config.AORC_DAY_END_HOUR_UTC == 12
```

- [ ] **Step 3: Run tests to verify they fail**

Run: `uv run pytest tests/test_basin.py tests/test_config.py -q`
Expected: FAIL — `ImportError: cannot import name 'cell_mask'` / `AttributeError: module 'spring_river.config' has no attribute 'BASIN_SOURCES'`.

- [ ] **Step 4: Implement config constants**

Append to `src/spring_river/config.py` (after `RECHARGE_BUFFER_KM`):

```python
import os

# Recharge-basin geometry (second edition, 2026-08-25). MoDNR / Missouri
# Geological Survey "Mammoth Spring Recharge Area" (layer modified 2022-09-14),
# 361.08 mi² per MoDNR, ~349 mi² equal-area recompute. Replaces the 30 km
# West Plains buffer, which is retained only for the comparison edition.
RECHARGE_POLYGON_PATH = PROJECT_ROOT / "docs" / "gis" / "mammoth_spring_recharge_modnr.geojson"
BASIN_SOURCES = ("aorc", "prism_polygon", "prism_buffer")
BASIN_PRECIP_SOURCE = os.environ.get("BASIN_PRECIP_SOURCE", "aorc")
if BASIN_PRECIP_SOURCE not in BASIN_SOURCES:
    raise ValueError(f"BASIN_PRECIP_SOURCE={BASIN_PRECIP_SOURCE!r} not in {BASIN_SOURCES}")

# NOAA AORC v1.1: 1 km hourly, anonymous S3 zarr, APCP_surface in mm/hr.
AORC_BUCKET = "noaa-nws-aorc-v1-1-1km"
AORC_VAR = "APCP_surface"
AORC_FIRST_YEAR = 1981           # study window; product starts 1979
AORC_DAY_END_HOUR_UTC = 12       # daily total = 24 h ending 12 UTC (PRISM day)

ALTON_SID = "USC00230127"        # Alton, MO COOP, 1940→, eastern edge of the polygon
```

Move the `import os` to the top of the file with the other import.

- [ ] **Step 5: Implement the geometry half of `basin.py`**

`src/spring_river/ingest/basin.py`:

```python
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
```

(`get_basin_pcpn` and `basin_label` are appended in Task 5.)

- [ ] **Step 6: Run tests to verify they pass**

Run: `uv run pytest tests/test_basin.py tests/test_config.py -q`
Expected: PASS (5 new tests). Then `uv run pytest -q` → all green.

- [ ] **Step 7: Commit**

```bash
git add spring-river-study/pyproject.toml spring-river-study/uv.lock spring-river-study/src/spring_river/config.py spring-river-study/src/spring_river/ingest/basin.py spring-river-study/tests/test_basin.py spring-river-study/tests/test_config.py
git commit -m "feat(study): MoDNR recharge polygon geometry (load, bbox, cell mask) and basin-source config"
```

---

### Task 2: AORC ingest module

**Files:**
- Create: `src/spring_river/ingest/aorc.py`
- Test: `tests/test_aorc.py`
- Modify: `pyproject.toml` (add `xarray`, `zarr`, `s3fs`)

**Interfaces:**
- Consumes: `basin.load_recharge_polygon`, `basin.polygon_bbox`, `basin.cell_mask`; `cache.fetch_cached`; config `AORC_*`, `START_DATE`.
- Produces: `daily_from_hourly(hourly, day_end_hour_utc)`, `get_basin_hourly(year, refresh)`, `get_basin_pcpn(start, end, refresh)`, `_basin_hourly_mean(da, mask)`.

Network facts (probed 2026-08-25): `xr.open_zarr(s3fs.S3FileSystem(anon=True).get_mapper(f"{AORC_BUCKET}/{year}.zarr"), consolidated=True)` works without dask; a 48-hour bbox subset loaded in ~5 s. Load a year in monthly time slices to bound memory and to keep each S3 request set small. Probed 2026-08-25: a full year loads in ~8 s (zarr chunks 144 × 128 × 256; the bbox spans few chunks), so 46 years ≈ 6–8 min. Run the pull in the background anyway (Task 6).

- [ ] **Step 1: Add dependencies**

Run: `uv add "xarray>=2024.6" "zarr>=2.18,<3" "s3fs>=2024.6"`
Expected: pyproject/uv.lock updated. (zarr 2.x pinned: the bucket's consolidated metadata is zarr v2; if `uv` resolves a zarr 3 that fails to open, pin `<3` explicitly.)

- [ ] **Step 2: Write the failing tests (no network)**

`tests/test_aorc.py`:

```python
import numpy as np
import pandas as pd
import pytest
import xarray as xr

from spring_river.ingest import aorc, cache


@pytest.fixture
def raw_dir(tmp_path, monkeypatch):
    monkeypatch.setattr(cache, "RAW_DIR", tmp_path)
    return tmp_path


def _hourly(start: str, hours: int, value: float = 1.0) -> pd.DataFrame:
    t = pd.date_range(start, periods=hours, freq="h")
    return pd.DataFrame({"time_utc": t, "pcpn_mm": np.full(hours, value)})


def test_daily_from_hourly_sums_24h_ending_12_utc():
    # 2020-01-01 13:00 .. 2020-01-02 12:00 is one complete day labelled 2020-01-02
    h = _hourly("2020-01-01 13:00", 24, value=25.4)
    out = aorc.daily_from_hourly(h)
    assert list(out.columns) == ["date", "pcpn_in"]
    assert out["date"].tolist() == [pd.Timestamp("2020-01-02")]
    assert out["pcpn_in"].iloc[0] == pytest.approx(24.0)


def test_daily_from_hourly_partial_day_is_nan_not_low():
    h = _hourly("2020-01-01 13:00", 30, value=1.0)  # one full day + 6 h of the next
    out = aorc.daily_from_hourly(h)
    assert out["date"].tolist() == [pd.Timestamp("2020-01-02"), pd.Timestamp("2020-01-03")]
    assert out["pcpn_in"].iloc[0] == pytest.approx(24 / 25.4)
    assert np.isnan(out["pcpn_in"].iloc[1])


def test_daily_from_hourly_boundary_hour_belongs_to_ending_day():
    h = pd.DataFrame({"time_utc": [pd.Timestamp("2020-01-02 12:00"), pd.Timestamp("2020-01-02 13:00")],
                      "pcpn_mm": [1.0, 2.0]})
    out = aorc.daily_from_hourly(h)
    # both days incomplete → NaN, but the labels must be 01-02 and 01-03
    assert out["date"].tolist() == [pd.Timestamp("2020-01-02"), pd.Timestamp("2020-01-03")]


def test_basin_hourly_mean_applies_mask():
    t = pd.date_range("2020-01-01", periods=2, freq="h")
    lats = np.array([36.5, 36.6])
    lons = np.array([-91.8, -91.7])
    data = np.array([[[1.0, 2.0], [3.0, 4.0]], [[10.0, 20.0], [30.0, 40.0]]])
    da = xr.DataArray(data, dims=("time", "latitude", "longitude"),
                      coords={"time": t, "latitude": lats, "longitude": lons})
    mask = np.array([[True, False], [False, True]])
    out = aorc._basin_hourly_mean(da, mask)
    assert list(out.columns) == ["time_utc", "pcpn_mm"]
    assert out["pcpn_mm"].tolist() == pytest.approx([2.5, 25.0])
    assert out["time_utc"].dt.tz is None


def test_get_basin_pcpn_concatenates_years_and_uses_cache(raw_dir, monkeypatch):
    calls = []

    def fake_year(year: int, refresh: bool = False) -> pd.DataFrame:
        calls.append(year)
        return _hourly(f"{year}-12-31 13:00", 24, value=25.4)  # one day labelled Jan 1 of year+1

    monkeypatch.setattr(aorc, "get_basin_hourly", fake_year)
    out = aorc.get_basin_pcpn("2019-01-01", "2020-12-31")
    assert calls == [2019, 2020]
    assert out["date"].tolist() == [pd.Timestamp("2020-01-01"), pd.Timestamp("2021-01-01")]
    assert out["pcpn_in"].tolist() == pytest.approx([24.0, 24.0])
```

- [ ] **Step 3: Run tests to verify they fail**

Run: `uv run pytest tests/test_aorc.py -q`
Expected: FAIL with `ModuleNotFoundError: No module named 'spring_river.ingest.aorc'`.

- [ ] **Step 4: Implement `aorc.py`**

```python
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
    keep = (daily["date"] >= pd.Timestamp(start)) & (daily["date"] <= pd.Timestamp(end))
    return daily[keep].reset_index(drop=True)
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `uv run pytest tests/test_aorc.py -q`
Expected: PASS (5 tests).

- [ ] **Step 6: Smoke the network path on one year (writes to the real cache)**

Run from `spring-river-study/`:
`uv run python -c "import time; from spring_river.ingest import aorc; t=time.time(); h=aorc.get_basin_hourly(2020); print(len(h), h['pcpn_mm'].sum()/25.4, round(time.time()-t))"`
Expected: `8784 <annual total ~40–55 in> <seconds>`. Record the seconds in the Task 6 note. If the annual total is outside 30–70 in, stop — the mask or units are wrong.

- [ ] **Step 7: Commit**

```bash
git add spring-river-study/pyproject.toml spring-river-study/uv.lock spring-river-study/src/spring_river/ingest/aorc.py spring-river-study/tests/test_aorc.py
git commit -m "feat(study): AORC v1.1 ingest — polygon-masked hourly basin mean per year, 12 UTC daily totals"
```

---

### Task 3: PRISM recut to the polygon

**Files:**
- Modify: `src/spring_river/ingest/prism.py`
- Test: `tests/test_prism.py`

**Interfaces:**
- Consumes: `basin.polygon_bbox`, `basin.cell_mask`.
- Produces: `prism.get_basin_pcpn(start, end, buffer_km=RECHARGE_BUFFER_KM, polygon=None, refresh=False)`; `_mean_grid_series(payload, mask=None)`; `_grid_latlon(payload) -> (lats_2d, lons_2d)`.

ACIS GridData returns the grid's coordinates when the request carries `"meta": ["ll"]`: `payload["meta"]["lat"]` and `payload["meta"]["lon"]` are 2-D lists with the same shape as each daily grid. Verify the shape once with a 1-day request before relying on it (Step 4).

- [ ] **Step 1: Write the failing tests**

Append to `tests/test_prism.py`:

```python
import numpy as np
from shapely.geometry import Polygon

from spring_river.ingest.prism import _grid_latlon, _polygon_mask_from_meta


def test_grid_latlon_from_meta():
    payload = {"meta": {"lat": [[36.5, 36.5], [36.6, 36.6]], "lon": [[-91.8, -91.7], [-91.8, -91.7]]}, "data": []}
    lat, lon = _grid_latlon(payload)
    assert lat.shape == lon.shape == (2, 2)
    assert lat[1, 0] == 36.6 and lon[0, 1] == -91.7


def test_polygon_mask_from_meta_selects_inside_cells():
    payload = {"meta": {"lat": [[36.5, 36.5], [36.6, 36.6]], "lon": [[-91.8, -91.7], [-91.8, -91.7]]}, "data": []}
    poly = Polygon([(-91.75, 36.55), (-91.65, 36.55), (-91.65, 36.65), (-91.75, 36.65)])
    m = _polygon_mask_from_meta(payload, poly)
    assert m.tolist() == [[False, False], [False, True]]


def test_mean_grid_series_with_mask():
    payload = {"data": [["2020-01-01", [[0.5, 0.7], [-999, 0.9]]]]}
    out = _mean_grid_series(payload, mask=np.array([[False, True], [True, True]]))
    assert math.isclose(out["pcpn_in"].iloc[0], (0.7 + 0.9) / 2)


def test_mean_grid_series_mask_shape_mismatch_raises():
    payload = {"data": [["2020-01-01", [[0.5, 0.7], [0.1, 0.9]]]]}
    with pytest.raises(ValueError):
        _mean_grid_series(payload, mask=np.array([[True, True, True]]))
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/test_prism.py -q`
Expected: FAIL with `ImportError: cannot import name '_grid_latlon'`.

- [ ] **Step 3: Implement**

Replace `prism.py` wholesale with:

```python
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
```

- [ ] **Step 4: Verify the ACIS `meta: ["ll"]` shape with one real 1-day request (no cache write)**

Run: `uv run python -c "
from spring_river.ingest.prism import _post, _grid_latlon, _polygon_mask_from_meta
from spring_river.ingest.basin import load_recharge_polygon, polygon_bbox
p = load_recharge_polygon(); b = polygon_bbox(p)
pay = _post({'bbox': ','.join(f'{v:.4f}' for v in b), 'sdate': '2020-06-01', 'edate': '2020-06-01', 'grid': '21', 'elems': [{'name': 'pcpn'}], 'meta': ['ll']})
lat, lon = _grid_latlon(pay); import numpy as np
print(lat.shape, np.asarray(pay['data'][0][1]).shape, 'rows const lat:', np.allclose(lat, lat[:, [0]]), 'cols const lon:', np.allclose(lon, lon[[0], :]))
print('cells in polygon', int(_polygon_mask_from_meta(pay, p).sum()))
"`
Expected: `lat.shape == data grid shape`, both `True`, cells in polygon ≈ 55–65 (≈ 904 km² / 16 km² per cell). If the rows/cols are not constant, replace `_polygon_mask_from_meta` with `shapely.contains_xy(poly, lon, lat)` on the full 2-D arrays and update the test to match.

- [ ] **Step 5: Run the tests**

Run: `uv run pytest tests/test_prism.py -q` then `uv run pytest -q`
Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add spring-river-study/src/spring_river/ingest/prism.py spring-river-study/tests/test_prism.py
git commit -m "feat(study): PRISM basin mean recut to the MoDNR polygon (ACIS meta ll + local cell mask); buffer kept for comparison"
```

---

### Task 4: Alton COOP station and the data pull

**Files:**
- Modify: `src/spring_river/ingest/pull_all.py`
- Modify: `docs/data_inventory.md` (append one row/paragraph)

**Interfaces:**
- Consumes: `config.ALTON_SID`; Task 5's `basin.get_basin_pcpn` (call it for each source — if Task 5 is not merged yet, call `aorc.get_basin_pcpn`, `prism.get_basin_pcpn(..., polygon=load_recharge_polygon())`, and `prism.get_basin_pcpn(...)` directly).
- Produces: `PRECIP_SIDS = ["KUNO", "USC00238880", ALTON_SID]` — index positions 0 and 1 are relied on by `ledger.py` and `phase6.py`; Alton must be appended, never inserted.

- [ ] **Step 1: Edit `pull_all.py`**

Replace the `PRECIP_SIDS` block and the basin pull:

```python
from spring_river.config import (
    ALTON_SID,
    BASIN_SOURCES,
    PARAM_DISCHARGE,
    PARAM_STAGE,
    SITE_HARDY,
    SITE_IMBODEN,
    SITE_MAMMOTH,
    START_DATE,
)
from spring_river.ingest import acis, basin, nwps, usgs

# Decisions from docs/data_inventory.md (Task 7) + docs/precip_sources.md (2026-08-25):
# - Primary precip = KUNO (West Plains ASOS); secondary = USC00238880 (West Plains COOP);
#   Alton COOP (1940→, eastern edge of the recharge polygon) appended for the second edition.
#   Positions 0 and 1 are load-bearing (ledger, phase6) — append only.
PRECIP_SIDS = ["KUNO", "USC00238880", ALTON_SID]
```

and in `main()` replace the `prism.get_basin_pcpn` call with:

```python
    for source in BASIN_SOURCES:
        df = basin.get_basin_pcpn(START_DATE, end, source=source)
        print(f"basin precip [{source}]: {len(df)} rows, {df['pcpn_in'].isna().sum()} NaN days")
```

- [ ] **Step 2: Pull Alton now (network, ~seconds)**

Run: `uv run python -c "from spring_river.ingest import acis; from spring_river.config import ALTON_SID, START_DATE; from datetime import date; df = acis.get_station_pcpn(ALTON_SID, START_DATE, date.today().isoformat()); print(len(df), df['date'].min().date(), df['date'].max().date(), df['pcpn_in'].isna().mean())"`
Expected: ~16,600 rows, 1981-01-01 → within the last week, NaN fraction < 0.15. Files `data/raw/acis_pcpn_USC00230127.{parquet,meta.json}` appear (git-ignored).

- [ ] **Step 3: Add Alton to `docs/data_inventory.md`**

Append under the precipitation station section:

```markdown
- **USC00230127 Alton, MO COOP** (added 2026-08-25, second edition): daily precip 1940→, active; sits on the eastern edge of the MoDNR recharge polygon. Pulled 1981-01-01→ (cache `acis_pcpn_USC00230127`); rows / NaN fraction recorded in the meta file. Used in Phase 6 as a third station series; not used for `precip_cal_in` (that column stays on USC00238880 for continuity).
```

- [ ] **Step 4: Run tests, commit**

Run: `uv run pytest -q` → PASS.

```bash
git add spring-river-study/src/spring_river/ingest/pull_all.py spring-river-study/docs/data_inventory.md
git commit -m "feat(study): add Alton COOP USC00230127 to the station pull; pull all three basin sources"
```

---

### Task 5: Dispatcher, labels, and consumer swap (ledger, Phase 4, Phase 6)

**Files:**
- Modify: `src/spring_river/ingest/basin.py` (append dispatcher + label)
- Modify: `src/spring_river/hydro/ledger.py`, `src/spring_river/analysis/phase4.py`, `src/spring_river/analysis/phase6.py`
- Test: `tests/test_basin.py` (append)

**Interfaces:**
- Consumes: `aorc.get_basin_pcpn`, `prism.get_basin_pcpn`, `load_recharge_polygon`.
- Produces: `basin.get_basin_pcpn(start, end, source=BASIN_PRECIP_SOURCE, refresh=False)`, `basin.basin_label(source)`.

Phase-doc lines the report regexes anchor on — keep these byte-identical: in `phase4_baseflow.md` the headers `## Q1 attribution`, `### Mammoth`, `### Hardy`, `### BFI trend`, `## Q5 rating drift`, `## Q4 post-flood`; the lines `- Series: source: …`, `- **Residual trend (non-climatic component): …`, `- OLS … R²=…, n=…`, `  - p_trailing_in: … (95% CI … to …)`, `- Pettitt change-point on min7: after WY …`, `- mean post-flood base-flow difference: …% (bootstrap 95% CI … to …); n=… events; … unique control years`, `Pairs: … n=… matched 15-min pairs`. In `phase6_precip.md`: `## {label}: index trends …` headers, the `![indices]…\n\nFigure: …` and `![lag]…\n\nFigure: …` pairs, `- response lag (max r): …`, and the `KUNO vs USC00238880 monthly totals … r=…, ratio COOP/KUNO=…, n=… months` line. Only the free text inside "Figure: …" captions and the series/limitation prose change.

- [ ] **Step 1: Write the failing tests**

Append to `tests/test_basin.py`:

```python
import pandas as pd

from spring_river.ingest import basin


def test_get_basin_pcpn_dispatches_by_source(monkeypatch):
    seen = []
    df = pd.DataFrame({"date": pd.to_datetime(["2020-01-01"]), "pcpn_in": [0.1]})
    monkeypatch.setattr(basin.aorc, "get_basin_pcpn", lambda s, e, refresh=False: (seen.append("aorc"), df)[1])
    monkeypatch.setattr(basin.prism, "get_basin_pcpn",
                        lambda s, e, polygon=None, refresh=False, **kw: (seen.append("polygon" if polygon is not None else "buffer"), df)[1])
    for src in ("aorc", "prism_polygon", "prism_buffer"):
        out = basin.get_basin_pcpn("2020-01-01", "2020-12-31", source=src)
        assert list(out.columns) == ["date", "pcpn_in"]
    assert seen == ["aorc", "polygon", "buffer"]


def test_get_basin_pcpn_rejects_unknown_source():
    with pytest.raises(ValueError):
        basin.get_basin_pcpn("2020-01-01", "2020-12-31", source="daymet")


def test_basin_label_names_geometry_and_product():
    assert "AORC" in basin.basin_label("aorc") and "MoDNR" in basin.basin_label("aorc")
    assert "PRISM" in basin.basin_label("prism_polygon") and "MoDNR" in basin.basin_label("prism_polygon")
    assert "30 km" in basin.basin_label("prism_buffer")
```

- [ ] **Step 2: Run to verify failure**

Run: `uv run pytest tests/test_basin.py -q` → FAIL (`AttributeError: module … has no attribute 'get_basin_pcpn'`).

- [ ] **Step 3: Append the dispatcher to `basin.py`**

```python
from spring_river.ingest import aorc, prism  # noqa: E402  (after the geometry helpers; aorc imports basin's geometry)

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
    if source not in BASIN_SOURCES:
        raise ValueError(f"source {source!r} not in {BASIN_SOURCES}")
    if source == "aorc":
        df = aorc.get_basin_pcpn(start, end, refresh=refresh)
    elif source == "prism_polygon":
        df = prism.get_basin_pcpn(start, end, polygon=load_recharge_polygon(), refresh=refresh)
    else:
        df = prism.get_basin_pcpn(start, end, refresh=refresh)
    return df[["date", "pcpn_in"]].assign(date=pd.to_datetime(df["date"])).reset_index(drop=True)
```

Circular-import check: `aorc.py` imports `cell_mask, load_recharge_polygon, polygon_bbox` from `basin`; `basin` imports `aorc` at module bottom. Python resolves this because `basin`'s geometry names are defined before the `from spring_river.ingest import aorc, prism` line. Run `uv run python -c "import spring_river.ingest.aorc; import spring_river.ingest.basin"` both orders to confirm; if either fails, move the `aorc`/`prism` imports inside `get_basin_pcpn`.

- [ ] **Step 4: Swap `ledger.py`**

In `main()`: replace `from spring_river.ingest import acis, nwps, prism, usgs` with `from spring_river.ingest import acis, basin as basin_mod, nwps, usgs`, replace `basin = prism.get_basin_pcpn(START_DATE, end)` with `basin = basin_mod.get_basin_pcpn(START_DATE, end)`, and change the figure title to
`f"source: USGS discharge/stage/peaks (site {SITE_HARDY}), basin recharge precip = {basin_mod.basin_label()}, ACIS USC00238880 calendar precip; "`.
Update the module docstring sentence "`precip_recharge_in` continues to use the PRISM basin-average grid (Task 5)" → "`precip_recharge_in` uses the basin series selected by `config.BASIN_PRECIP_SOURCE` (AORC over the MoDNR polygon by default; second edition 2026-08-25)".

- [ ] **Step 5: Swap `phase4.py`**

- Import: `from spring_river.ingest import basin as basin_mod, oni, usgs` (drop `prism`); `from spring_river.config import BASIN_PRECIP_SOURCE` added to the config import list.
- `main()`: `basin = basin_mod.get_basin_pcpn(START_DATE, end)`.
- Header line: replace `f"Basin precip: PRISM 30 km buffer around West Plains, {basin['date'].min().date()}–…"` with `f"Basin precip: {basin_mod.basin_label()} [{BASIN_PRECIP_SOURCE}], {basin['date'].min().date()}–{basin['date'].max().date()}; "`.
- Limitations: replace `"- Basin precip is the 30 km West Plains PRISM buffer, not a dye-traced recharge polygon."` with `f"- Basin precip: {basin_mod.basin_label()}. The polygon excludes recharge shared with Bill Mac and Greer springs (separate MoDNR layers). AORC before 2002 has no radar input and shares gauge/Stage IV inputs with PRISM, so the two grids are not independent."`.

- [ ] **Step 6: Swap `phase6.py` and add Alton**

- Imports: `from spring_river.ingest import acis, basin as basin_mod, usgs`; `from spring_river.config import BASIN_PRECIP_SOURCE, …`.
- Add `ALTON_SID = PRECIP_SIDS[2]` next to `COOP_SID`/`KUNO_SID`.
- `main()`: `basin = basin_mod.get_basin_pcpn(START_DATE, end)`; `alton = acis.get_station_pcpn(ALTON_SID, START_DATE, end)`.
- Series line: append `f", {ALTON_SID} Alton COOP ({_series_span(alton)}), basin = {basin_mod.basin_label()} ({_series_span(basin)})"` and remove the `PRISM 30 km basin mean (…)` fragment.
- Trend loop: `for label, df in ((COOP_SID, coop), ("KUNO", kuno), (ALTON_SID, alton), ("basin", basin)):` (the `basin` label string must stay `"basin"` — `phase6_indices_basin.parquet` and the qmd depend on it).
- `_divergence_note`: replace the PRISM bullet with `f"- Basin values are {basin_mod.basin_label()}; station gaps enter a gridded product only through its gauge blending. Treat the basin trends as the Q3 headline and the station tests as a consistency check."` (pass nothing new — `basin_label()` uses the config default).
- `_lag_figure` title: `f"USGS DV {SITE_MAMMOTH} + basin precip [{BASIN_PRECIP_SOURCE}]; …"`.
- Lag figure caption: `f"Figure: {caption(f'USGS DV {SITE_MAMMOTH} + {basin_mod.basin_label()}', mammoth)}."`.
- Limitations: replace `"- Station indices are point measurements; basin indices are a 4 km grid mean (smoother extremes by construction)."` with `f"- Station indices are point measurements; basin indices are a gridded areal mean ({basin_mod.basin_label()}) — smoother extremes by construction."`.

- [ ] **Step 7: Run tests and the three runners on the default source**

Run: `uv run pytest -q` → PASS.
Run: `make ledger phase4 phase6` (needs the AORC cache from Task 6 for every year 1981→today — if Task 6 has not finished, run with `BASIN_PRECIP_SOURCE=prism_polygon make ledger phase4 phase6` to validate the plumbing, then re-run on `aorc` after Task 6).
Expected: `docs/phase4_baseflow.md` header reads `Basin precip: NOAA AORC v1.1 … [aorc]`; `docs/phase6_precip.md` has four `index trends` sections (USC00238880, KUNO, USC00230127, basin); no exception.

- [ ] **Step 8: Commit**

```bash
git add spring-river-study/src/spring_river/ingest/basin.py spring-river-study/src/spring_river/hydro/ledger.py spring-river-study/src/spring_river/analysis/phase4.py spring-river-study/src/spring_river/analysis/phase6.py spring-river-study/tests/test_basin.py
git commit -m "feat(study): basin-precip dispatcher (aorc | prism_polygon | prism_buffer); ledger, Phase 4 and Phase 6 read it; Alton in Phase 6"
```

Do not commit the regenerated `docs/phase*.md` yet — they are regenerated again in Task 7 after all data are in.

---

### Task 6: Pull the AORC record (background, network)

**Files:** none in git (`data/raw` is ignored). Produces `data/raw/aorc_basin_hourly_{1981..2026}.parquet`, `data/raw/prism_basin_pcpn_polygon.parquet`, `data/raw/acis_pcpn_USC00230127.parquet`.

- [ ] **Step 1: Start the pull in the background**

Run from `spring-river-study/` (background, timeout 600 s per call is not enough — use `run_in_background` and poll):
`uv run python -m spring_river.ingest.pull_all > /private/tmp/claude-501/-Users-COLEMAN-orca-workspaces-ozark-stream-tracker-goatfish/c3f6ce55-ea99-41db-b63e-c5b903b8fa85/scratchpad/pull_all.log 2>&1`
Expected: USGS/ACIS/NWPS lines are instant (cached); `basin precip [aorc]` takes 46 × (Task 2 Step 6 seconds). If S3 drops mid-run, re-run — each completed year is cached.

- [ ] **Step 2: Verify the pulled series**

Run: `uv run python -c "
from spring_river.ingest import basin
from datetime import date
for s in basin.BASIN_SOURCES:
    d = basin.get_basin_pcpn('1981-01-01', date.today().isoformat(), source=s)
    a = d.set_index('date')['pcpn_in'].resample('YS').sum(min_count=360)
    print(s, len(d), d['date'].min().date(), d['date'].max().date(), 'NaN days', int(d['pcpn_in'].isna().sum()), 'mean annual in', round(a.dropna().mean(), 1))
"`
Expected: all three ~16,600 rows from 1981-01-01; AORC ends within ~10 days of today; mean annual ≈ 44–50 in for the two polygon series, the buffer a little lower/higher but within ±10 %. AORC NaN days: only the final partial day. If AORC's mean annual differs from PRISM-polygon by > 15 %, stop and check units/mask before proceeding.

- [ ] **Step 3: Record**

Add the run time and the three mean-annual numbers to `spring_river_research.md` in Task 8's section (keep a note now in the scratchpad).

---

### Task 7: Source comparison runner

**Files:**
- Create: `src/spring_river/analysis/compare_sources.py`
- Test: `tests/test_compare_sources.py`
- Modify: `Makefile` (`compare` target; `analysis: ledger phase4 phase5 phase6 phase7 compare`)

**Interfaces:**
- Consumes: `basin.get_basin_pcpn`, `basin.basin_label`, `lowflow.attribution_table/fit_attribution`, `postflood.matched_comparison/paired_summary`, `intensity.annual_indices/index_trends`, `coupling.monthly_series/lag_correlation/response_lag`, `phase4._major_flood_dates`, `oni.get_oni`, `usgs.get_dv/get_peaks`.
- Produces: `reports/tables/precip_source_comparison.parquet` with columns `source, block, metric, value, lo, hi, n` (block ∈ {q1_mammoth, q1_hardy, q4_mammoth, q4_hardy, q3, coupling, agreement}); `docs/precip_comparison.md`; `reports/figures/precip_sources_annual.png`. Pure helpers: `compare_rows(source, series, basin, oni_df, majors) -> list[dict]`, `agreement_rows(a_name, a, b_name, b) -> list[dict]`, `to_markdown_table(df) -> str`.

- [ ] **Step 1: Write the failing tests (synthetic data, no network)**

`tests/test_compare_sources.py`:

```python
import numpy as np
import pandas as pd

from spring_river.analysis.compare_sources import agreement_rows, to_markdown_table


def _daily(seed: int, scale: float) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    d = pd.date_range("2000-01-01", "2004-12-31", freq="D")
    return pd.DataFrame({"date": d, "pcpn_in": rng.gamma(0.5, scale, len(d))})


def test_agreement_rows_report_annual_r_and_ratio():
    a = _daily(0, 0.2)
    b = a.assign(pcpn_in=a["pcpn_in"] * 1.1)
    rows = agreement_rows("aorc", a, "prism_polygon", b)
    by = {r["metric"]: r for r in rows}
    assert by["annual_total_r"]["value"] > 0.99
    assert abs(by["annual_total_ratio"]["value"] - 1.1) < 1e-6
    assert by["daily_r"]["value"] > 0.99
    assert all(r["source"] == "aorc vs prism_polygon" and r["block"] == "agreement" for r in rows)
    assert by["annual_total_r"]["n"] == 5


def test_to_markdown_table_pivots_sources_wide():
    df = pd.DataFrame([
        {"source": "aorc", "block": "q3", "metric": "total_in slope/decade", "value": 2.0, "lo": 0.5, "hi": 3.5, "n": 45},
        {"source": "prism_buffer", "block": "q3", "metric": "total_in slope/decade", "value": 2.4, "lo": 0.4, "hi": 4.5, "n": 45},
    ])
    md = to_markdown_table(df)
    assert "| metric" in md and "aorc" in md and "prism_buffer" in md
    assert "2.0 (0.5 to 3.5; n=45)" in md and "2.4 (0.4 to 4.5; n=45)" in md
```

- [ ] **Step 2: Run to verify failure**

Run: `uv run pytest tests/test_compare_sources.py -q` → FAIL (`ModuleNotFoundError`).

- [ ] **Step 3: Implement**

`src/spring_river/analysis/compare_sources.py`:

```python
"""Second-edition comparison: every precipitation-dependent result under each
basin source (aorc | prism_polygon | prism_buffer). Writes one long table,
a markdown summary and a figure. Uses the same functions as the phase
runners so a number here equals the phase doc's number for the default source.
"""
from datetime import date

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from spring_river.analysis.phase4 import _major_flood_dates
from spring_river.climate.coupling import lag_correlation, monthly_series, response_lag
from spring_river.climate.intensity import annual_indices, index_trends
from spring_river.config import (
    BASIN_PRECIP_SOURCE,
    BASIN_SOURCES,
    DOCS_DIR,
    FIGURES_DIR,
    PARAM_DISCHARGE,
    SITE_HARDY,
    SITE_MAMMOTH,
    START_DATE,
    TABLES_DIR,
)
from spring_river.hydro.lowflow import attribution_table, fit_attribution
from spring_river.hydro.postflood import matched_comparison, paired_summary
from spring_river.ingest import basin as basin_mod, oni, usgs

Q3_INDICES = ("total_in", "recharge_in", "max1_in", "sdii_in")
N_BOOT = 1000


def _row(source: str, block: str, metric: str, value: float, lo: float = np.nan, hi: float = np.nan, n: int | None = None) -> dict:
    return {"source": source, "block": block, "metric": metric, "value": float(value), "lo": float(lo), "hi": float(hi),
            "n": None if n is None else int(n)}


def _q1_rows(source: str, label: str, q: pd.DataFrame, basin: pd.DataFrame, oni_df: pd.DataFrame) -> list[dict]:
    fit = fit_attribution(attribution_table(q, basin, oni_df))
    blk = f"q1_{label}"
    lo, hi = fit.ci["p_trailing_in"]
    rt = fit.residual_trend
    return [
        _row(source, blk, "p_trailing_in coef (log-cfs/in)", fit.coef["p_trailing_in"], lo, hi, fit.n),
        _row(source, blk, "OLS R²", fit.r2, n=fit.n),
        _row(source, blk, "residual trend (log-cfs/yr)", rt.slope, rt.slope_lo, rt.slope_hi, rt.n),
    ]


def _q4_rows(source: str, label: str, q: pd.DataFrame, basin: pd.DataFrame, majors: pd.Series) -> list[dict]:
    s = paired_summary(matched_comparison(q, basin, majors))
    return [_row(source, f"q4_{label}", "post-flood base-flow diff (%)", s["mean_diff_pct"], s["lo"], s["hi"], s["n"])]


def _q3_rows(source: str, basin: pd.DataFrame) -> list[dict]:
    tr = index_trends(annual_indices(basin)).set_index("index")
    out = []
    for k in Q3_INDICES:
        r = tr.loc[k]
        out.append(_row(source, "q3", f"{k} slope/decade", r["slope_per_decade"], r["lo"], r["hi"], r["n"]))
        out.append(_row(source, "q3", f"{k} BH-significant", float(bool(r["significant_bh"])), n=r["n"]))
    return out


def _coupling_rows(source: str, basin: pd.DataFrame, mammoth: pd.DataFrame) -> list[dict]:
    lc = lag_correlation(monthly_series(basin, mammoth), n_boot=N_BOOT)
    best = response_lag(lc)
    r = lc.loc[lc["lag"] == best].iloc[0]
    return [_row(source, "coupling", "response lag (months)", best, n=r["n"]),
            _row(source, "coupling", "r at response lag", r["r"], r["r_lo"], r["r_hi"], r["n"])]


def compare_rows(source: str, series: dict[str, pd.DataFrame], basin: pd.DataFrame, oni_df: pd.DataFrame,
                 majors: pd.Series) -> list[dict]:
    rows = []
    for label, q in series.items():
        rows += _q1_rows(source, label, q, basin, oni_df)
        rows += _q4_rows(source, label, q, basin, majors)
    rows += _q3_rows(source, basin)
    rows += _coupling_rows(source, basin, series["mammoth"])
    return rows


def agreement_rows(a_name: str, a: pd.DataFrame, b_name: str, b: pd.DataFrame) -> list[dict]:
    j = a.merge(b, on="date", suffixes=("_a", "_b")).dropna()
    ya = j.set_index("date")["pcpn_in_a"].resample("YS").agg(["sum", "count"])
    yb = j.set_index("date")["pcpn_in_b"].resample("YS").agg(["sum", "count"])
    full = (ya["count"] >= 360) & (yb["count"] >= 360)
    ya, yb = ya.loc[full, "sum"], yb.loc[full, "sum"]
    src = f"{a_name} vs {b_name}"
    return [
        _row(src, "agreement", "daily_r", np.corrcoef(j["pcpn_in_a"], j["pcpn_in_b"])[0, 1], n=len(j)),
        _row(src, "agreement", "annual_total_r", np.corrcoef(ya, yb)[0, 1], n=len(ya)),
        _row(src, "agreement", "annual_total_ratio", yb.sum() / ya.sum(), n=len(ya)),
        _row(src, "agreement", f"{a_name} mean annual (in)", ya.mean(), n=len(ya)),
        _row(src, "agreement", f"{b_name} mean annual (in)", yb.mean(), n=len(yb)),
    ]


def _cell(r: pd.Series) -> str:
    if r["metric"].endswith("BH-significant"):
        return "yes" if r["value"] else "no"
    s = f"{r['value']:.3g}"
    if pd.notna(r["lo"]):
        s += f" ({r['lo']:.3g} to {r['hi']:.3g}"
        s += f"; n={int(r['n'])})" if pd.notna(r["n"]) else ")"
    elif pd.notna(r["n"]):
        s += f" (n={int(r['n'])})"
    return s


def to_markdown_table(df: pd.DataFrame) -> str:
    d = df.assign(cell=df.apply(_cell, axis=1))
    wide = d.pivot_table(index=["block", "metric"], columns="source", values="cell", aggfunc="first", sort=False)
    wide = wide.reindex(columns=[s for s in BASIN_SOURCES if s in wide.columns])
    return wide.reset_index().to_markdown(index=False)


def _figure(basins: dict[str, pd.DataFrame]) -> None:
    fig, ax = plt.subplots(figsize=(10, 4))
    for s, b in basins.items():
        a = b.set_index("date")["pcpn_in"].resample("YS").sum(min_count=360)
        ax.plot(a.index.year, a.values, marker="o", ms=3, label=s)
    ax.set_ylabel("calendar-year total (in)"); ax.set_xlabel("year"); ax.legend()
    ax.set_title("Basin precipitation by source; period 1981–present; no approval flag applies", fontsize=9)
    fig.tight_layout(); fig.savefig(FIGURES_DIR / "precip_sources_annual.png", dpi=150); plt.close(fig)


def main() -> None:
    end = date.today().isoformat()
    TABLES_DIR.mkdir(parents=True, exist_ok=True); FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    oni_df = oni.get_oni()
    series = {"mammoth": usgs.get_dv(SITE_MAMMOTH, PARAM_DISCHARGE, START_DATE, end),
              "hardy": usgs.get_dv(SITE_HARDY, PARAM_DISCHARGE, START_DATE, end)}
    majors = _major_flood_dates(usgs.get_peaks(SITE_HARDY))
    basins = {s: basin_mod.get_basin_pcpn(START_DATE, end, source=s) for s in BASIN_SOURCES}
    rows = []
    for s, b in basins.items():
        rows += compare_rows(s, series, b, oni_df, majors)
    rows += agreement_rows("aorc", basins["aorc"], "prism_polygon", basins["prism_polygon"])
    rows += agreement_rows("prism_polygon", basins["prism_polygon"], "prism_buffer", basins["prism_buffer"])
    df = pd.DataFrame(rows)
    df.to_parquet(TABLES_DIR / "precip_source_comparison.parquet")
    _figure(basins)
    lines = [f"# Basin precipitation source comparison — generated {date.today().isoformat()}", "",
             f"Default source for this edition: `{BASIN_PRECIP_SOURCE}`. Sources:", ""]
    lines += [f"- `{s}`: {basin_mod.basin_label(s)} ({b['date'].min().date()}–{b['date'].max().date()})" for s, b in basins.items()]
    lines += ["", "Same code paths as Phases 4 and 6 (all-data variant). Q1 = OLS p_trailing coefficient, R², residual Sen trend; "
              "Q4 = mean 6-month post-flood base-flow difference vs matched controls; Q3 = Sen slope per decade with BH flag; "
              "coupling = monthly anomaly lag correlation with block-bootstrap CI.", "",
              to_markdown_table(df[df["block"] != "agreement"]), "", "## Agreement between sources", "",
              to_markdown_table(df[df["block"] == "agreement"]), "",
              "![sources](../reports/figures/precip_sources_annual.png)", ""]
    (DOCS_DIR / "precip_comparison.md").write_text("\n".join(lines))
    print(f"wrote {DOCS_DIR / 'precip_comparison.md'} ({len(df)} rows)")


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Makefile**

Add after `phase7:`:

```make
compare:
	uv run python -m spring_river.analysis.compare_sources
```

change `analysis: ledger phase4 phase5 phase6 phase7` to `analysis: ledger phase4 phase5 phase6 phase7 compare`, and add `compare` to `.PHONY`.

- [ ] **Step 5: Run tests, then the runner**

Run: `uv run pytest -q` → PASS. Then `make compare` (needs Task 6 complete; ~3 × lag bootstrap ≈ a few minutes).
Expected: `docs/precip_comparison.md` with two tables and three source columns; `reports/tables/precip_source_comparison.parquet`.

Sanity: the `aorc` column's Q1/Q4/Q3/coupling numbers must equal the ones in `docs/phase4_baseflow.md` / `docs/phase6_precip.md` after `make analysis` (same functions, same data). Check two by eye.

- [ ] **Step 6: Commit**

```bash
git add spring-river-study/src/spring_river/analysis/compare_sources.py spring-river-study/tests/test_compare_sources.py spring-river-study/Makefile
git commit -m "feat(study): basin-source comparison runner (Q1/Q4/Q3/coupling under aorc, prism_polygon, prism_buffer)"
```

---

### Task 8: Regenerate, record decisions, update report and brief

**Files:**
- Regenerate (commit): `docs/phase4_baseflow.md`, `docs/phase6_precip.md`, `docs/precip_comparison.md`, `reports/tables/*.parquet`, `reports/figures/*.png`, `data/processed/annual_ledger.parquet` (check which of these are tracked with `git ls-files reports/tables data/processed | head`; commit only what is already tracked plus the new `precip_source_comparison.parquet` and `precip_sources_annual.png` if tables/figures are tracked).
- Modify: `spring_river_research.md`, `reports/report.qmd`, `reports/brief.html`, `CLAUDE.md` (study), `docs/handoffs/2026-08-25-precip-edition.md` (mark done).

- [ ] **Step 1: `make analysis`** (default source `aorc`). Expected: all runners complete; note every headline that moved versus the first edition (Q1 coefficients / residual trend, Q4 %, Q3 basin slopes and BH flags, coupling lag/r, ledger `precip_recharge_in`). Sensitivity (all vs approved-only) is re-run by the same code path — grep the two phase docs for `**CHANGED**` and list any hits.

- [ ] **Step 2: `spring_river_research.md`** — append:

```markdown
## Second edition — basin precipitation on the MoDNR polygon and AORC — 2026-08-2X

Decisions: basin = MoDNR Mammoth Spring recharge polygon (docs/gis/…, ~349 mi², SE of West Plains); primary
basin series = NOAA AORC v1.1 (1 km hourly, 12 UTC days); PRISM recut to the polygon as second opinion; the
30 km buffer retained only for comparison; Alton COOP USC00230127 added to Phase 6. `config.BASIN_PRECIP_SOURCE`
selects the series (env-overridable); `make compare` writes docs/precip_comparison.md.

AORC pull: 46 years in <N> min; mean annual (1981–2025) aorc <x> in, prism_polygon <y> in, prism_buffer <z> in;
annual-total r aorc/prism_polygon = <r>, ratio = <ratio>.

### What changed (first edition → second edition, all-data variant)

<paste the non-agreement table from docs/precip_comparison.md, adding a "first edition" column copied from the
Phase 4–6 headline table above>

Interpretation: <2–4 sentences: did the precip coefficients tighten and coupling r rise as predicted in
docs/precip_sources.md? did any BH flag flip? did any all/approved-only CHANGED flag appear?>
```

Then update the **Headline results** table rows Q1, Q3 (and Q4 if it moved) with the second-edition numbers, marking "(2nd ed.)".

- [ ] **Step 3: `reports/report.qmd`** edits (numbers stay dynamic; only prose and one new section):

1. Title block: add `subtitle: "Second edition — MoDNR recharge polygon and AORC basin precipitation"` (or append to the existing subtitle) and bump the date.
2. Setup chunk: after `ledger = …` add
   ```python
   cmp = tbl("precip_source_comparison")
   def cmp_val(source, block, metric):
       r = cmp[(cmp.source == source) & (cmp.block == block) & (cmp.metric == metric)].iloc[0]
       return r
   agree = cmp_val("aorc vs prism_polygon", "agreement", "annual_total_r")
   ratio = cmp_val("aorc vs prism_polygon", "agreement", "annual_total_ratio")
   ```
3. Abstract: `Basin (PRISM) precipitation rose` → `Basin (AORC, MoDNR recharge polygon) precipitation rose`.
4. Setting bullet (line ~429): replace with
   `- **Recharge basin.** The MoDNR / Missouri Geological Survey "Mammoth Spring Recharge Area" polygon (revised layer 2022-09-14; 361 mi² stated, ~349 mi² equal-area), south-east of West Plains toward Alton and Thayer. Basin precipitation is the NOAA AORC v1.1 1 km hourly analysis averaged over the polygon (daily totals are the 24 h ending 12 UTC); PRISM 4 km over the same polygon is the second opinion (§7.1). The first edition's 30 km West Plains buffer was ~3× the polygon's area and offset north-west. Station series: USC00238880 West Plains COOP (1981+ in this build), KUNO West Plains ASOS (1998-04+), USC00230127 Alton COOP (1981+ pulled; record from 1940).`
5. Ledger figure caption: `PRISM 30 km basin mean` → `AORC basin mean over the MoDNR polygon`.
6. Q1 limitation (line ~487): drop `; basin precipitation is a 30 km buffer, not a traced recharge polygon` and add `; AORC before 2002 is a gauge/reanalysis blend without radar`.
7. Precipitation section bullet (line ~654): `Basin (PRISM 30 km mean, n = …)` → `Basin (AORC, MoDNR polygon, n = …)`; limitation (line ~660): `PRISM is a 4 km grid mean` → `AORC is a 1 km gridded analysis blending Stage IV/MRMS radar (2002+), gauges and reanalysis, averaged over the polygon`; add `Alton USC00230127: ` + its sig count using `sig_count['USC00230127']` (add that key wherever `sig_count` is built — it comes from `phase6_index_trends.parquet`, which now carries the Alton series).
8. New subsection after the Precipitation regime's limitation, before "## Seasonality and recession":
   ````markdown
   ## What changed with the polygon and AORC

   The first edition averaged PRISM over a 30 km buffer around West Plains. This edition uses the MoDNR recharge polygon and AORC; @tbl-sources repeats every precipitation-dependent result under all three basin series (same code, all-data variant). AORC and PRISM annual totals over the polygon agree (r = `{python} g(agree['value'], 3)`, ratio PRISM/AORC = `{python} g(ratio['value'], 3)`, n = `{python} int(agree['n'])` years).

   ```{python}
   #| label: tbl-sources
   #| tbl-cap: "Precipitation-dependent results by basin source (reports/tables/precip_source_comparison.parquet). Cells: estimate (95 % CI; n)."
   from spring_river.analysis.compare_sources import to_markdown_table
   Markdown(to_markdown_table(cmp[cmp.block != "agreement"]))
   ```

   <two sentences stating which conclusions moved and which did not, written from the table after Step 1 — no number typed by hand>

   ![Calendar-year basin precipitation under the three sources; period 1981–present; no approval flag applies.](figures/precip_sources_annual.png){#fig-sources}
   ````
   (Import `Markdown` is already in the setup chunk — `show()` returns one. If `to_markdown_table` cannot be imported inside Quarto, copy the function body into the chunk.)
9. Limitations "Unobtained inputs": replace the polygon bullet with `- Recharge polygon: MoDNR layer, not a study-specific dye trace; recharge shared with Bill Mac and Greer springs is excluded.`; in "Methods" replace `(PRISM basin series is complete)` with `(basin series are complete)`.
10. Code references row: `spring_river.ingest.{usgs,acis,prism,oni,nwps}` → `spring_river.ingest.{usgs,acis,prism,aorc,basin,oni,nwps}`; add `| spring_river.analysis.compare_sources | basin-source comparison table |`.
11. Review record: append `Second edition (2026-08-2X): basin geometry and series replaced; comparison in §7.1; Codex pass <summary>.`

- [ ] **Step 4: `make report`** — Expected: renders without assertion errors. If a `doc_re` assertion fails, the phase-doc wording drifted from the Task 5 list — fix the runner prose, not the regex.

- [ ] **Step 5: `reports/brief.html`** — hand edits (numbers from the regenerated tables/phase docs, not from memory):
   - Figure captions at ~lines 508 and 659: `PRISM 4-km rain averaged over a 30-km circle around West Plains, MO` → `NOAA AORC 1-km rain averaged over the Missouri DNR Mammoth Spring recharge area`; update the Sen slope / CI / n in the rain caption and the "9 of 10 intensity indices" sentence to the new basin numbers.
   - Caveat bullet at ~line 745: `The rain trend is a model product. PRISM blends stations into a grid.` → `The rain trend is a model product. AORC blends radar (from 2002), rain gauges and a weather reanalysis into a grid; PRISM, a second blend over the same area, gives the same direction (see the technical report's source comparison).`
   - Any headline number in the brief that moved in Step 1 (Q1 residual %/yr, Q3 slope, Q4 %, coupling lag) — update the text and the inline SVG data arrays that draw them (search the `<script>` for the affected series; the arrays are typed from `reports/tables`).
   - Add one line near the top: "Second edition, <date>: recharge area and rainfall data replaced — see 'What changed'." and a short "What changed" paragraph.

- [ ] **Step 6: `CLAUDE.md` (study)** — Analysis-order paragraph: add `Second edition 2026-08-2X: basin precip via ingest/basin.py (config.BASIN_PRECIP_SOURCE, default aorc); make compare → docs/precip_comparison.md.` Handoff doc: prepend `Status: implemented 2026-08-2X on study/precip-edition — see docs/superpowers/plans/2026-08-25-spring-river-precip-edition.md.`

- [ ] **Step 7: Commit (explicit files only)**

```bash
git add spring-river-study/spring_river_research.md spring-river-study/reports/report.qmd spring-river-study/reports/brief.html spring-river-study/CLAUDE.md spring-river-study/docs/handoffs/2026-08-25-precip-edition.md spring-river-study/docs/phase4_baseflow.md spring-river-study/docs/phase6_precip.md spring-river-study/docs/precip_comparison.md
git add $(git ls-files spring-river-study/reports/tables spring-river-study/reports/figures spring-river-study/data/processed spring-river-study/docs/phase5_floods.md spring-river-study/docs/phase7_seasonality.md)   # only already-tracked outputs
git status --short   # confirm nothing under data/raw and no stray files
git commit -m "docs(study): second edition — polygon + AORC results, comparison section, brief and decisions updated"
```

If `reports/tables/precip_source_comparison.parquet` / `reports/figures/precip_sources_annual.png` are in a tracked directory, `git add` them by name too.

---

### Task 9: Verification, adversarial review, merge, publish

- [ ] **Step 1: Fresh-clone check**

```bash
cd /private/tmp/claude-501/-Users-COLEMAN-orca-workspaces-ozark-stream-tracker-goatfish/c3f6ce55-ea99-41db-b63e-c5b903b8fa85/scratchpad && rm -rf fresh && git clone -q --branch study/precip-edition ~/orca/workspaces/ozark_stream_tracker/goatfish fresh
cp -R ~/orca/workspaces/ozark_stream_tracker/goatfish/spring-river-study/data/raw fresh/spring-river-study/data/raw
cd fresh/spring-river-study && uv sync -q && uv run pytest -q && make report 2>&1 | tail -5
diff <(sed 's/generated [0-9-]*//' docs/phase4_baseflow.md) <(sed 's/generated [0-9-]*//' ~/orca/workspaces/ozark_stream_tracker/goatfish/spring-river-study/docs/phase4_baseflow.md) && echo IDENTICAL
```
Expected: tests pass, report renders, phase docs identical.

- [ ] **Step 2: Codex adversarial pass** — invoke the `codex-signoff` skill on the whole branch (`git diff origin/main...HEAD`), with the problem statement: basin geometry and precipitation series replaced; asks: (a) is the 12 UTC day alignment right for AORC end-of-hour stamps and consistent with PRISM/COOP; (b) is the polygon mask applied to the right axes (lat rows, lon cols) in both AORC and ACIS; (c) does any regex-anchored phase-doc line change; (d) does the comparison table use the identical code path as the phase runners; (e) anything missed. Fix blocking findings, re-run `make report`, commit as `fix(study): codex review — …`. Record the findings in `docs/review_phase4-6.md` under a new `## Second edition review (2026-08-2X)` header.

- [ ] **Step 3: Merge and push**

```bash
cd ~/orca/workspaces/ozark_stream_tracker/goatfish && git checkout main && git pull --ff-only && git merge --no-ff study/precip-edition -m "Merge branch 'study/precip-edition': MoDNR recharge polygon + AORC basin precipitation, source comparison, second-edition report" && git push
```
(Nick's standing rule: side-effecting pushes are within the handoff's explicit scope — the handoff says "merge with a merge commit, push, republish both artifacts".)

- [ ] **Step 4: Republish both artifacts to the SAME URLs**

Technical report: extract from `reports/report.html` — strip `<meta>`/`<title>` from `<head>`, keep its `<style>`/`<script>`, wrap the body in a `<div>`, add `<title>Spring River at Hardy — Hydrologic Regime, 2nd ed.</title>` — write to the scratchpad and call `Artifact` with `url: https://claude.ai/code/artifact/a1dc172c-1984-4789-9ca4-cb3ba474b90c`, favicon unchanged from the first edition, `label: "second-edition-aorc-polygon"`. Brief: `Artifact` with `file_path: reports/brief.html`, `url: https://claude.ai/code/artifact/7512d71e-8a5a-404d-a102-2a71e92a1f49`. Load `artifact-design` first as the tool requires.

- [ ] **Step 5: Memory + handoff** — update `~/.claude/projects/-Users-COLEMAN-Documents-GitHub-ozark-stream-tracker/memory/spring-river-study-status.md` (second edition merged, comparison headline, next = Phase 8) and run the `handoff` skill.

---

## Self-review

- Spec coverage: handoff steps 1 (Task 2), 2 (Task 3), 3 (Task 4), 4 (Task 5), 5 (Tasks 7–8; the comparison is one runner rather than three `make analysis` passes so the phase docs are not overwritten three times), 6 (Task 8 Step 1 grep for CHANGED), 7 (Tasks 8–9). Gotchas: ACIS cache-by-sid (Alton is a new sid — no collision), tz-aware peaks (`_major_flood_dates` reused), pre-2002 AORC note (labels + limitations), pre-commit prettier (edit brief in place), explicit staging.
- Placeholders: Task 8 Steps 2/3/5 contain `<…>` slots for numbers that do not exist until `make analysis` runs; each says where the number comes from. No other TBDs.
- Type consistency: `get_basin_pcpn(start, end, source, refresh)` in `basin`; `aorc.get_basin_pcpn(start, end, refresh)`; `prism.get_basin_pcpn(start, end, buffer_km, polygon, refresh)`; `_mean_grid_series(payload, mask)`; frames are always `date`, `pcpn_in`.
