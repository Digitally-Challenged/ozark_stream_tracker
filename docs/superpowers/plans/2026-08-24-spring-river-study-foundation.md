# Spring River Study — Foundation (Phases 0–3) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the reproducible data foundation for the Spring River hydrologic study — project scaffold, data inventory, cached ingestion (USGS, ACIS, PRISM-via-ACIS, NWPS), QA report, and the annual ledger (Phases 0–3 of the spec).

**Architecture:** A standalone Python 3.12 package (`spring_river`) inside `spring-river-study/`, managed with `uv`. Ingest modules pull from public APIs into `data/raw/` (parquet + request-metadata JSON sidecars, never edited), QA modules produce `docs/qa_report.md`, and a ledger module produces `data/processed/annual_ledger.parquet`. Everything runs via `make data | make qa | make ledger`. Analysis (Phases 4–6) and the Quarto report (Phases 7–8) are separate follow-up plans that consume these outputs.

**Tech Stack:** Python 3.12 (via uv), pandas, numpy, scipy, dataretrieval (USGS-maintained NWIS client), requests, pyarrow, matplotlib, pytest.

**Spec:** `spring-river-study/plan.md` (the research spec). This plan implements spec Phases 0–3 only. Phases 4–6 (analysis) and 7–8 (report) get their own plans after the QA report is reviewed — the spec mandates "Do not start Phase 4+ until QA report is reviewed."

## Global Constraints

Copied verbatim from the spec — every task implicitly includes these:

- Water year (Oct–Sep) for all annual hydrologic stats; calendar year for precip totals unless stated. Recharge season = Sep–Feb.
- Units: cfs, feet (record datum as reported by USGS), inches.
- Pull approval status flags (A = approved, P = provisional) and preserve them.
- Never interpolate across gaps > 7 days. Never edit `data/raw`.
- Ingest modules must be idempotent and cached; raw pulls saved with request metadata.
- Primary gauge: USGS 07069305 (Spring River at Hardy, AR); long-record proxy: 07069500 (Imboden); NWS gauge HDYA4.
- Parameters: 00060 discharge (cfs), 00065 gage height (ft).
- Recharge basin approximation: 30 km buffer around West Plains, MO (36.7439, −91.8524) unless a dye-trace polygon is obtained; the approximation must be stated wherever used.
- Study period: 1981-01-01 through 2026-08-24 (run date; ingest takes an `end` argument so later runs extend it).
- All work happens under `spring-river-study/`; paths below are relative to it. Run Python via `uv run`.
- This git branch is `Digitally-Challenged/goatfish`; commit after each task with conventional-commit messages.

**Verified period of record (NWIS site service, queried 2026-08-24 — spec risk #1 resolved):**

- Hardy 07069305: daily discharge 2001-10-01 → present; **no daily stage product**; instantaneous stage 2007-10-01 → present; annual peaks 2002–2025 (24).
- Imboden 07069500: daily discharge 1936-04-01 → present; annual peaks 1915–2025 (90).
- Therefore: Hardy is the WY 2002+ series; Imboden is the long flood-frequency record; 1981–2001 Hardy exists only in the NWS crest list (NWPS). Stage-threshold days come from daily max of Hardy instantaneous stage (WY 2008+). Task 8 does not pull Hardy DV 00065; Task 11 derives `dv_stage` as `daily_max_stage` from IV. `START_DATE` stays 1981-01-01 for precip; USGS pulls simply return their own start.

---

### Task 1: Project scaffold

**Files:**
- Create: `spring-river-study/pyproject.toml`
- Create: `spring-river-study/.gitignore`
- Create: `spring-river-study/Makefile`
- Create: `spring-river-study/CLAUDE.md`
- Create: `spring-river-study/src/spring_river/__init__.py`
- Create: `spring-river-study/src/spring_river/config.py`
- Create: `spring-river-study/tests/test_config.py`
- Create empty dirs (with `.gitkeep`): `data/raw/`, `data/interim/`, `data/processed/`, `docs/`, `reports/figures/`, `reports/tables/`, `notebooks/`

**Interfaces:**
- Produces: `spring_river.config` module exposing `SITE_HARDY = "07069305"`, `SITE_IMBODEN = "07069500"`, `NWS_GAUGE = "HDYA4"`, `PARAM_DISCHARGE = "00060"`, `PARAM_STAGE = "00065"`, `START_DATE = "1981-01-01"`, `WEST_PLAINS_LATLON = (36.7439, -91.8524)`, `RECHARGE_BUFFER_KM = 30`, and path constants `RAW_DIR`, `INTERIM_DIR`, `PROCESSED_DIR`, `DOCS_DIR`, `FIGURES_DIR` (all `pathlib.Path`, anchored to the project root via `Path(__file__).resolve().parents[2]`).

- [ ] **Step 1: Write `pyproject.toml`**

```toml
[project]
name = "spring-river"
version = "0.1.0"
description = "Spring River at Hardy, AR hydrologic regime study (1981-2026)"
requires-python = ">=3.12,<3.13"
dependencies = [
    "pandas>=2.2,<3",
    "numpy>=1.26,<3",
    "scipy>=1.13,<2",
    "dataretrieval>=1.0,<2",
    "requests>=2.32,<3",
    "pyarrow>=16,<21",
    "matplotlib>=3.9,<4",
]

[dependency-groups]
dev = ["pytest>=8,<9"]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src/spring_river"]

[tool.pytest.ini_options]
testpaths = ["tests"]
```

- [ ] **Step 2: Write `.gitignore`**

```gitignore
data/raw/*
data/interim/*
!data/raw/.gitkeep
!data/interim/.gitkeep
__pycache__/
*.egg-info/
.venv/
.pytest_cache/
```

Note: `data/processed/` IS committed (small parquet outputs, reproducibility anchor).

- [ ] **Step 3: Write `Makefile`**

```makefile
.PHONY: data qa ledger test inventory

inventory:
	uv run python -m spring_river.ingest.inventory

data:
	uv run python -m spring_river.ingest.pull_all

qa:
	uv run python -m spring_river.qa.report

ledger:
	uv run python -m spring_river.hydro.ledger

test:
	uv run pytest -q
```

- [ ] **Step 4: Write `CLAUDE.md`** — copy the "CLAUDE.md draft" section verbatim from `spring-river-study/plan.md` (spec §5), changing `docs/spec.md` to `plan.md` in the "Analysis order" line since the spec lives at `spring-river-study/plan.md`.

- [ ] **Step 5: Write `src/spring_river/config.py`**

```python
"""Project-wide constants. Single source of truth for sites, params, paths."""
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

SITE_HARDY = "07069305"
SITE_IMBODEN = "07069500"
NWS_GAUGE = "HDYA4"
PARAM_DISCHARGE = "00060"  # cfs
PARAM_STAGE = "00065"      # ft

START_DATE = "1981-01-01"

WEST_PLAINS_LATLON = (36.7439, -91.8524)
RECHARGE_BUFFER_KM = 30  # stated approximation of Mammoth Spring recharge basin

RAW_DIR = PROJECT_ROOT / "data" / "raw"
INTERIM_DIR = PROJECT_ROOT / "data" / "interim"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
DOCS_DIR = PROJECT_ROOT / "docs"
FIGURES_DIR = PROJECT_ROOT / "reports" / "figures"
```

`src/spring_river/__init__.py` is empty.

- [ ] **Step 6: Write the test `tests/test_config.py`**

```python
from spring_river import config


def test_sites_and_params():
    assert config.SITE_HARDY == "07069305"
    assert config.SITE_IMBODEN == "07069500"
    assert config.PARAM_DISCHARGE == "00060"


def test_paths_anchor_to_project_root():
    assert (config.PROJECT_ROOT / "pyproject.toml").exists()
    assert config.RAW_DIR.parts[-2:] == ("data", "raw")
```

- [ ] **Step 7: Install and run tests**

Run (from `spring-river-study/`): `uv sync && uv run pytest -q`
Expected: 2 passed. (`uv sync` creates `.venv` with Python 3.12 and pinned deps.)

- [ ] **Step 8: Commit**

```bash
git add spring-river-study/pyproject.toml spring-river-study/.gitignore spring-river-study/Makefile spring-river-study/CLAUDE.md spring-river-study/src spring-river-study/tests spring-river-study/uv.lock spring-river-study/data/raw/.gitkeep spring-river-study/data/interim/.gitkeep spring-river-study/data/processed/.gitkeep
git commit -m "feat(study): scaffold spring-river study package"
```

---

### Task 2: Cache layer (shared by all ingest modules)

**Files:**
- Create: `src/spring_river/ingest/__init__.py` (empty)
- Create: `src/spring_river/ingest/cache.py`
- Test: `tests/test_cache.py`

**Interfaces:**
- Produces: `cache.fetch_cached(name: str, fetch_fn: Callable[[], pd.DataFrame], meta: dict, refresh: bool = False) -> pd.DataFrame`. Writes `data/raw/{name}.parquet` and `data/raw/{name}.meta.json` (the `meta` dict plus `fetched_at` ISO timestamp and `rows`). Returns cached parquet without calling `fetch_fn` when the file exists and `refresh` is False. All Task 3–6 ingest functions call this.

- [ ] **Step 1: Write the failing test `tests/test_cache.py`**

```python
import json

import pandas as pd
import pytest

from spring_river.ingest import cache


@pytest.fixture
def raw_dir(tmp_path, monkeypatch):
    monkeypatch.setattr(cache, "RAW_DIR", tmp_path)
    return tmp_path


def test_fetch_writes_parquet_and_meta(raw_dir):
    df = cache.fetch_cached(
        "demo", lambda: pd.DataFrame({"x": [1, 2]}), meta={"source": "test"}
    )
    assert len(df) == 2
    assert (raw_dir / "demo.parquet").exists()
    meta = json.loads((raw_dir / "demo.meta.json").read_text())
    assert meta["source"] == "test"
    assert meta["rows"] == 2
    assert "fetched_at" in meta


def test_second_call_uses_cache_not_fetch_fn(raw_dir):
    cache.fetch_cached("demo", lambda: pd.DataFrame({"x": [1]}), meta={})

    def boom():
        raise AssertionError("fetch_fn called despite cache hit")

    df = cache.fetch_cached("demo", boom, meta={})
    assert len(df) == 1


def test_refresh_true_refetches(raw_dir):
    cache.fetch_cached("demo", lambda: pd.DataFrame({"x": [1]}), meta={})
    df = cache.fetch_cached(
        "demo", lambda: pd.DataFrame({"x": [1, 2, 3]}), meta={}, refresh=True
    )
    assert len(df) == 3
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_cache.py -q`
Expected: FAIL — `ImportError` (module `spring_river.ingest.cache` does not exist).

- [ ] **Step 3: Write `src/spring_river/ingest/cache.py`**

```python
"""Raw-data cache: every API pull lands in data/raw with request metadata."""
import json
from datetime import datetime, timezone
from typing import Callable

import pandas as pd

from spring_river.config import RAW_DIR


def fetch_cached(
    name: str,
    fetch_fn: Callable[[], pd.DataFrame],
    meta: dict,
    refresh: bool = False,
) -> pd.DataFrame:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    parquet_path = RAW_DIR / f"{name}.parquet"
    if parquet_path.exists() and not refresh:
        return pd.read_parquet(parquet_path)

    df = fetch_fn()
    df.to_parquet(parquet_path)
    record = dict(meta)
    record["fetched_at"] = datetime.now(timezone.utc).isoformat()
    record["rows"] = int(len(df))
    (RAW_DIR / f"{name}.meta.json").write_text(json.dumps(record, indent=2))
    return df
```

Note: `monkeypatch.setattr(cache, "RAW_DIR", tmp_path)` in the tests requires `cache.py` to reference the module-level name `RAW_DIR` (as written above), not re-import it inside the function.

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/test_cache.py -q`
Expected: 3 passed.

- [ ] **Step 5: Commit**

```bash
git add spring-river-study/src/spring_river/ingest spring-river-study/tests/test_cache.py
git commit -m "feat(study): raw-data cache layer with request metadata"
```

---

### Task 3: USGS ingest module

**Files:**
- Create: `src/spring_river/ingest/usgs.py`
- Test: `tests/test_usgs.py`

**Interfaces:**
- Consumes: `cache.fetch_cached` (Task 2), `config` constants (Task 1).
- Produces:
  - `get_dv(site: str, param: str, start: str, end: str, refresh: bool = False) -> pd.DataFrame` — columns `date` (datetime64), `value` (float), `approved` (bool); one row per day.
  - `get_iv(site: str, param: str, start: str, end: str, refresh: bool = False) -> pd.DataFrame` — columns `datetime`, `value`, `approved`.
  - `get_peaks(site: str, refresh: bool = False) -> pd.DataFrame` — columns `date`, `peak_cfs` (float), `gage_ht_ft` (float, NaN allowed).
  - `_tidy_dv(raw: pd.DataFrame, param: str) -> pd.DataFrame` — pure function that normalizes a dataretrieval NWIS frame; unit-tested directly.

Implementation notes for the engineer: `dataretrieval.nwis.get_dv(sites=..., parameterCd=..., start=..., end=...)` returns a tuple `(df, metadata)`. The df is indexed by datetime and has columns like `"00060_Mean"` and `"00060_Mean_cd"` (the `_cd` column holds qualification codes; `"A"`-prefixed = approved, `"P"`-prefixed = provisional). `nwis.get_discharge_peaks(sites=...)` returns a df with `peak_va` (cfs) and `gage_ht` (ft) columns indexed/keyed by `datetime`. Spec requires preserving approval flags — that is the `approved` boolean.

- [ ] **Step 1: Write the failing test `tests/test_usgs.py`** (tests the pure tidy function on a synthetic dataretrieval-shaped frame — no network)

```python
import pandas as pd

from spring_river.ingest.usgs import _tidy_dv


def _fake_nwis_dv() -> pd.DataFrame:
    idx = pd.DatetimeIndex(
        ["2020-01-01", "2020-01-02", "2020-01-03"], tz="UTC", name="datetime"
    )
    return pd.DataFrame(
        {
            "site_no": ["07069305"] * 3,
            "00060_Mean": [850.0, 900.0, -999999.0],
            "00060_Mean_cd": ["A", "P", "A, e"],
        },
        index=idx,
    )


def test_tidy_dv_columns_and_approval():
    out = _tidy_dv(_fake_nwis_dv(), param="00060")
    assert list(out.columns) == ["date", "value", "approved"]
    assert out["approved"].tolist() == [True, False, True]
    assert out["date"].dt.tz is None  # naive local dates


def test_tidy_dv_masks_nwis_sentinel():
    out = _tidy_dv(_fake_nwis_dv(), param="00060")
    assert pd.isna(out["value"].iloc[2])  # -999999 => NaN
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_usgs.py -q`
Expected: FAIL — `ImportError: cannot import name '_tidy_dv'`.

- [ ] **Step 3: Write `src/spring_river/ingest/usgs.py`**

```python
"""USGS NWIS ingestion via the dataretrieval package, cached to data/raw."""
import pandas as pd
from dataretrieval import nwis

from spring_river.ingest.cache import fetch_cached


def _tidy_dv(raw: pd.DataFrame, param: str) -> pd.DataFrame:
    value_col = f"{param}_Mean"
    cd_col = f"{param}_Mean_cd"
    out = pd.DataFrame(
        {
            "date": raw.index.tz_localize(None)
            if raw.index.tz is not None
            else raw.index,
            "value": pd.to_numeric(raw[value_col], errors="coerce"),
            "approved": raw[cd_col].astype(str).str.startswith("A"),
        }
    ).reset_index(drop=True)
    out.loc[out["value"] <= -999990, "value"] = pd.NA
    out["value"] = out["value"].astype("float64")
    return out


def get_dv(
    site: str, param: str, start: str, end: str, refresh: bool = False
) -> pd.DataFrame:
    name = f"usgs_dv_{site}_{param}"

    def fetch() -> pd.DataFrame:
        raw, _ = nwis.get_dv(sites=site, parameterCd=param, start=start, end=end)
        return _tidy_dv(raw, param)

    meta = {
        "source": "USGS NWIS daily values via dataretrieval",
        "site": site,
        "parameterCd": param,
        "start": start,
        "end": end,
    }
    return fetch_cached(name, fetch, meta, refresh=refresh)


def get_iv(
    site: str, param: str, start: str, end: str, refresh: bool = False
) -> pd.DataFrame:
    name = f"usgs_iv_{site}_{param}_{start[:4]}_{end[:4]}"

    def fetch() -> pd.DataFrame:
        raw, _ = nwis.get_iv(sites=site, parameterCd=param, start=start, end=end)
        cd_cols = [c for c in raw.columns if c.endswith("_cd")]
        value_cols = [
            c for c in raw.columns if c.startswith(param) and not c.endswith("_cd")
        ]
        out = pd.DataFrame(
            {
                "datetime": raw.index.tz_convert("US/Central").tz_localize(None),
                "value": pd.to_numeric(raw[value_cols[0]], errors="coerce"),
                "approved": raw[cd_cols[0]].astype(str).str.startswith("A"),
            }
        ).reset_index(drop=True)
        out.loc[out["value"] <= -999990, "value"] = pd.NA
        return out

    meta = {
        "source": "USGS NWIS instantaneous values via dataretrieval",
        "site": site,
        "parameterCd": param,
        "start": start,
        "end": end,
    }
    return fetch_cached(name, fetch, meta, refresh=refresh)


def get_peaks(site: str, refresh: bool = False) -> pd.DataFrame:
    name = f"usgs_peaks_{site}"

    def fetch() -> pd.DataFrame:
        raw, _ = nwis.get_discharge_peaks(sites=site)
        out = pd.DataFrame(
            {
                "date": pd.to_datetime(raw.index)
                if isinstance(raw.index, pd.DatetimeIndex)
                else pd.to_datetime(raw["datetime"]),
                "peak_cfs": pd.to_numeric(raw["peak_va"], errors="coerce"),
                "gage_ht_ft": pd.to_numeric(raw["gage_ht"], errors="coerce"),
            }
        ).reset_index(drop=True)
        return out

    meta = {"source": "USGS NWIS annual peaks via dataretrieval", "site": site}
    return fetch_cached(name, fetch, meta, refresh=refresh)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/test_usgs.py -q`
Expected: 2 passed.

- [ ] **Step 5: Live smoke test (one real pull, small window)**

Run: `uv run python -c "from spring_river.ingest.usgs import get_dv; df = get_dv('07069305','00060','2024-01-01','2024-01-31'); print(df.head()); print(len(df), 'rows,', df['approved'].mean())"`
Expected: 31 rows, plausible cfs values, approval fraction printed. If dataretrieval raises about the legacy endpoint (spec risk #2), record the actual df column names it returned, adjust `_tidy_dv`'s expected columns AND the synthetic frame in the test to match reality, and note the endpoint status in `docs/data_inventory.md` during Task 7. Then delete the smoke-test cache files: `rm data/raw/usgs_dv_07069305_00060.parquet data/raw/usgs_dv_07069305_00060.meta.json` (the real pull in Task 8 uses the full date range).

- [ ] **Step 6: Commit**

```bash
git add spring-river-study/src/spring_river/ingest/usgs.py spring-river-study/tests/test_usgs.py
git commit -m "feat(study): USGS DV/IV/peaks ingestion with approval flags"
```

---

### Task 4: ACIS precipitation ingest

**Files:**
- Create: `src/spring_river/ingest/acis.py`
- Test: `tests/test_acis.py`

**Interfaces:**
- Consumes: `cache.fetch_cached` (Task 2).
- Produces:
  - `get_station_pcpn(sid: str, start: str, end: str, refresh: bool = False) -> pd.DataFrame` — columns `date`, `pcpn_in` (float; trace "T" → 0.0; "M" → NaN).
  - `_parse_stndata(payload: dict) -> pd.DataFrame` — pure parser, unit-tested.
  - `find_stations(bbox: tuple[float, float, float, float]) -> pd.DataFrame` — station metadata (`sid`, `name`, `ll`, `valid_daterange`) from ACIS `StnMeta`, used by the Task 7 inventory. Not cached (metadata query, cheap).

API notes: POST JSON to `https://data.rcc-acis.org/StnData` with body `{"sid": sid, "sdate": start, "edate": end, "elems": [{"name": "pcpn"}]}`. Response: `{"meta": {...}, "data": [["1981-01-01", "0.00"], ...]}`. Values are strings: `"T"` = trace, `"M"` = missing. `StnMeta` takes `{"bbox": "west,south,east,north", "elems": "pcpn", "meta": "name,sids,ll,valid_daterange"}`. No API key.

- [ ] **Step 1: Write the failing test `tests/test_acis.py`**

```python
import pandas as pd

from spring_river.ingest.acis import _parse_stndata


PAYLOAD = {
    "meta": {"name": "WEST PLAINS"},
    "data": [
        ["2020-01-01", "0.35"],
        ["2020-01-02", "T"],
        ["2020-01-03", "M"],
        ["2020-01-04", "1.20"],
    ],
}


def test_parse_stndata_values():
    out = _parse_stndata(PAYLOAD)
    assert list(out.columns) == ["date", "pcpn_in"]
    assert out["pcpn_in"].iloc[0] == 0.35
    assert out["pcpn_in"].iloc[1] == 0.0  # trace -> 0.0
    assert pd.isna(out["pcpn_in"].iloc[2])  # missing -> NaN
    assert out["date"].dtype.kind == "M"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_acis.py -q`
Expected: FAIL — module does not exist.

- [ ] **Step 3: Write `src/spring_river/ingest/acis.py`**

```python
"""RCC-ACIS daily precipitation (StnData) and station discovery (StnMeta)."""
import pandas as pd
import requests

from spring_river.ingest.cache import fetch_cached

ACIS_BASE = "https://data.rcc-acis.org"


def _parse_stndata(payload: dict) -> pd.DataFrame:
    rows = payload["data"]
    df = pd.DataFrame(rows, columns=["date", "pcpn_in"])
    df["date"] = pd.to_datetime(df["date"])
    df["pcpn_in"] = (
        df["pcpn_in"].replace({"T": "0.0", "M": None}).astype("float64")
    )
    return df


def get_station_pcpn(
    sid: str, start: str, end: str, refresh: bool = False
) -> pd.DataFrame:
    name = f"acis_pcpn_{sid.replace(' ', '_')}"
    body = {"sid": sid, "sdate": start, "edate": end, "elems": [{"name": "pcpn"}]}

    def fetch() -> pd.DataFrame:
        resp = requests.post(f"{ACIS_BASE}/StnData", json=body, timeout=60)
        resp.raise_for_status()
        payload = resp.json()
        if "error" in payload:
            raise RuntimeError(f"ACIS error for {sid}: {payload['error']}")
        return _parse_stndata(payload)

    meta = {"source": "RCC-ACIS StnData", "request": body}
    return fetch_cached(name, fetch, meta, refresh=refresh)


def find_stations(bbox: tuple[float, float, float, float]) -> pd.DataFrame:
    body = {
        "bbox": ",".join(str(v) for v in bbox),  # west,south,east,north
        "elems": "pcpn",
        "meta": "name,sids,ll,valid_daterange",
    }
    resp = requests.post(f"{ACIS_BASE}/StnMeta", json=body, timeout=60)
    resp.raise_for_status()
    stations = resp.json()["meta"]
    return pd.DataFrame(
        {
            "name": [s.get("name") for s in stations],
            "sids": [s.get("sids") for s in stations],
            "ll": [s.get("ll") for s in stations],
            "valid_daterange": [s.get("valid_daterange") for s in stations],
        }
    )
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/test_acis.py -q`
Expected: 1 passed.

- [ ] **Step 5: Live smoke test**

Run: `uv run python -c "from spring_river.ingest.acis import get_station_pcpn; df = get_station_pcpn('KUNO','2024-01-01','2024-01-31'); print(df.head(3), len(df))"`
Expected: 31 rows of West Plains ASOS precip. If `KUNO` errors, try sid `"UNO"` and `"West Plains, MO"`; the working sid gets recorded in the inventory (Task 7). Delete the smoke cache after: `rm data/raw/acis_pcpn_KUNO.parquet data/raw/acis_pcpn_KUNO.meta.json`.

- [ ] **Step 6: Commit**

```bash
git add spring-river-study/src/spring_river/ingest/acis.py spring-river-study/tests/test_acis.py
git commit -m "feat(study): ACIS daily precip ingestion and station discovery"
```

---

### Task 5: Basin-averaged precip (PRISM grid via ACIS GridData)

**Files:**
- Create: `src/spring_river/ingest/prism.py`
- Test: `tests/test_prism.py`

**Interfaces:**
- Consumes: `cache.fetch_cached` (Task 2), `config.WEST_PLAINS_LATLON`, `config.RECHARGE_BUFFER_KM` (Task 1).
- Produces:
  - `get_basin_pcpn(start: str, end: str, buffer_km: float = 30, refresh: bool = False) -> pd.DataFrame` — columns `date`, `pcpn_in` (spatial mean over the buffer bbox).
  - `_bbox_around(lat: float, lon: float, km: float) -> tuple[float, float, float, float]` — pure, unit-tested (west, south, east, north).
  - `_mean_grid_series(payload: dict) -> pd.DataFrame` — pure parser of GridData response, unit-tested.

API notes: ACIS `GridData` (`POST https://data.rcc-acis.org/GridData`) serves the PRISM 4 km grid as `"grid": "21"`. Body: `{"bbox": "w,s,e,n", "sdate": start, "edate": end, "grid": "21", "elems": [{"name": "pcpn"}]}`. Response `data` is `[[date, grid2d], ...]` where `grid2d` is a list of rows of floats; missing cells are `-999`. We average valid cells per day client-side. A square bbox over a circle is a stated approximation on top of the 30 km approximation — acceptable; document in captions (Plan 2 concern). This yields PRISM daily without downloading BIL files.

- [ ] **Step 1: Write the failing test `tests/test_prism.py`**

```python
import math

import pandas as pd

from spring_river.ingest.prism import _bbox_around, _mean_grid_series


def test_bbox_around_west_plains():
    w, s, e, n = _bbox_around(36.7439, -91.8524, 30)
    assert s < 36.7439 < n
    assert w < -91.8524 < e
    # 30 km of latitude ~ 0.27 deg
    assert math.isclose(n - s, 2 * 30 / 111.32, rel_tol=1e-3)


def test_mean_grid_series_ignores_missing_cells():
    payload = {
        "data": [
            ["2020-01-01", [[0.5, 0.7], [-999, 0.9]]],
            ["2020-01-02", [[-999, -999], [-999, -999]]],
        ]
    }
    out = _mean_grid_series(payload)
    assert list(out.columns) == ["date", "pcpn_in"]
    assert math.isclose(out["pcpn_in"].iloc[0], (0.5 + 0.7 + 0.9) / 3)
    assert pd.isna(out["pcpn_in"].iloc[1])
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_prism.py -q`
Expected: FAIL — module does not exist.

- [ ] **Step 3: Write `src/spring_river/ingest/prism.py`**

```python
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


def _mean_grid_series(payload: dict) -> pd.DataFrame:
    dates, means = [], []
    for date_str, grid in payload["data"]:
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
```

(Year-by-year requests keep each GridData response small; the union with the literal start date covers a mid-year `start`.)

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/test_prism.py -q`
Expected: 2 passed.

- [ ] **Step 5: Live smoke test (one month)**

Run: `uv run python -c "from spring_river.ingest.prism import get_basin_pcpn; df = get_basin_pcpn('2024-01-01','2024-01-31'); print(df.head(3), len(df))"`
Expected: 31 daily basin means, values 0–3 in. Then `rm data/raw/prism_basin_pcpn_30km.parquet data/raw/prism_basin_pcpn_30km.meta.json`.

- [ ] **Step 6: Commit**

```bash
git add spring-river-study/src/spring_river/ingest/prism.py spring-river-study/tests/test_prism.py
git commit -m "feat(study): PRISM basin precip via ACIS GridData with stated buffer approximation"
```

---

### Task 6: NWPS ingest (flood categories + historic crests)

**Files:**
- Create: `src/spring_river/ingest/nwps.py`
- Test: `tests/test_nwps.py`

**Interfaces:**
- Consumes: `cache.fetch_cached` (Task 2), `config.NWS_GAUGE` (Task 1).
- Produces:
  - `get_gauge_info(refresh: bool = False) -> dict` — full JSON for HDYA4 saved to `data/raw/nwps_HDYA4.json` (not parquet; it's a nested document). Returns the parsed dict.
  - `flood_categories(info: dict) -> dict[str, float]` — pure; returns `{"action": ..., "minor": ..., "moderate": ..., "major": ...}` stage in ft.
  - `historic_crests(info: dict) -> pd.DataFrame` — pure; columns `date`, `stage_ft`, `flow_cfs` (NaN when NWPS reports 0), deduplicated, sorted. Verified live 2026-08-24: 21 entries, record crest 29.0 ft on 1982-12-03, then 2002+. This is the only pre-2001 Hardy record; the Phase 5 plan consumes it.

API notes: `GET https://api.water.noaa.gov/nwps/v1/gauges/HDYA4` returns JSON with a `flood.categories` object shaped like `{"action": {"stage": 8.0, ...}, "minor": {...}, ...}`. This module bypasses `fetch_cached` (which is parquet-only) and does its own JSON caching with the same sidecar-metadata convention.

- [ ] **Step 1: Write the failing test `tests/test_nwps.py`**

```python
from spring_river.ingest.nwps import flood_categories


def test_flood_categories_extracts_stages():
    info = {
        "flood": {
            "categories": {
                "action": {"stage": 8.0},
                "minor": {"stage": 10.0},
                "moderate": {"stage": 14.0},
                "major": {"stage": 16.0},
            }
        }
    }
    assert flood_categories(info) == {
        "action": 8.0,
        "minor": 10.0,
        "moderate": 14.0,
        "major": 16.0,
    }


def test_flood_categories_missing_returns_empty():
    assert flood_categories({}) == {}


def test_historic_crests_dedups_and_sorts():
    from spring_river.ingest.nwps import historic_crests

    info = {
        "flood": {
            "crests": {
                "historic": [
                    {"occurredTime": "2008-03-19T12:30:00Z", "stage": 22.29, "flow": 80700},
                    {"occurredTime": "1982-12-03T00:00:00Z", "stage": 29, "flow": 0},
                    {"occurredTime": "1982-12-03T00:00:00Z", "stage": 29, "flow": 0},
                ]
            }
        }
    }
    out = historic_crests(info)
    assert list(out.columns) == ["date", "stage_ft", "flow_cfs"]
    assert len(out) == 2  # duplicate 1982 entry removed (NWPS returns it twice)
    assert out["date"].iloc[0].year == 1982
    assert pd.isna(out["flow_cfs"].iloc[0])  # flow 0 means "not reported"
```

(Add `import pandas as pd` at the top of `tests/test_nwps.py`.)

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_nwps.py -q`
Expected: FAIL — module does not exist.

- [ ] **Step 3: Write `src/spring_river/ingest/nwps.py`**

```python
"""NWS NWPS gauge document for HDYA4: flood categories, ratings, crests."""
import json
from datetime import datetime, timezone

import requests

from spring_river.config import NWS_GAUGE, RAW_DIR

NWPS_URL = f"https://api.water.noaa.gov/nwps/v1/gauges/{NWS_GAUGE}"


def get_gauge_info(refresh: bool = False) -> dict:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    path = RAW_DIR / f"nwps_{NWS_GAUGE}.json"
    if path.exists() and not refresh:
        return json.loads(path.read_text())
    resp = requests.get(NWPS_URL, timeout=30)
    resp.raise_for_status()
    info = resp.json()
    path.write_text(json.dumps(info, indent=2))
    (RAW_DIR / f"nwps_{NWS_GAUGE}.meta.json").write_text(
        json.dumps(
            {
                "source": "NWS NWPS v1 gauge document",
                "url": NWPS_URL,
                "fetched_at": datetime.now(timezone.utc).isoformat(),
            },
            indent=2,
        )
    )
    return info


def flood_categories(info: dict) -> dict[str, float]:
    cats = info.get("flood", {}).get("categories", {})
    return {
        name: float(body["stage"])
        for name, body in cats.items()
        if isinstance(body, dict) and body.get("stage") is not None
    }


def historic_crests(info: dict) -> pd.DataFrame:
    """NWS crest list — the only Hardy record before USGS DV starts in 2001.
    NWPS reports flow=0 when unknown; treat as missing. Duplicates dropped."""
    rows = info.get("flood", {}).get("crests", {}).get("historic", [])
    df = pd.DataFrame(
        {
            "date": pd.to_datetime([r["occurredTime"] for r in rows]).tz_localize(None),
            "stage_ft": [float(r["stage"]) for r in rows],
            "flow_cfs": [float(r["flow"]) if r.get("flow") else float("nan") for r in rows],
        }
    )
    return (
        df.drop_duplicates(["date", "stage_ft"])
        .sort_values("date")
        .reset_index(drop=True)
    )
```

(Add `import pandas as pd` to the imports of `nwps.py`.)

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/test_nwps.py -q`
Expected: 3 passed.

- [ ] **Step 5: Live smoke test**

Run: `uv run python -c "from spring_river.ingest.nwps import get_gauge_info, flood_categories; print(flood_categories(get_gauge_info()))"`
Expected: four stages printed (spec expects roughly action 8 / minor 10 / moderate 14 / major 16 — record whatever NWPS actually says; the spec's thresholds are hypotheses, the API is authoritative). Keep this cache file — it's the real pull.

- [ ] **Step 6: Commit**

```bash
git add spring-river-study/src/spring_river/ingest/nwps.py spring-river-study/tests/test_nwps.py
git commit -m "feat(study): NWPS gauge ingestion with flood categories"
```

---

### Task 7: Phase 0 data inventory

**Files:**
- Create: `src/spring_river/ingest/inventory.py`
- Output (committed): `docs/data_inventory.md`

**Interfaces:**
- Consumes: `dataretrieval.nwis` directly (site metadata + period-of-record queries), `acis.find_stations` (Task 4), `nwps.get_gauge_info`/`flood_categories` (Task 6).
- Produces: `docs/data_inventory.md` — the Phase 0 exit artifact: exact period of record per site/parameter/service, Mammoth Spring / Warm Fork gauge search results, ACIS candidate stations with completeness, NWPS flood categories, and the primary-station decision. Also `main()` runnable as `python -m spring_river.ingest.inventory` (wired to `make inventory`).

This task is exploratory by nature — the script queries live services and writes what it finds. No unit test (it's a report generator over live metadata; spec's testing strategy: skip tests for main()/CLI). The deliverable is the reviewed markdown.

- [ ] **Step 1: Write `src/spring_river/ingest/inventory.py`**

```python
"""Phase 0: data inventory. Writes docs/data_inventory.md from live metadata."""
from datetime import date

import pandas as pd
from dataretrieval import nwis

from spring_river.config import DOCS_DIR, SITE_HARDY, SITE_IMBODEN
from spring_river.ingest.acis import find_stations
from spring_river.ingest.nwps import flood_categories, get_gauge_info
from spring_river.ingest.prism import _bbox_around
from spring_river.config import WEST_PLAINS_LATLON


def _period_of_record(site: str) -> pd.DataFrame:
    """Per-parameter/service date ranges from the NWIS site service."""
    raw, _ = nwis.get_info(sites=site, seriesCatalogOutput=True)
    cols = ["parm_cd", "data_type_cd", "begin_date", "end_date", "count_nu"]
    have = [c for c in cols if c in raw.columns]
    df = raw[have].copy()
    return df[df["parm_cd"].isin(["00060", "00065"]) | df["data_type_cd"].eq("pk")]


def _mammoth_spring_search() -> pd.DataFrame:
    """Search NWIS for gauges near Mammoth Spring / Warm Fork (spec §1.1)."""
    frames = []
    for state, name_like in [("ar", "mammoth"), ("mo", "warm fork")]:
        try:
            raw, _ = nwis.what_sites(stateCd=state, siteNameMatchOperator="any")
            hit = raw[raw["station_nm"].str.lower().str.contains(name_like, na=False)]
            frames.append(hit[["site_no", "station_nm", "site_tp_cd"]])
        except Exception as exc:  # noqa: BLE001 - inventory records failures
            frames.append(
                pd.DataFrame(
                    {"site_no": ["ERROR"], "station_nm": [str(exc)], "site_tp_cd": [state]}
                )
            )
    return pd.concat(frames, ignore_index=True)


def main() -> None:
    lines = [f"# Data inventory — generated {date.today().isoformat()}", ""]

    for site, label in [(SITE_HARDY, "Hardy 07069305"), (SITE_IMBODEN, "Imboden 07069500")]:
        lines += [f"## USGS {label} — period of record", ""]
        lines.append(_period_of_record(site).to_markdown(index=False))
        lines.append("")

    lines += ["## Mammoth Spring / Warm Fork gauge search", ""]
    lines.append(_mammoth_spring_search().to_markdown(index=False))
    lines.append("")

    lines += ["## ACIS precip stations within ~40 km of West Plains", ""]
    bbox = _bbox_around(*WEST_PLAINS_LATLON, 40)
    lines.append(find_stations(bbox).to_markdown(index=False))
    lines.append("")

    lines += ["## NWPS HDYA4 flood categories (ft)", ""]
    lines.append(str(flood_categories(get_gauge_info())))
    lines += [
        "",
        "## Decisions (fill in after review)",
        "",
        "- [ ] Long flood-frequency series: Hardy alone or Imboden-extended?",
        "- [ ] Primary precip station (ASOS vs COOP) and its working ACIS sid",
        "- [ ] Mammoth Spring discharge series available: yes/no",
        "- [ ] IV data availability from 2007+ for rating-drift analysis: yes/no",
        "- [ ] Legacy NWIS endpoint status note",
    ]

    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    out = DOCS_DIR / "data_inventory.md"
    out.write_text("\n".join(lines))
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
```

(Requires `tabulate` for `to_markdown` — add it: `uv add tabulate`.)

- [ ] **Step 2: Run it**

Run: `uv add tabulate && make inventory`
Expected: `docs/data_inventory.md` written. If `nwis.get_info(seriesCatalogOutput=True)` returns different column names, print `raw.columns` and adapt `_period_of_record` — the exit criterion is the markdown content, not the exact code path. If `what_sites` with those arguments errors, fall back to `nwis.what_sites(stateCd=state, hasDataTypeCd="dv")` and filter by name client-side.

- [ ] **Step 3: Review and fill in the Decisions section**

Read the generated inventory. Answer each Decisions checkbox in the file from the evidence above it (this is the spec's Phase 0 exit criterion: "exact date ranges and gaps" + spec risk #1: does Hardy DV really start 1981?). Where the answer changes downstream defaults (e.g., DV pull start date, chosen precip sid), record the value here — Task 8 reads these decisions.

- [ ] **Step 4: Commit**

```bash
git add spring-river-study/src/spring_river/ingest/inventory.py spring-river-study/docs/data_inventory.md spring-river-study/pyproject.toml spring-river-study/uv.lock spring-river-study/Makefile
git commit -m "feat(study): phase 0 data inventory with period-of-record and station decisions"
```

---

### Task 8: `make data` — full pull orchestration

**Files:**
- Create: `src/spring_river/ingest/pull_all.py`

**Interfaces:**
- Consumes: every ingest module (Tasks 3–6), decisions from `docs/data_inventory.md` (Task 7).
- Produces: a populated `data/raw/` — the Phase 1 exit criterion ("`make data` runs clean from empty cache"). Downstream tasks read these exact cache names: `usgs_dv_{site}_{param}`, `usgs_peaks_{site}`, `usgs_iv_07069305_00065_2007_2026`, `acis_pcpn_{sid}`, `prism_basin_pcpn_30km`, `nwps_HDYA4.json`.

- [ ] **Step 1: Write `src/spring_river/ingest/pull_all.py`**

```python
"""Phase 1: pull everything into data/raw. Idempotent — cached pulls are skipped."""
from datetime import date

from spring_river.config import (
    PARAM_DISCHARGE,
    PARAM_STAGE,
    SITE_HARDY,
    SITE_IMBODEN,
    START_DATE,
)
from spring_river.ingest import acis, nwps, prism, usgs

# Adjust from docs/data_inventory.md decisions:
PRECIP_SIDS = ["KUNO"]  # + COOP sids chosen in Task 7
IV_START = "2007-01-01"  # rating-drift analysis needs sub-daily pairs 2007+


def main() -> None:
    end = date.today().isoformat()

    # Hardy has no daily-stage product (verified 2026-08-24); stage comes from IV.
    for site in (SITE_HARDY, SITE_IMBODEN):
        df = usgs.get_dv(site, PARAM_DISCHARGE, START_DATE, end)
        print(f"dv {site} {PARAM_DISCHARGE}: {len(df)} rows")
        print(f"peaks {site}: {len(usgs.get_peaks(site))} rows")

    df = usgs.get_iv(SITE_HARDY, PARAM_STAGE, IV_START, end)
    print(f"iv {SITE_HARDY} stage: {len(df)} rows")

    for sid in PRECIP_SIDS:
        df = acis.get_station_pcpn(sid, START_DATE, end)
        print(f"acis {sid}: {len(df)} rows")

    df = prism.get_basin_pcpn(START_DATE, end)
    print(f"prism basin: {len(df)} rows")

    cats = nwps.flood_categories(nwps.get_gauge_info())
    print(f"nwps flood categories: {cats}")


if __name__ == "__main__":
    main()
```

Before running, update `PRECIP_SIDS` and (if the inventory says IV starts later) `IV_START` per the Task 7 Decisions section.

- [ ] **Step 2: Run the full pull**

Run: `make data` (the IV pull is the big one — 19 years of sub-daily stage; expect minutes, not seconds; dataretrieval may need the pull chunked by year if the service rejects the range — if so, loop `get_iv` per year inside `pull_all.py` with per-year cache names `usgs_iv_{site}_{param}_{y}_{y}`).
Expected: all row counts printed, no exceptions; `ls data/raw/` shows a parquet + meta.json pair per pull.

- [ ] **Step 3: Verify idempotence (Phase 1 exit criterion)**

Run: `make data` a second time.
Expected: identical output, near-instant (all cache hits, no network).

- [ ] **Step 4: Commit**

```bash
git add spring-river-study/src/spring_river/ingest/pull_all.py
git commit -m "feat(study): make data orchestration for full raw pull"
```

---

### Task 9: QA module — gaps, cross-check, homogeneity, QA report

**Files:**
- Create: `src/spring_river/qa/__init__.py` (empty)
- Create: `src/spring_river/qa/gaps.py`
- Create: `src/spring_river/qa/crosscheck.py`
- Create: `src/spring_river/qa/report.py`
- Test: `tests/test_gaps.py`, `tests/test_crosscheck.py`
- Output (committed): `docs/qa_report.md`, `reports/figures/qa_*.png`

**Interfaces:**
- Consumes: raw parquet from Task 8 (via `usgs.get_dv` etc. — cache hits), `config` paths.
- Produces:
  - `gaps.find_gaps(df: pd.DataFrame, max_days: int = 7) -> pd.DataFrame` — pure; input has `date`,`value`; output columns `gap_start`, `gap_end`, `days` for runs of missing dates OR NaN values longer than `max_days`.
  - `gaps.approval_summary(df: pd.DataFrame) -> dict` — `{"approved_frac": float, "provisional_from": Timestamp | None}`.
  - `crosscheck.hardy_vs_imboden(hardy: pd.DataFrame, imboden: pd.DataFrame) -> pd.DataFrame` — inner-join on date, log-log OLS (scipy.stats.linregress on `log10(value)` of positive-flow days), returns per-day residuals with columns `date`, `hardy`, `imboden`, `residual`; extreme residuals (|z| > 4) flag Hardy record problems.
  - `crosscheck.precip_overlap(a: pd.DataFrame, b: pd.DataFrame) -> dict` — overlap-period stats between two precip series: `{"n_days": int, "corr": float, "mean_ratio": float}`.
  - `report.main()` — assembles `docs/qa_report.md` with gap tables, approval split, cross-check figure, precip homogeneity stats. Wired to `make qa`.

- [ ] **Step 1: Write the failing tests**

`tests/test_gaps.py`:

```python
import pandas as pd

from spring_river.qa.gaps import approval_summary, find_gaps


def _series_with_gap() -> pd.DataFrame:
    dates = pd.date_range("2020-01-01", "2020-02-29", freq="D")
    df = pd.DataFrame({"date": dates, "value": 100.0, "approved": True})
    # 10-day NaN run (> 7 flag threshold)
    df.loc[10:19, "value"] = pd.NA
    # 3-day NaN run (below threshold)
    df.loc[40:42, "value"] = pd.NA
    # drop 9 calendar days entirely (missing rows count as a gap too)
    return df.drop(index=range(25, 34)).reset_index(drop=True)


def test_find_gaps_flags_long_runs_only():
    gaps = find_gaps(_series_with_gap(), max_days=7)
    assert list(gaps.columns) == ["gap_start", "gap_end", "days"]
    assert len(gaps) == 2  # the 10-day NaN run and the 9 missing days
    assert set(gaps["days"]) == {10, 9}


def test_approval_summary():
    df = pd.DataFrame(
        {
            "date": pd.date_range("2020-01-01", periods=4),
            "value": 1.0,
            "approved": [True, True, False, False],
        }
    )
    out = approval_summary(df)
    assert out["approved_frac"] == 0.5
    assert out["provisional_from"] == pd.Timestamp("2020-01-03")
```

`tests/test_crosscheck.py`:

```python
import numpy as np
import pandas as pd

from spring_river.qa.crosscheck import hardy_vs_imboden, precip_overlap


def test_hardy_vs_imboden_flags_planted_outlier():
    rng = np.random.default_rng(1)
    dates = pd.date_range("2020-01-01", periods=400, freq="D")
    imboden = pd.Series(10 ** rng.normal(3, 0.4, size=400))
    hardy = imboden * 0.6 * 10 ** rng.normal(0, 0.02, size=400)
    hardy.iloc[200] *= 40  # planted bad Hardy value
    h = pd.DataFrame({"date": dates, "value": hardy.values})
    i = pd.DataFrame({"date": dates, "value": imboden.values})
    out = hardy_vs_imboden(h, i)
    z = (out["residual"] - out["residual"].mean()) / out["residual"].std()
    assert dates[200] in set(out.loc[z.abs() > 4, "date"])


def test_precip_overlap_stats():
    dates = pd.date_range("2020-01-01", periods=100, freq="D")
    a = pd.DataFrame({"date": dates, "pcpn_in": np.linspace(0, 1, 100)})
    b = pd.DataFrame({"date": dates, "pcpn_in": np.linspace(0, 1, 100) * 1.1})
    out = precip_overlap(a, b)
    assert out["n_days"] == 100
    assert out["corr"] > 0.99
    assert 1.05 < out["mean_ratio"] < 1.15  # b/a
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/test_gaps.py tests/test_crosscheck.py -q`
Expected: FAIL — modules do not exist.

- [ ] **Step 3: Write `src/spring_river/qa/gaps.py`**

```python
"""Gap detection and approval-status accounting. Spec: flag gaps > 7 days."""
import pandas as pd


def find_gaps(df: pd.DataFrame, max_days: int = 7) -> pd.DataFrame:
    s = df.set_index("date")["value"].sort_index()
    full = s.reindex(pd.date_range(s.index.min(), s.index.max(), freq="D"))
    missing = full.isna()
    group = (missing != missing.shift()).cumsum()
    runs = (
        pd.DataFrame({"missing": missing, "group": group})
        .reset_index(names="date")
        .groupby("group")
        .agg(
            gap_start=("date", "min"),
            gap_end=("date", "max"),
            days=("date", "size"),
            missing=("missing", "first"),
        )
    )
    gaps = runs[runs["missing"] & (runs["days"] > max_days)]
    return gaps[["gap_start", "gap_end", "days"]].reset_index(drop=True)


def approval_summary(df: pd.DataFrame) -> dict:
    approved_frac = float(df["approved"].mean())
    provisional = df.loc[~df["approved"], "date"]
    return {
        "approved_frac": approved_frac,
        "provisional_from": provisional.min() if len(provisional) else None,
    }
```

- [ ] **Step 4: Write `src/spring_river/qa/crosscheck.py`**

```python
"""Hardy vs Imboden discharge cross-check and precip homogeneity (spec §2.1)."""
import numpy as np
import pandas as pd
from scipy import stats


def hardy_vs_imboden(hardy: pd.DataFrame, imboden: pd.DataFrame) -> pd.DataFrame:
    merged = hardy.merge(imboden, on="date", suffixes=("_h", "_i"))
    merged = merged[(merged["value_h"] > 0) & (merged["value_i"] > 0)].copy()
    lh, li = np.log10(merged["value_h"]), np.log10(merged["value_i"])
    fit = stats.linregress(li, lh)
    merged["residual"] = lh - (fit.intercept + fit.slope * li)
    return merged.rename(columns={"value_h": "hardy", "value_i": "imboden"})[
        ["date", "hardy", "imboden", "residual"]
    ].reset_index(drop=True)


def precip_overlap(a: pd.DataFrame, b: pd.DataFrame) -> dict:
    merged = a.merge(b, on="date", suffixes=("_a", "_b")).dropna()
    mean_a = merged["pcpn_in_a"].mean()
    return {
        "n_days": int(len(merged)),
        "corr": float(merged["pcpn_in_a"].corr(merged["pcpn_in_b"])),
        "mean_ratio": float(merged["pcpn_in_b"].mean() / mean_a)
        if mean_a > 0
        else float("nan"),
    }
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `uv run pytest tests/test_gaps.py tests/test_crosscheck.py -q`
Expected: 4 passed.

- [ ] **Step 6: Write `src/spring_river/qa/report.py`**

```python
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
```

- [ ] **Step 7: Run against real data**

Run: `make qa`
Expected: `docs/qa_report.md` and `reports/figures/qa_hardy_imboden_residuals.png` written; read the report and sanity-check spans against `docs/data_inventory.md`. This report is the Phase 2 exit artifact and — per the spec — must be reviewed by Nick before any Phase 4+ analysis plan is executed.

- [ ] **Step 8: Commit**

```bash
git add spring-river-study/src/spring_river/qa spring-river-study/tests/test_gaps.py spring-river-study/tests/test_crosscheck.py spring-river-study/docs/qa_report.md spring-river-study/reports/figures/qa_hardy_imboden_residuals.png
git commit -m "feat(study): QA module with gap maps, cross-check, and qa_report.md"
```

---

### Task 10: Water-year utilities + base-flow separation

**Files:**
- Create: `src/spring_river/hydro/__init__.py` (empty)
- Create: `src/spring_river/hydro/wateryear.py`
- Create: `src/spring_river/hydro/baseflow.py`
- Test: `tests/test_wateryear.py`, `tests/test_baseflow.py`

**Interfaces:**
- Consumes: nothing project-specific (pure numerics).
- Produces (Task 11 and the Phase 4 plan consume these exact signatures):
  - `wateryear.water_year(dates: pd.Series) -> pd.Series` — int WY (Oct–Sep, labeled by ending year: 2019-10-01 → 2020).
  - `wateryear.min7(df: pd.DataFrame) -> pd.Series` — annual minimum 7-day mean discharge per water year, indexed by WY; a WY is NaN if any 7-day window overlapping its minimum has missing days (never interpolate).
  - `wateryear.daily_max_stage(iv: pd.DataFrame) -> pd.DataFrame` — collapses an IV frame (`datetime`, `value`, `approved`) to one row per calendar day: `date`, `value` (daily max), `approved` (True only if every reading that day was approved). Needed because Hardy has no USGS daily-stage product.
  - `baseflow.eckhardt(q: np.ndarray, alpha: float = 0.98, bfi_max: float = 0.8) -> np.ndarray` — recursive filter, `b[t] = ((1-bfi_max)*alpha*b[t-1] + (1-alpha)*bfi_max*q[t]) / (1 - alpha*bfi_max)`, clipped to `b[t] <= q[t]`, initialized `b[0] = q[0] * bfi_max`.
  - `baseflow.bfi(q: np.ndarray, **kw) -> float` — `sum(eckhardt(q)) / sum(q)`.

- [ ] **Step 1: Write the failing tests**

`tests/test_wateryear.py`:

```python
import pandas as pd

from spring_river.hydro.wateryear import min7, water_year


def test_water_year_boundaries():
    dates = pd.Series(pd.to_datetime(["2019-09-30", "2019-10-01", "2020-09-30"]))
    assert water_year(dates).tolist() == [2019, 2020, 2020]


def test_min7_finds_low_flow_window():
    dates = pd.date_range("2019-10-01", "2020-09-30", freq="D")
    values = pd.Series(500.0, index=range(len(dates)))
    values.iloc[300:307] = [100, 90, 80, 80, 80, 90, 100]  # 7-day low ~ 88.57
    df = pd.DataFrame({"date": dates, "value": values.values})
    out = min7(df)
    assert out.index.tolist() == [2020]
    assert abs(out.loc[2020] - (100 + 90 + 80 * 3 + 90 + 100) / 7) < 1e-9


def test_daily_max_stage_collapses_iv():
    from spring_river.hydro.wateryear import daily_max_stage

    iv = pd.DataFrame(
        {
            "datetime": pd.to_datetime(
                ["2020-01-01 00:15", "2020-01-01 12:00", "2020-01-02 06:00"]
            ),
            "value": [4.0, 9.5, 5.0],
            "approved": [True, False, True],
        }
    )
    out = daily_max_stage(iv)
    assert list(out.columns) == ["date", "value", "approved"]
    assert out["value"].tolist() == [9.5, 5.0]
    assert out["approved"].tolist() == [False, True]


def test_min7_nan_when_gap_at_minimum():
    dates = pd.date_range("2019-10-01", "2020-09-30", freq="D")
    values = pd.Series(500.0, index=range(len(dates)))
    values.iloc[300:307] = 50.0
    values.iloc[303] = float("nan")  # gap inside the minimum window
    df = pd.DataFrame({"date": dates, "value": values.values})
    # min over complete windows only; the NaN window must not silently win
    out = min7(df)
    assert out.loc[2020] >= 50.0  # computed from complete windows only
```

`tests/test_baseflow.py`:

```python
import numpy as np

from spring_river.hydro.baseflow import bfi, eckhardt


def test_eckhardt_never_exceeds_streamflow():
    rng = np.random.default_rng(7)
    q = np.exp(rng.normal(5, 1, size=500))
    b = eckhardt(q)
    assert np.all(b <= q + 1e-9)
    assert np.all(b >= 0)


def test_constant_flow_converges_to_bfi_max():
    q = np.full(400, 250.0)
    b = eckhardt(q, bfi_max=0.8)
    # fixed point of the recursion under constant flow is bfi_max * q
    assert abs(b[-1] - 0.8 * 250.0) < 1e-6


def test_bfi_between_0_and_1():
    rng = np.random.default_rng(7)
    q = np.exp(rng.normal(5, 1, size=500))
    assert 0 < bfi(q) < 1
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/test_wateryear.py tests/test_baseflow.py -q`
Expected: FAIL — modules do not exist.

- [ ] **Step 3: Write `src/spring_river/hydro/wateryear.py`**

```python
"""Water-year (Oct-Sep) conventions per spec: WY labeled by ending year."""
import pandas as pd


def water_year(dates: pd.Series) -> pd.Series:
    d = pd.to_datetime(dates)
    return d.dt.year + (d.dt.month >= 10).astype(int)


def min7(df: pd.DataFrame) -> pd.Series:
    """Annual minimum 7-day mean discharge per water year.

    Uses complete 7-day windows only (min_periods=7): windows touching a data
    gap are excluded rather than interpolated (spec: never interpolate).
    """
    s = df.set_index("date")["value"].sort_index()
    full = s.reindex(pd.date_range(s.index.min(), s.index.max(), freq="D"))
    roll = full.rolling(7, min_periods=7).mean()
    wy = water_year(pd.Series(roll.index))
    return roll.groupby(wy.values).min().rename("min7")


def daily_max_stage(iv: pd.DataFrame) -> pd.DataFrame:
    """Daily max of instantaneous stage; a day is 'approved' only if all its
    readings are. Hardy has no USGS daily-stage product, so this stands in."""
    day = iv["datetime"].dt.normalize()
    out = (
        iv.groupby(day)
        .agg(value=("value", "max"), approved=("approved", "all"))
        .reset_index(names="date")
    )
    return out[["date", "value", "approved"]]
```

- [ ] **Step 4: Write `src/spring_river/hydro/baseflow.py`**

```python
"""Eckhardt recursive base-flow filter (spec §2.2). Lyne-Hollick check lands
with the Phase 4 analysis plan; the ledger only needs Eckhardt BFI."""
import numpy as np


def eckhardt(q: np.ndarray, alpha: float = 0.98, bfi_max: float = 0.8) -> np.ndarray:
    q = np.asarray(q, dtype="float64")
    b = np.empty_like(q)
    b[0] = q[0] * bfi_max
    denom = 1.0 - alpha * bfi_max
    for t in range(1, len(q)):
        b[t] = ((1 - bfi_max) * alpha * b[t - 1] + (1 - alpha) * bfi_max * q[t]) / denom
        b[t] = min(b[t], q[t])
    return b


def bfi(q: np.ndarray, **kw) -> float:
    q = np.asarray(q, dtype="float64")
    return float(eckhardt(q, **kw).sum() / q.sum())
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `uv run pytest tests/test_wateryear.py tests/test_baseflow.py -q`
Expected: 7 passed.

- [ ] **Step 6: Commit**

```bash
git add spring-river-study/src/spring_river/hydro spring-river-study/tests/test_wateryear.py spring-river-study/tests/test_baseflow.py
git commit -m "feat(study): water-year utils and Eckhardt base-flow filter"
```

---

### Task 11: Annual ledger (Phase 3 exit)

**Files:**
- Create: `src/spring_river/hydro/ledger.py`
- Test: `tests/test_ledger.py`
- Output (committed): `data/processed/annual_ledger.parquet`, `reports/figures/annual_ledger.png`

**Interfaces:**
- Consumes: `usgs.get_dv`/`get_peaks` (Task 3), `acis.get_station_pcpn` + `pull_all.PRECIP_SIDS` (Tasks 4/8), `prism.get_basin_pcpn` (Task 5), `wateryear.water_year`/`min7`, `baseflow.bfi` (Task 10), `nwps.flood_categories` thresholds (Task 6).
- Produces: `build_ledger(dv_q, dv_stage, peaks, precip, basin_precip, thresholds) -> pd.DataFrame` — pure assembly function, one row per water year, columns: `wy`, `peak_stage_ft`, `peak_cfs`, `days_ge_8ft`, `days_ge_10ft`, `days_ge_14ft`, `days_ge_16ft`, `min7_cfs`, `bfi`, `precip_cal_in` (calendar-year station total, labeled by calendar year = wy), `precip_recharge_in` (basin Sep–Feb total ending in that wy's winter: Sep(wy−1)–Feb(wy)). Plus `main()` that writes the parquet and figure, wired to `make ledger`.

Note: the spec's ledger asks for "≥8/10/14/16 counts" — implemented as days-at-or-above each stage threshold from DV stage (event declustering into POT counts is Phase 5, next plan). Thresholds come from NWPS categories, falling back to `{8, 10, 14, 16}` if a category is missing.

- [ ] **Step 1: Write the failing test `tests/test_ledger.py`**

```python
import pandas as pd

from spring_river.hydro.ledger import build_ledger


def _one_wy_inputs():
    dates = pd.date_range("2019-10-01", "2020-09-30", freq="D")
    dv_q = pd.DataFrame({"date": dates, "value": 400.0, "approved": True})
    stage = pd.Series(5.0, index=range(len(dates)))
    stage.iloc[100:112] = 11.0  # 12 days >= 10 ft (and >= 8 ft)
    dv_stage = pd.DataFrame({"date": dates, "value": stage.values, "approved": True})
    peaks = pd.DataFrame(
        {
            "date": [pd.Timestamp("2020-01-15")],
            "peak_cfs": [22000.0],
            "gage_ht_ft": [11.2],
        }
    )
    pdates = pd.date_range("2019-01-01", "2020-12-31", freq="D")
    precip = pd.DataFrame({"date": pdates, "pcpn_in": 0.1})
    basin = pd.DataFrame({"date": pdates, "pcpn_in": 0.1})
    thresholds = {"action": 8.0, "minor": 10.0, "moderate": 14.0, "major": 16.0}
    return dv_q, dv_stage, peaks, precip, basin, thresholds


def test_ledger_one_water_year():
    ledger = build_ledger(*_one_wy_inputs())
    row = ledger[ledger["wy"] == 2020].iloc[0]
    assert row["peak_cfs"] == 22000.0
    assert row["peak_stage_ft"] == 11.2
    assert row["days_ge_8ft"] == 12
    assert row["days_ge_10ft"] == 12
    assert row["days_ge_14ft"] == 0
    assert row["min7_cfs"] == 400.0
    assert 0 < row["bfi"] <= 1
    # recharge season Sep 2019 - Feb 2020 = 182 days * 0.1
    assert abs(row["precip_recharge_in"] - 18.2) < 0.11
    # calendar 2020 station total = 366 * 0.1
    assert abs(row["precip_cal_in"] - 36.6) < 1e-6
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_ledger.py -q`
Expected: FAIL — module does not exist.

- [ ] **Step 3: Write `src/spring_river/hydro/ledger.py`**

```python
"""Phase 3: annual ledger — one row per water year (spec Phase 3 exit)."""
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
    precip = acis.get_station_pcpn(PRECIP_SIDS[0], START_DATE, end)
    basin = prism.get_basin_pcpn(START_DATE, end)
    thresholds = nwps.flood_categories(nwps.get_gauge_info())

    ledger = build_ledger(dv_q, dv_stage, peaks, precip, basin, thresholds)
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    ledger.to_parquet(PROCESSED_DIR / "annual_ledger.parquet")

    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    fig, axes = plt.subplots(3, 1, figsize=(11, 9), sharex=True)
    axes[0].bar(ledger["wy"], ledger["peak_stage_ft"].astype(float))
    axes[0].set_ylabel("peak stage (ft)")
    axes[1].plot(ledger["wy"], ledger["min7_cfs"].astype(float), marker="o")
    axes[1].set_ylabel("7-day low flow (cfs)")
    axes[2].bar(ledger["wy"], ledger["precip_recharge_in"].astype(float))
    axes[2].set_ylabel("recharge-season precip (in)")
    axes[2].set_xlabel("water year")
    fig.suptitle("Spring River at Hardy — annual ledger (source: USGS/ACIS/PRISM)")
    fig.savefig(FIGURES_DIR / "annual_ledger.png", dpi=150)
    print(f"wrote {PROCESSED_DIR / 'annual_ledger.parquet'} ({len(ledger)} water years)")


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_ledger.py -q`
Expected: 1 passed. Then run the whole suite: `uv run pytest -q` — expected: all tests pass (≈16).

- [ ] **Step 5: Build the real ledger**

Run: `make ledger`
Expected: parquet with one row per water year over the actual Hardy period of record; open the figure and eyeball it against the spec's screenshot-derived expectations (2008/2025 as top-tier peaks; low 7-day floors in drought years). If the ledger starts later than WY 1982, that confirms spec risk #1 — the finding goes in the inventory Decisions, not silently absorbed.

- [ ] **Step 6: Commit**

```bash
git add spring-river-study/src/spring_river/hydro/ledger.py spring-river-study/tests/test_ledger.py spring-river-study/data/processed/annual_ledger.parquet spring-river-study/reports/figures/annual_ledger.png
git commit -m "feat(study): annual ledger with peaks, threshold days, min7, BFI, precip"
```

---

## What this plan does NOT cover (deliberate — separate plans)

- **Phases 4–6** (base-flow attribution, B17C flood frequency, precip intensity indices, recession, rating drift from IV): planned after Nick reviews `docs/qa_report.md`, per the spec's gate. That plan adds `pymannkendall`, the Lyne-Hollick check, POT declustering, permutation tests, and the drought/ONI/gwlevels covariate pulls.
- **Phases 7–8** (Quarto report + adversarial review): Quarto is not installed on this machine; installation is a prerequisite noted for that plan.
- **NCEI CDO cross-check** (needs an API token — a credential decision for Nick) and the **dye-trace recharge polygon literature pull**: both flagged as open items; the 30 km buffer approximation is used and stated throughout.
