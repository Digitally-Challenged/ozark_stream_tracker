# Spring River Phases 4–6 (Base flow, Floods, Precip regime) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Answer research questions Q1–Q8 with reproducible code and three markdown exit artifacts: `docs/phase4_baseflow.md` (residual trend with CI), `docs/phase5_floods.md` (LP3 table with CIs + stationarity verdict), `docs/phase6_precip.md` (index trend table).

**Architecture:** A small `stats` package (Mann-Kendall, Sen slope with CI, Pettitt, Benjamini-Hochberg, permutation) is shared by three phase runners (`analysis/phase4.py`, `phase5.py`, `phase6.py`). Each runner loads cached raw data via the existing ingest modules, computes on gap-segmented series, runs every result twice (all data / approved-only), and writes a markdown report + parquet tables + captioned figures. Pure functions live in `hydro/`, `qa/`, `climate/`; runners only orchestrate and format.

**Tech Stack:** Python 3.12, pandas, numpy, scipy (`stats.pearson3`, `stats.norm`), statsmodels (OLS), matplotlib, pytest, `uv`.

**Spec:** `spring-river-study/plan.md` (§0 questions, §2.2–2.6 methods, §4 phases 4–6). Supporting facts: `spring-river-study/spring_river_research.md`, `docs/data_inventory.md`, `docs/qa_report.md`.

## Global Constraints

- All paths below are relative to `spring-river-study/`. Run commands from that directory with `uv run …`.
- Python `>=3.12,<3.13`; deps pinned in `pyproject.toml` (add `statsmodels>=0.14,<0.15`).
- Water year (Oct–Sep) for all annual hydrologic stats; calendar year for precip totals. Recharge season = Sep–Feb (Sep of `wy-1` through Feb of `wy`).
- **Never interpolate across gaps > 7 days.** Gaps ≤ 7 days may be linearly interpolated. **Never edit `data/raw`.**
- Every figure caption: source, period, approval status. Every trend claim: test name, effect size, 95% CI, n. No bare p-values.
- Every analysis runs twice: all data, then approved-only (`approved == True`). Report any conclusion whose sign or CI-includes-zero status changes.
- Hardy discharge DV starts 2001-10-01 (WY 2002); Hardy IV stage starts 2007-10-01 (`IV_START`). Mammoth Spring vent DV (`SITE_MAMMOTH = "07069190"`) 1981-02-25→present, no gaps. Imboden DV has gaps 1995-05-11→2001-09-30 and 2015-10-27→2016-12-14.
- Ledger BFI is descriptive only; any BFI trend claim must use gap-segmented filtering (Task 3).
- Style for reports: scientific, terse. Thesis → evidence → limitation.
- Tests: `uv run pytest -q` must stay green after every task. Commit after every task with a `feat(study):`/`fix(study):`/`test(study):` conventional message.

## File map

| Path | Responsibility |
|---|---|
| `src/spring_river/stats/__init__.py` | package marker |
| `src/spring_river/stats/trends.py` | `mann_kendall`, `sen_slope`, `pettitt`, `TrendResult` |
| `src/spring_river/stats/multiple.py` | `benjamini_hochberg` |
| `src/spring_river/stats/permutation.py` | `conditional_rate_test` (Q7) |
| `src/spring_river/hydro/segments.py` | `segment_gapfree` — split a daily series at gaps > 7 d, interpolate ≤ 7 d |
| `src/spring_river/hydro/baseflow.py` (modify) | add `lyne_hollick`, `eckhardt_segmented`, `bfi_by_wy` |
| `src/spring_river/ingest/oni.py` | CPC ONI ingest, recharge-season mean per WY |
| `src/spring_river/hydro/lowflow.py` | Q1 attribution table + OLS + residual trend |
| `src/spring_river/qa/rating.py` | Q5 stage-at-fixed-discharge per WY from IV pairs |
| `src/spring_river/hydro/postflood.py` | Q4 post-flood base flow vs precip-matched years |
| `src/spring_river/hydro/pot.py` | POT declustering, annual counts, dispersion test |
| `src/spring_river/hydro/freq_lp3.py` | LP3 fit, weighted skew, Grubbs-Beck, bootstrap CI, stage↔flow |
| `src/spring_river/hydro/interarrival.py` | Q6 inter-arrival vs exponential; antecedent conditions |
| `src/spring_river/climate/__init__.py` | package marker |
| `src/spring_river/climate/intensity.py` | Q3 annual indices with coverage gate |
| `src/spring_river/climate/coupling.py` | monthly precip → spring-flow lag correlation |
| `src/spring_river/analysis/__init__.py` | package marker |
| `src/spring_river/analysis/common.py` | `approval_variants`, `caption`, `write_report`, `sensitivity_lines` |
| `src/spring_river/analysis/phase4.py` | Phase 4 runner → `docs/phase4_baseflow.md` |
| `src/spring_river/analysis/phase5.py` | Phase 5 runner → `docs/phase5_floods.md` |
| `src/spring_river/analysis/phase6.py` | Phase 6 runner → `docs/phase6_precip.md` |
| `src/spring_river/config.py` (modify) | add `REGIONAL_SKEW`, `REGIONAL_SKEW_MSE`, `TABLES_DIR`, `RATING_FLOWS_CFS` |
| `Makefile` (modify) | `phase4`, `phase5`, `phase6`, `analysis` targets |
| `tests/test_trends.py`, `tests/test_multiple.py`, `tests/test_permutation.py`, `tests/test_segments.py`, `tests/test_baseflow.py` (extend), `tests/test_oni.py`, `tests/test_lowflow.py`, `tests/test_rating.py`, `tests/test_postflood.py`, `tests/test_pot.py`, `tests/test_freq_lp3.py`, `tests/test_interarrival.py`, `tests/test_intensity.py`, `tests/test_coupling.py`, `tests/test_analysis_common.py` | unit tests |

Shared data-frame contracts (already produced by ingest; reused throughout):

- Daily discharge/stage frames: columns `date` (datetime64, tz-naive), `value` (float64, NaN = missing), `approved` (bool).
- IV frames (`usgs.get_iv`): columns `datetime` (tz-naive US/Central), `value`, `approved`.
- Peaks (`usgs.get_peaks`): columns `date`, `peak_cfs`, `gage_ht_ft`.
- Precip (`acis.get_station_pcpn`): `date`, `pcpn_in`, `flag`. Basin precip (`prism.get_basin_pcpn`): `date`, `pcpn_in`.
- Ledger (`data/processed/annual_ledger.parquet`): `wy, peak_stage_ft, peak_cfs, days_ge_8ft, days_ge_10ft, days_ge_14ft, days_ge_16ft, min7_cfs, bfi, precip_cal_in, precip_cal_days, precip_recharge_in, complete`.

---

### Task 1: Trend statistics — Mann-Kendall, Sen slope with CI, Pettitt

**Files:**
- Create: `src/spring_river/stats/__init__.py` (empty)
- Create: `src/spring_river/stats/trends.py`
- Test: `tests/test_trends.py`

**Interfaces:**
- Produces:
  - `@dataclass(frozen=True) TrendResult(n: int, s: float, z: float, p: float, slope: float, slope_lo: float, slope_hi: float, intercept: float)`
  - `mann_kendall(x: np.ndarray) -> tuple[float, float, float]` → `(s, z, p)`; tie-corrected variance; NaN dropped by caller.
  - `sen_slope(x: np.ndarray, t: np.ndarray | None = None, alpha: float = 0.05) -> tuple[float, float, float, float]` → `(slope, lo, hi, intercept)` using Gilbert (1987) rank-based CI.
  - `trend_test(x: np.ndarray, t: np.ndarray | None = None, alpha: float = 0.05) -> TrendResult` (drops NaN pairs; raises `ValueError` if n < 8).
  - `@dataclass(frozen=True) PettittResult(n: int, k: float, change_index: int, p: float)`
  - `pettitt(x: np.ndarray) -> PettittResult`; `change_index` is the last index of the first segment (0-based).

- [ ] **Step 1: Write the failing tests**

```python
# tests/test_trends.py
import numpy as np
import pytest

from spring_river.stats.trends import mann_kendall, pettitt, sen_slope, trend_test


def test_mann_kendall_monotone_increasing_is_positive_and_significant():
    x = np.arange(20, dtype=float)
    s, z, p = mann_kendall(x)
    assert s == 190  # n(n-1)/2 concordant pairs
    assert z > 0
    assert p < 0.001


def test_mann_kendall_constant_series_is_zero():
    s, z, p = mann_kendall(np.full(15, 3.0))
    assert s == 0
    assert z == 0
    assert p == 1.0


def test_mann_kendall_tie_correction_reduces_variance():
    # Known small example (Gilbert 1987 style): n=10 with ties
    x = np.array([1, 2, 2, 3, 3, 3, 4, 5, 5, 6], dtype=float)
    s, z, p = mann_kendall(x)
    assert s == 42
    # variance without ties would be 125; with ties it is smaller -> larger |z|
    assert z > (42 - 1) / np.sqrt(125)


def test_sen_slope_recovers_linear_slope():
    t = np.arange(30)
    x = 2.5 * t + 10
    slope, lo, hi, intercept = sen_slope(x, t)
    assert abs(slope - 2.5) < 1e-9
    assert lo <= slope <= hi
    assert abs(intercept - 10) < 1e-9


def test_sen_slope_ci_contains_true_slope_with_noise():
    rng = np.random.default_rng(1)
    t = np.arange(40)
    x = 0.8 * t + rng.normal(0, 3, 40)
    slope, lo, hi, _ = sen_slope(x, t)
    assert lo < 0.8 < hi
    assert lo < slope < hi


def test_trend_test_drops_nan_and_reports_n():
    x = np.array([1, 2, np.nan, 4, 5, 6, 7, 8, 9, 10], dtype=float)
    r = trend_test(x)
    assert r.n == 9
    assert r.slope > 0


def test_trend_test_requires_min_n():
    with pytest.raises(ValueError, match="n < 8"):
        trend_test(np.arange(5, dtype=float))


def test_pettitt_finds_step_change():
    x = np.concatenate([np.full(20, 10.0), np.full(20, 20.0)])
    r = pettitt(x)
    assert r.change_index == 19
    assert r.p < 0.01


def test_pettitt_no_change_is_not_significant():
    rng = np.random.default_rng(3)
    r = pettitt(rng.normal(size=60))
    assert r.p > 0.05
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/test_trends.py -q`
Expected: FAIL with `ModuleNotFoundError: No module named 'spring_river.stats'`

- [ ] **Step 3: Implement**

```python
# src/spring_river/stats/__init__.py
```
(empty file)

```python
# src/spring_river/stats/trends.py
"""Non-parametric trend tests (spec §2.2, §2.6).

Mann-Kendall S with tie-corrected variance; Sen's slope with the Gilbert
(1987) rank-based confidence interval; Pettitt (1979) single change-point.
Every public function returns effect size + CI + n so callers can satisfy
the "no bare p-values" rule.
"""
from dataclasses import dataclass

import numpy as np
from scipy import stats

MIN_N = 8


@dataclass(frozen=True)
class TrendResult:
    n: int
    s: float
    z: float
    p: float
    slope: float
    slope_lo: float
    slope_hi: float
    intercept: float


@dataclass(frozen=True)
class PettittResult:
    n: int
    k: float
    change_index: int
    p: float


def _mk_variance(x: np.ndarray) -> float:
    n = len(x)
    var = n * (n - 1) * (2 * n + 5)
    _, counts = np.unique(x, return_counts=True)
    ties = counts[counts > 1]
    var -= np.sum(ties * (ties - 1) * (2 * ties + 5))
    return var / 18.0


def mann_kendall(x: np.ndarray) -> tuple[float, float, float]:
    x = np.asarray(x, dtype="float64")
    n = len(x)
    s = 0.0
    for i in range(n - 1):
        s += np.sign(x[i + 1 :] - x[i]).sum()
    var = _mk_variance(x)
    if var == 0 or s == 0:
        return float(s), 0.0, 1.0
    z = (s - 1) / np.sqrt(var) if s > 0 else (s + 1) / np.sqrt(var)
    p = 2 * (1 - stats.norm.cdf(abs(z)))
    return float(s), float(z), float(p)


def sen_slope(
    x: np.ndarray, t: np.ndarray | None = None, alpha: float = 0.05
) -> tuple[float, float, float, float]:
    x = np.asarray(x, dtype="float64")
    n = len(x)
    t = np.arange(n, dtype="float64") if t is None else np.asarray(t, dtype="float64")
    i, j = np.triu_indices(n, k=1)
    dt = t[j] - t[i]
    keep = dt != 0
    slopes = np.sort((x[j] - x[i])[keep] / dt[keep])
    slope = float(np.median(slopes))
    n_pairs = len(slopes)
    c = stats.norm.ppf(1 - alpha / 2) * np.sqrt(_mk_variance(x))
    m1 = int(np.floor((n_pairs - c) / 2))
    m2 = int(np.ceil((n_pairs + c) / 2))
    lo = float(slopes[max(m1, 0)])
    hi = float(slopes[min(m2, n_pairs - 1)])
    intercept = float(np.median(x - slope * t))
    return slope, lo, hi, intercept


def trend_test(
    x: np.ndarray, t: np.ndarray | None = None, alpha: float = 0.05
) -> TrendResult:
    x = np.asarray(x, dtype="float64")
    t = np.arange(len(x), dtype="float64") if t is None else np.asarray(t, dtype="float64")
    ok = ~np.isnan(x) & ~np.isnan(t)
    x, t = x[ok], t[ok]
    if len(x) < MIN_N:
        raise ValueError(f"n < {MIN_N}: got {len(x)}")
    s, z, p = mann_kendall(x)
    slope, lo, hi, intercept = sen_slope(x, t, alpha)
    return TrendResult(len(x), s, z, p, slope, lo, hi, intercept)


def pettitt(x: np.ndarray) -> PettittResult:
    x = np.asarray(x, dtype="float64")
    n = len(x)
    sign = np.sign(x[None, :] - x[:, None])  # sign[i, j] = sign(x_j - x_i)
    u = np.array([sign[: t + 1, t + 1 :].sum() for t in range(n - 1)])
    k_idx = int(np.argmax(np.abs(u)))
    k = float(abs(u[k_idx]))
    p = float(min(1.0, 2 * np.exp(-6 * k**2 / (n**3 + n**2))))
    return PettittResult(n, k, k_idx, p)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/test_trends.py -q`
Expected: 9 passed

- [ ] **Step 5: Commit**

```bash
git add src/spring_river/stats/__init__.py src/spring_river/stats/trends.py tests/test_trends.py
git commit -m "feat(study): Mann-Kendall, Sen slope with CI, Pettitt in stats/trends"
```

---

### Task 2: Benjamini-Hochberg and the Q7 permutation test

**Files:**
- Create: `src/spring_river/stats/multiple.py`
- Create: `src/spring_river/stats/permutation.py`
- Test: `tests/test_multiple.py`, `tests/test_permutation.py`

**Interfaces:**
- Produces:
  - `benjamini_hochberg(p: np.ndarray, q: float = 0.05) -> tuple[np.ndarray, np.ndarray]` → `(rejected: bool array, adjusted_p: float array)`.
  - `@dataclass(frozen=True) ConditionalRateResult(n_years: int, n_major: int, rate_after_major: float, base_rate: float, diff: float, diff_lo: float, diff_hi: float, p: float)`
  - `conditional_rate_test(major: np.ndarray, quiet: np.ndarray, n_perm: int = 10000, seed: int = 0) -> ConditionalRateResult` — `major[t]`, `quiet[t]` are bool arrays indexed by consecutive years; tests P(quiet[t+1] | major[t]) − P(quiet); CI is the 2.5–97.5 percentile of the bootstrap difference.

- [ ] **Step 1: Write the failing tests**

```python
# tests/test_multiple.py
import numpy as np

from spring_river.stats.multiple import benjamini_hochberg


def test_bh_matches_known_example():
    p = np.array([0.01, 0.04, 0.03, 0.20, 0.50])
    rejected, adj = benjamini_hochberg(p, q=0.05)
    # sorted: .01,.03,.04,.20,.50 -> adj: .05,.0667,.0667,.25,.50
    assert rejected.tolist() == [True, False, False, False, False]
    assert abs(adj[0] - 0.05) < 1e-9
    assert abs(adj[1] - 0.0667) < 1e-3


def test_bh_all_null():
    rejected, _ = benjamini_hochberg(np.array([0.3, 0.6, 0.9]))
    assert not rejected.any()
```

```python
# tests/test_permutation.py
import numpy as np

from spring_river.stats.permutation import conditional_rate_test


def test_strong_pattern_is_significant():
    # every major year followed by a quiet year; no other quiet years
    major = np.array([True, False] * 10)
    quiet = np.array([False, True] * 10)
    r = conditional_rate_test(major, quiet, n_perm=2000, seed=1)
    assert r.rate_after_major == 1.0
    assert r.diff > 0
    assert r.p < 0.05
    assert r.n_major == 10


def test_no_pattern_is_not_significant():
    rng = np.random.default_rng(5)
    major = rng.random(60) < 0.25
    quiet = rng.random(60) < 0.3
    r = conditional_rate_test(major, quiet, n_perm=2000, seed=2)
    assert r.p > 0.05


def test_no_major_years_gives_nan_rate():
    r = conditional_rate_test(np.zeros(10, bool), np.ones(10, bool), n_perm=100)
    assert np.isnan(r.rate_after_major)
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/test_multiple.py tests/test_permutation.py -q`
Expected: FAIL with `ModuleNotFoundError`

- [ ] **Step 3: Implement**

```python
# src/spring_river/stats/multiple.py
"""Benjamini-Hochberg FDR control across the Q3 index family (spec §2.6)."""
import numpy as np


def benjamini_hochberg(p: np.ndarray, q: float = 0.05) -> tuple[np.ndarray, np.ndarray]:
    p = np.asarray(p, dtype="float64")
    m = len(p)
    order = np.argsort(p)
    ranked = p[order] * m / np.arange(1, m + 1)
    adj_sorted = np.minimum.accumulate(ranked[::-1])[::-1]
    adj = np.empty(m)
    adj[order] = np.minimum(adj_sorted, 1.0)
    return adj <= q, adj
```

```python
# src/spring_river/stats/permutation.py
"""Q7: is a quiet year more likely after a major-flood year? (spec §2.3)"""
from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class ConditionalRateResult:
    n_years: int
    n_major: int
    rate_after_major: float
    base_rate: float
    diff: float
    diff_lo: float
    diff_hi: float
    p: float


def _rate_after(major: np.ndarray, quiet: np.ndarray) -> float:
    idx = np.flatnonzero(major[:-1])
    if len(idx) == 0:
        return float("nan")
    return float(quiet[idx + 1].mean())


def conditional_rate_test(
    major: np.ndarray, quiet: np.ndarray, n_perm: int = 10000, seed: int = 0
) -> ConditionalRateResult:
    major = np.asarray(major, dtype=bool)
    quiet = np.asarray(quiet, dtype=bool)
    n = len(major)
    base = float(quiet.mean())
    observed = _rate_after(major, quiet)
    diff = observed - base
    rng = np.random.default_rng(seed)
    n_major = int(major[:-1].sum())
    if n_major == 0:
        return ConditionalRateResult(n, 0, observed, base, float("nan"), float("nan"), float("nan"), float("nan"))
    perm = np.array([_rate_after(rng.permutation(major), quiet) - base for _ in range(n_perm)])
    p = float((perm >= diff).mean())
    boot = np.array(
        [
            _rate_after(major[idx := np.sort(rng.integers(0, n, n))], quiet[idx]) - quiet[idx].mean()
            for _ in range(n_perm)
        ]
    )
    boot = boot[~np.isnan(boot)]
    lo, hi = (np.percentile(boot, [2.5, 97.5]) if len(boot) else (float("nan"), float("nan")))
    return ConditionalRateResult(n, n_major, observed, base, float(diff), float(lo), float(hi), p)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/test_multiple.py tests/test_permutation.py -q`
Expected: 5 passed

- [ ] **Step 5: Commit**

```bash
git add src/spring_river/stats/multiple.py src/spring_river/stats/permutation.py tests/test_multiple.py tests/test_permutation.py
git commit -m "feat(study): Benjamini-Hochberg and conditional-rate permutation test"
```

---

### Task 3: Gap-segmented base-flow filtering (Eckhardt + Lyne-Hollick, BFI by WY)

**Files:**
- Create: `src/spring_river/hydro/segments.py`
- Modify: `src/spring_river/hydro/baseflow.py`
- Test: `tests/test_segments.py`, `tests/test_baseflow.py` (append)

**Interfaces:**
- Consumes: daily frame `date, value, approved`.
- Produces:
  - `segment_gapfree(df: pd.DataFrame, max_gap_days: int = 7) -> list[pd.DataFrame]` — reindexes to daily, linearly interpolates runs of ≤ `max_gap_days` missing days, splits at longer runs; each returned frame has `date, value` with no NaN, sorted, contiguous.
  - `lyne_hollick(q: np.ndarray, alpha: float = 0.925, passes: int = 3) -> np.ndarray`.
  - `eckhardt_segmented(df: pd.DataFrame, spinup_days: int = 30, **kw) -> pd.DataFrame` — columns `date, value, baseflow`; filter state resets at every segment; first `spinup_days` of each segment have `baseflow = NaN`.
  - `bfi_by_wy(df: pd.DataFrame, min_days: int = 300, method: str = "eckhardt") -> pd.Series` indexed by `wy`, NaN where fewer than `min_days` non-NaN baseflow days.

- [ ] **Step 1: Write the failing tests**

```python
# tests/test_segments.py
import numpy as np
import pandas as pd

from spring_river.hydro.segments import segment_gapfree


def _frame(values, start="2020-01-01"):
    dates = pd.date_range(start, periods=len(values), freq="D")
    return pd.DataFrame({"date": dates, "value": values, "approved": True})


def test_short_gap_is_interpolated():
    v = [10.0, np.nan, np.nan, 40.0]
    segs = segment_gapfree(_frame(v))
    assert len(segs) == 1
    assert segs[0]["value"].tolist() == [10.0, 20.0, 30.0, 40.0]


def test_long_gap_splits_segments():
    v = [1.0] * 5 + [np.nan] * 8 + [2.0] * 5
    segs = segment_gapfree(_frame(v))
    assert len(segs) == 2
    assert len(segs[0]) == 5 and len(segs[1]) == 5
    assert segs[1]["date"].iloc[0] == pd.Timestamp("2020-01-14")


def test_missing_rows_count_as_gap():
    df = _frame([1.0] * 5)
    later = _frame([2.0] * 5, start="2020-02-01")
    segs = segment_gapfree(pd.concat([df, later]))
    assert len(segs) == 2
```

Append to `tests/test_baseflow.py`:

```python
import pandas as pd

from spring_river.hydro.baseflow import bfi_by_wy, eckhardt_segmented, lyne_hollick


def test_lyne_hollick_bounded():
    rng = np.random.default_rng(2)
    q = np.exp(rng.normal(5, 1, size=400))
    b = lyne_hollick(q)
    assert np.all(b <= q + 1e-9) and np.all(b >= 0)


def test_eckhardt_segmented_resets_and_spins_up():
    dates = pd.date_range("2019-10-01", periods=400, freq="D")
    v = np.full(400, 300.0)
    v[100:120] = np.nan  # 20-day gap -> two segments
    df = pd.DataFrame({"date": dates, "value": v, "approved": True})
    out = eckhardt_segmented(df, spinup_days=30)
    assert out["baseflow"].iloc[:30].isna().all()          # spin-up of segment 1
    assert out["baseflow"].iloc[120:150].isna().all()      # spin-up of segment 2
    assert out["baseflow"].iloc[100:120].isna().all()      # gap itself
    assert abs(out["baseflow"].iloc[-1] - 0.8 * 300.0) < 1e-6


def test_bfi_by_wy_requires_min_days():
    dates = pd.date_range("2019-10-01", "2021-09-30", freq="D")
    df = pd.DataFrame({"date": dates, "value": 300.0, "approved": True})
    s = bfi_by_wy(df, min_days=300)
    assert set(s.index) == {2020, 2021}
    assert 0 < s.loc[2021] <= 1
    short = df[df["date"] < "2020-03-01"]
    assert np.isnan(bfi_by_wy(short, min_days=300).loc[2020])
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/test_segments.py tests/test_baseflow.py -q`
Expected: FAIL (ImportError on `segment_gapfree`, `lyne_hollick`, …)

- [ ] **Step 3: Implement**

```python
# src/spring_river/hydro/segments.py
"""Split daily series at gaps > 7 days (project rule: never interpolate
across them). Gaps of <= max_gap_days are linearly interpolated."""
import pandas as pd


def segment_gapfree(df: pd.DataFrame, max_gap_days: int = 7) -> list[pd.DataFrame]:
    s = df.set_index("date")["value"].sort_index().astype("float64")
    if s.empty:
        return []
    full = s.reindex(pd.date_range(s.index.min(), s.index.max(), freq="D"))
    missing = full.isna()
    run_id = (missing != missing.shift()).cumsum()
    run_len = missing.groupby(run_id).transform("size")
    long_gap = missing & (run_len > max_gap_days)
    filled = full.interpolate(limit_area="inside")
    filled[long_gap] = float("nan")
    seg_id = (long_gap != long_gap.shift()).cumsum()
    out = []
    for _, chunk in filled.groupby(seg_id):
        chunk = chunk.dropna()
        if len(chunk):
            out.append(chunk.rename("value").rename_axis("date").reset_index())
    return out
```

Add to `src/spring_river/hydro/baseflow.py` (keep `eckhardt` and `bfi` unchanged; add `import pandas as pd` and `from spring_river.hydro.segments import segment_gapfree`, `from spring_river.hydro.wateryear import water_year`):

```python
def lyne_hollick(q: np.ndarray, alpha: float = 0.925, passes: int = 3) -> np.ndarray:
    """Lyne-Hollick one-parameter filter, forward/backward passes (check on Eckhardt)."""
    q = np.asarray(q, dtype="float64")
    if len(q) == 0:
        return np.empty(0, dtype="float64")
    if np.isnan(q).any():
        raise ValueError("q contains NaN; segment or drop gaps before filtering")
    b = q.copy()
    for p in range(passes):
        src = b if p % 2 == 0 else b[::-1]
        quick = np.zeros_like(src)
        for t in range(1, len(src)):
            quick[t] = alpha * quick[t - 1] + (1 + alpha) / 2 * (src[t] - src[t - 1])
            quick[t] = min(max(quick[t], 0.0), src[t])
        base = src - quick
        b = base if p % 2 == 0 else base[::-1]
    return np.clip(b, 0.0, q)


def eckhardt_segmented(df: pd.DataFrame, spinup_days: int = 30, **kw) -> pd.DataFrame:
    """Eckhardt on each gap-free segment; filter state resets at every gap
    boundary (> 7 days); first `spinup_days` of each segment set to NaN."""
    frames = []
    for seg in segment_gapfree(df):
        b = eckhardt(seg["value"].to_numpy(), **kw)
        b[:spinup_days] = float("nan")
        frames.append(seg.assign(baseflow=b))
    if not frames:
        return pd.DataFrame({"date": pd.Series(dtype="datetime64[ns]"), "value": [], "baseflow": []})
    return pd.concat(frames, ignore_index=True)


def bfi_by_wy(df: pd.DataFrame, min_days: int = 300, method: str = "eckhardt") -> pd.Series:
    """Trend-safe annual BFI: sum(baseflow)/sum(flow) over days with a defined
    baseflow; NaN when fewer than `min_days` such days in the water year."""
    if method == "eckhardt":
        bf = eckhardt_segmented(df)
    elif method == "lyne_hollick":
        frames = []
        for seg in segment_gapfree(df):
            b = lyne_hollick(seg["value"].to_numpy())
            b[:30] = float("nan")
            frames.append(seg.assign(baseflow=b))
        bf = pd.concat(frames, ignore_index=True)
    else:
        raise ValueError(f"unknown method {method}")
    bf = bf.assign(wy=water_year(bf["date"]))
    ok = bf.dropna(subset=["baseflow"])
    g = ok.groupby("wy")
    out = g["baseflow"].sum() / g["value"].sum()
    out[g.size() < min_days] = float("nan")
    return out.reindex(sorted(bf["wy"].unique())).rename("bfi")
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/test_segments.py tests/test_baseflow.py -q`
Expected: all pass (3 + 10)

- [ ] **Step 5: Commit**

```bash
git add src/spring_river/hydro/segments.py src/spring_river/hydro/baseflow.py tests/test_segments.py tests/test_baseflow.py
git commit -m "feat(study): gap-segmented Eckhardt/Lyne-Hollick and trend-safe BFI by water year"
```

---

### Task 4: ONI ingest (ENSO covariate) and config additions

**Files:**
- Create: `src/spring_river/ingest/oni.py`
- Modify: `src/spring_river/config.py`
- Modify: `pyproject.toml` (add `"statsmodels>=0.14,<0.15"` to `dependencies`)
- Test: `tests/test_oni.py`

**Interfaces:**
- Produces:
  - `ONI_URL = "https://www.cpc.ncep.noaa.gov/data/indices/oni.ascii.txt"`
  - `parse_oni(text: str) -> pd.DataFrame` with columns `date` (first of the season's center month), `anom` (float).
  - `get_oni(refresh: bool = False) -> pd.DataFrame` (cached via `fetch_cached("cpc_oni", …)`).
  - `recharge_season_oni(oni: pd.DataFrame) -> pd.Series` indexed by `wy`: mean `anom` over center months Sep(wy−1)…Feb(wy).
- Config additions:

```python
TABLES_DIR = PROJECT_ROOT / "reports" / "tables"
RATING_FLOWS_CFS = (400.0, 1000.0)      # spec §2.2 stage-at-fixed-discharge
RATING_TOLERANCE = 0.05                 # ±5% flow window for IV pairs
# Bulletin 17B Plate I generalized skew for the S. Missouri / NE Arkansas
# region is approximately -0.2 with map MSE 0.302. APPROXIMATE — replace
# with the USGS Arkansas/Missouri regional-skew study value when obtained,
# and flag every B17 result as provisional until then.
REGIONAL_SKEW = -0.2
REGIONAL_SKEW_MSE = 0.302
MAJOR_FLOOD_FT = 16.0
```

- [ ] **Step 1: Write the failing tests**

```python
# tests/test_oni.py
import pandas as pd

from spring_river.ingest.oni import parse_oni, recharge_season_oni

SAMPLE = """ SEAS  YR   TOTAL   ANOM
 DJF 2019   26.55   0.70
 JFM 2019   26.87   0.70
 ASO 2019   26.60   0.30
 SON 2019   26.50   0.50
 OND 2019   26.40   0.50
 NDJ 2019   26.30   0.50
 DJF 2020   26.20   0.50
 JFM 2020   26.10   0.50
 FMA 2020   26.00   0.40
"""


def test_parse_oni_center_month():
    df = parse_oni(SAMPLE)
    assert df.loc[df["date"] == pd.Timestamp("2019-01-01"), "anom"].item() == 0.70  # DJF 2019 -> Jan 2019
    assert df.loc[df["date"] == pd.Timestamp("2019-12-01"), "anom"].item() == 0.50  # NDJ 2019 -> Dec 2019


def test_recharge_season_mean():
    df = parse_oni(SAMPLE)
    s = recharge_season_oni(df)
    # WY 2020 = Sep 2019 (ASO .30), Oct (SON .50), Nov (OND .50), Dec (NDJ .50), Jan 2020 (DJF .50), Feb (JFM .50)
    assert abs(s.loc[2020] - (0.30 + 0.50 * 5) / 6) < 1e-9
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/test_oni.py -q`
Expected: FAIL with `ModuleNotFoundError`

- [ ] **Step 3: Implement**

```python
# src/spring_river/ingest/oni.py
"""CPC Oceanic Niño Index — ENSO covariate for Q1 attribution (spec §1.3)."""
import io

import pandas as pd
import requests

from spring_river.ingest.cache import fetch_cached

ONI_URL = "https://www.cpc.ncep.noaa.gov/data/indices/oni.ascii.txt"
_CENTER_MONTH = {
    "DJF": 1, "JFM": 2, "FMA": 3, "MAM": 4, "AMJ": 5, "MJJ": 6,
    "JJA": 7, "JAS": 8, "ASO": 9, "SON": 10, "OND": 11, "NDJ": 12,
}


def parse_oni(text: str) -> pd.DataFrame:
    raw = pd.read_csv(io.StringIO(text), sep=r"\s+")
    month = raw["SEAS"].map(_CENTER_MONTH)
    date = pd.to_datetime({"year": raw["YR"], "month": month, "day": 1})
    return pd.DataFrame({"date": date, "anom": raw["ANOM"].astype("float64")}).sort_values("date").reset_index(drop=True)


def get_oni(refresh: bool = False) -> pd.DataFrame:
    def fetch() -> pd.DataFrame:
        resp = requests.get(ONI_URL, timeout=60)
        resp.raise_for_status()
        return parse_oni(resp.text)

    return fetch_cached("cpc_oni", fetch, {"source": "CPC ONI", "url": ONI_URL}, refresh=refresh)


def recharge_season_oni(oni: pd.DataFrame) -> pd.Series:
    d = oni["date"]
    wy = d.dt.year + (d.dt.month >= 9).astype(int)   # Sep..Dec belong to next WY's recharge season
    in_season = d.dt.month.isin([9, 10, 11, 12, 1, 2])
    return oni.loc[in_season].groupby(wy[in_season])["anom"].mean().rename("oni_recharge")
```

Then edit `config.py` with the block from Interfaces and add `statsmodels` to `pyproject.toml`; run `uv sync`.

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv sync && uv run pytest tests/test_oni.py -q`
Expected: 2 passed

- [ ] **Step 5: Commit**

```bash
git add src/spring_river/ingest/oni.py src/spring_river/config.py pyproject.toml uv.lock tests/test_oni.py
git commit -m "feat(study): CPC ONI ingest, B17 skew + rating constants, statsmodels dep"
```

---

### Task 5: Q1 attribution table, OLS, residual trend (`hydro/lowflow.py`)

**Files:**
- Create: `src/spring_river/hydro/lowflow.py`
- Test: `tests/test_lowflow.py`

**Interfaces:**
- Consumes: `min7` (wateryear.py), `bfi_by_wy` (Task 3), `recharge_season_oni` (Task 4), `trend_test` (Task 1).
- Produces:
  - `attribution_table(dv_q: pd.DataFrame, basin_precip: pd.DataFrame, oni: pd.DataFrame, min_precip_days: int = 165) -> pd.DataFrame` with columns `wy, min7_cfs, son_mean_cfs, bfi, p_recharge_in, p_recharge_prev_in, oni_recharge, complete`; `p_recharge_in` is NaN when fewer than `min_precip_days` non-NaN days in Sep–Feb (181/182 days possible).
  - `@dataclass(frozen=True) AttributionFit(n: int, coef: dict[str, float], ci: dict[str, tuple[float, float]], r2: float, residual_trend: TrendResult, min7_trend: TrendResult)`
  - `fit_attribution(tbl: pd.DataFrame, response: str = "min7_cfs") -> AttributionFit` — OLS `log(response) ~ p_recharge_in + p_recharge_prev_in + oni_recharge` (HC3 robust CIs); residual trend via `trend_test(resid, wy)`; also raw `min7` trend for comparison. Drops rows with `complete == False` or any NaN predictor.

- [ ] **Step 1: Write the failing tests**

```python
# tests/test_lowflow.py
import numpy as np
import pandas as pd

from spring_river.hydro.lowflow import attribution_table, fit_attribution


def _synthetic(n_years=30, seed=0):
    rng = np.random.default_rng(seed)
    start = pd.Timestamp("1990-10-01")
    dates = pd.date_range(start, periods=365 * n_years, freq="D")
    wy = dates.year + (dates.month >= 10).astype(int)
    precip_by_wy = {y: 15 + rng.normal(0, 3) for y in np.unique(wy)}
    # flow driven by that WY's recharge precip, no time trend
    q = np.array([200 + 10 * precip_by_wy[y] for y in wy]) + rng.normal(0, 5, len(dates))
    dv_q = pd.DataFrame({"date": dates, "value": q, "approved": True})
    daily_p = np.array([precip_by_wy[y] / 182 if m in (9, 10, 11, 12, 1, 2) else 0.05 for y, m in zip(wy, dates.month)])
    basin = pd.DataFrame({"date": dates, "pcpn_in": daily_p})
    oni_dates = pd.date_range(start, periods=12 * n_years, freq="MS")
    oni = pd.DataFrame({"date": oni_dates, "anom": rng.normal(0, 0.8, len(oni_dates))})
    return dv_q, basin, oni


def test_attribution_table_columns_and_precip_gate():
    dv_q, basin, oni = _synthetic()
    tbl = attribution_table(dv_q, basin, oni)
    assert list(tbl.columns) == ["wy", "min7_cfs", "son_mean_cfs", "bfi", "p_recharge_in", "p_recharge_prev_in", "oni_recharge", "complete"]
    assert tbl["p_recharge_in"].notna().sum() >= 28
    # first WY has no prior-year precip
    assert np.isnan(tbl.iloc[0]["p_recharge_prev_in"])


def test_fit_recovers_positive_precip_effect_and_no_residual_trend():
    dv_q, basin, oni = _synthetic()
    tbl = attribution_table(dv_q, basin, oni)
    fit = fit_attribution(tbl)
    assert fit.coef["p_recharge_in"] > 0
    lo, hi = fit.ci["p_recharge_in"]
    assert lo > 0
    assert fit.residual_trend.slope_lo < 0 < fit.residual_trend.slope_hi
    assert fit.n >= 25
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/test_lowflow.py -q`
Expected: FAIL with `ModuleNotFoundError`

- [ ] **Step 3: Implement**

```python
# src/spring_river/hydro/lowflow.py
"""Q1: is base flow declining secularly or tracking precipitation? (spec §2.2)

Attribution model: log(min7) ~ P_recharge(t) + P_recharge(t-1) + ONI.
The residual Mann-Kendall/Sen trend isolates non-climatic decline.
"""
from dataclasses import dataclass

import numpy as np
import pandas as pd
import statsmodels.api as sm

from spring_river.hydro.baseflow import bfi_by_wy
from spring_river.hydro.wateryear import min7, water_year
from spring_river.ingest.oni import recharge_season_oni
from spring_river.stats.trends import TrendResult, trend_test

PREDICTORS = ["p_recharge_in", "p_recharge_prev_in", "oni_recharge"]


@dataclass(frozen=True)
class AttributionFit:
    n: int
    coef: dict[str, float]
    ci: dict[str, tuple[float, float]]
    r2: float
    residual_trend: TrendResult
    min7_trend: TrendResult


def _recharge_totals(basin_precip: pd.DataFrame, min_days: int) -> pd.Series:
    d = basin_precip["date"]
    wy = d.dt.year + (d.dt.month >= 9).astype(int)
    in_season = d.dt.month.isin([9, 10, 11, 12, 1, 2])
    g = basin_precip.loc[in_season].groupby(wy[in_season])["pcpn_in"]
    total = g.sum()
    total[g.count() < min_days] = float("nan")
    return total


def attribution_table(
    dv_q: pd.DataFrame,
    basin_precip: pd.DataFrame,
    oni: pd.DataFrame,
    min_precip_days: int = 165,
) -> pd.DataFrame:
    q = dv_q.assign(wy=water_year(dv_q["date"]))
    m7 = min7(dv_q[["date", "value"]])
    son = q[q["date"].dt.month.isin([9, 10, 11])].groupby("wy")["value"].mean()
    bfi = bfi_by_wy(dv_q)
    p = _recharge_totals(basin_precip, min_precip_days)
    o = recharge_season_oni(oni)
    complete = q.groupby("wy")["date"].max() >= [pd.Timestamp(y, 9, 30) for y in q.groupby("wy")["date"].max().index]
    wys = sorted(q["wy"].unique())
    tbl = pd.DataFrame({"wy": wys})
    tbl["min7_cfs"] = tbl["wy"].map(m7)
    tbl["son_mean_cfs"] = tbl["wy"].map(son)
    tbl["bfi"] = tbl["wy"].map(bfi)
    tbl["p_recharge_in"] = tbl["wy"].map(p)
    tbl["p_recharge_prev_in"] = (tbl["wy"] - 1).map(p)
    tbl["oni_recharge"] = tbl["wy"].map(o)
    tbl["complete"] = tbl["wy"].map(complete).fillna(False).astype(bool)
    return tbl


def fit_attribution(tbl: pd.DataFrame, response: str = "min7_cfs") -> AttributionFit:
    d = tbl[tbl["complete"]].dropna(subset=[response] + PREDICTORS)
    d = d[d[response] > 0]
    y = np.log(d[response].to_numpy())
    X = sm.add_constant(d[PREDICTORS].to_numpy())
    res = sm.OLS(y, X).fit(cov_type="HC3")
    names = ["const"] + PREDICTORS
    ci_arr = res.conf_int()
    coef = {k: float(v) for k, v in zip(names, res.params)}
    ci = {k: (float(lo), float(hi)) for k, (lo, hi) in zip(names, ci_arr)}
    wy = d["wy"].to_numpy(dtype="float64")
    return AttributionFit(
        n=int(res.nobs),
        coef=coef,
        ci=ci,
        r2=float(res.rsquared),
        residual_trend=trend_test(np.asarray(res.resid), wy),
        min7_trend=trend_test(y, wy),
    )
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/test_lowflow.py -q`
Expected: 2 passed

- [ ] **Step 5: Commit**

```bash
git add src/spring_river/hydro/lowflow.py tests/test_lowflow.py
git commit -m "feat(study): Q1 attribution table, OLS with HC3 CIs, residual trend"
```

---

### Task 6: Q5 rating drift — stage at fixed discharge per water year (`qa/rating.py`)

**Files:**
- Create: `src/spring_river/qa/rating.py`
- Test: `tests/test_rating.py`

**Interfaces:**
- Consumes: IV discharge and IV stage frames (`datetime, value, approved`), `RATING_FLOWS_CFS`, `RATING_TOLERANCE`.
- Produces:
  - `pair_iv(iv_q: pd.DataFrame, iv_h: pd.DataFrame) -> pd.DataFrame` — inner join on `datetime`; columns `datetime, q_cfs, stage_ft, approved` (approved = both).
  - `stage_at_flow(pairs: pd.DataFrame, flows: tuple[float, ...] = RATING_FLOWS_CFS, tol: float = RATING_TOLERANCE, min_pairs: int = 20) -> pd.DataFrame` — one row per `(wy, flow_cfs)`: `wy, flow_cfs, stage_median_ft, stage_iqr_ft, n_pairs`; NaN stage where `n_pairs < min_pairs`.
  - `rating_shift_at_events(sf: pd.DataFrame, event_dates: pd.Series) -> pd.DataFrame` — for each event date and each flow: `event_date, flow_cfs, stage_before_ft (WY of event), stage_after_ft (WY+1), shift_ft`.

- [ ] **Step 1: Write the failing tests**

```python
# tests/test_rating.py
import numpy as np
import pandas as pd

from spring_river.qa.rating import pair_iv, rating_shift_at_events, stage_at_flow


def _iv(n_days=800, seed=0, drop_after=None, drop_ft=0.5):
    rng = np.random.default_rng(seed)
    t = pd.date_range("2018-10-01", periods=n_days * 4, freq="6h")
    q = np.exp(rng.normal(np.log(600), 0.6, len(t)))
    stage = 3.0 + 2.0 * np.log10(q / 100)          # synthetic rating
    if drop_after is not None:
        stage = np.where(t >= pd.Timestamp(drop_after), stage - drop_ft, stage)
    iv_q = pd.DataFrame({"datetime": t, "value": q, "approved": True})
    iv_h = pd.DataFrame({"datetime": t, "value": stage, "approved": True})
    return iv_q, iv_h


def test_pair_iv_inner_join():
    iv_q, iv_h = _iv()
    pairs = pair_iv(iv_q, iv_h.iloc[10:])
    assert len(pairs) == len(iv_h) - 10
    assert list(pairs.columns) == ["datetime", "q_cfs", "stage_ft", "approved"]


def test_stage_at_flow_recovers_rating():
    pairs = pair_iv(*_iv())
    sf = stage_at_flow(pairs, flows=(400.0, 1000.0), tol=0.05, min_pairs=5)
    row = sf[(sf["wy"] == 2019) & (sf["flow_cfs"] == 400.0)].iloc[0]
    assert abs(row["stage_median_ft"] - (3.0 + 2.0 * np.log10(4))) < 0.05
    assert row["n_pairs"] >= 5


def test_shift_detected_after_event():
    pairs = pair_iv(*_iv(drop_after="2019-10-01", drop_ft=0.5))
    sf = stage_at_flow(pairs, flows=(400.0,), tol=0.05, min_pairs=5)
    shifts = rating_shift_at_events(sf, pd.Series([pd.Timestamp("2019-06-01")]))
    assert abs(shifts.iloc[0]["shift_ft"] + 0.5) < 0.05
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/test_rating.py -q`
Expected: FAIL with `ModuleNotFoundError`

- [ ] **Step 3: Implement**

```python
# src/spring_river/qa/rating.py
"""Q5: is the stage-floor decline a rating artifact? Stage at fixed discharge
per water year from IV pairs (spec §2.2, risk #4). This is the IV-derived
substitute for USGS shift records, which have not been obtained."""
import pandas as pd

from spring_river.config import RATING_FLOWS_CFS, RATING_TOLERANCE
from spring_river.hydro.wateryear import water_year


def pair_iv(iv_q: pd.DataFrame, iv_h: pd.DataFrame) -> pd.DataFrame:
    m = iv_q.merge(iv_h, on="datetime", suffixes=("_q", "_h"))
    return pd.DataFrame(
        {
            "datetime": m["datetime"],
            "q_cfs": m["value_q"].astype("float64"),
            "stage_ft": m["value_h"].astype("float64"),
            "approved": m["approved_q"] & m["approved_h"],
        }
    ).dropna(subset=["q_cfs", "stage_ft"]).reset_index(drop=True)


def stage_at_flow(
    pairs: pd.DataFrame,
    flows: tuple[float, ...] = RATING_FLOWS_CFS,
    tol: float = RATING_TOLERANCE,
    min_pairs: int = 20,
) -> pd.DataFrame:
    p = pairs.assign(wy=water_year(pairs["datetime"]))
    rows = []
    for wy, grp in p.groupby("wy"):
        for f in flows:
            win = grp[(grp["q_cfs"] >= f * (1 - tol)) & (grp["q_cfs"] <= f * (1 + tol))]["stage_ft"]
            n = len(win)
            rows.append(
                {
                    "wy": int(wy),
                    "flow_cfs": float(f),
                    "stage_median_ft": float(win.median()) if n >= min_pairs else float("nan"),
                    "stage_iqr_ft": float(win.quantile(0.75) - win.quantile(0.25)) if n >= min_pairs else float("nan"),
                    "n_pairs": n,
                }
            )
    return pd.DataFrame(rows)


def rating_shift_at_events(sf: pd.DataFrame, event_dates: pd.Series) -> pd.DataFrame:
    idx = sf.set_index(["wy", "flow_cfs"])["stage_median_ft"]
    rows = []
    for d in pd.to_datetime(event_dates):
        wy = int(water_year(pd.Series([d])).iloc[0])
        for f in sorted(sf["flow_cfs"].unique()):
            before = idx.get((wy, f), float("nan"))
            after = idx.get((wy + 1, f), float("nan"))
            rows.append(
                {
                    "event_date": d,
                    "flow_cfs": f,
                    "stage_before_ft": before,
                    "stage_after_ft": after,
                    "shift_ft": after - before,
                }
            )
    return pd.DataFrame(rows)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/test_rating.py -q`
Expected: 3 passed

- [ ] **Step 5: Commit**

```bash
git add src/spring_river/qa/rating.py tests/test_rating.py
git commit -m "feat(study): Q5 stage-at-fixed-discharge rating drift from IV pairs"
```

---

### Task 7: Q4 post-flood recharge comparison (`hydro/postflood.py`)

**Files:**
- Create: `src/spring_river/hydro/postflood.py`
- Test: `tests/test_postflood.py`

**Interfaces:**
- Consumes: `eckhardt_segmented` (Task 3), a daily flow frame, basin precip frame, event dates.
- Produces:
  - `post_event_baseflow(dv_q: pd.DataFrame, event_dates: pd.Series, months: int = 6) -> pd.DataFrame` — `event_date, post_baseflow_mean_cfs, post_days, post_precip_in` (precip column filled by caller-provided frame in the next function).
  - `matched_comparison(dv_q, basin_precip, event_dates, months=6, k=3) -> pd.DataFrame` — for each event: mean base flow over the `months` after the event; the same window of the `k` non-flood years (no event within ±1 year) whose window precip total is closest; columns `event_date, post_bf_cfs, post_p_in, matched_years (str), matched_bf_cfs, matched_p_in, diff_cfs, diff_pct`.
  - `paired_summary(cmp: pd.DataFrame, n_boot: int = 5000, seed: int = 0) -> dict` → `{"n": int, "mean_diff_pct": float, "lo": float, "hi": float}` bootstrap CI on the mean of `diff_pct`.

- [ ] **Step 1: Write the failing tests**

```python
# tests/test_postflood.py
import numpy as np
import pandas as pd

from spring_river.hydro.postflood import matched_comparison, paired_summary, post_event_baseflow


def _data(n_years=12, seed=0):
    rng = np.random.default_rng(seed)
    dates = pd.date_range("2005-10-01", periods=365 * n_years, freq="D")
    q = np.full(len(dates), 400.0) + rng.normal(0, 10, len(dates))
    # flood year 2010: spike in April then depressed base flow for 6 months
    ev = pd.Timestamp("2010-04-15")
    i = np.searchsorted(dates, ev)
    q[i : i + 3] = 40000.0
    q[i + 3 : i + 183] = 250.0
    dv_q = pd.DataFrame({"date": dates, "value": q, "approved": True})
    basin = pd.DataFrame({"date": dates, "pcpn_in": 0.12})
    return dv_q, basin, pd.Series([ev])


def test_post_event_baseflow_window():
    dv_q, _, ev = _data()
    out = post_event_baseflow(dv_q, ev, months=6)
    assert out.iloc[0]["post_days"] >= 150
    assert out.iloc[0]["post_baseflow_mean_cfs"] < 350


def test_matched_comparison_negative_diff():
    dv_q, basin, ev = _data()
    cmp = matched_comparison(dv_q, basin, ev, months=6, k=3)
    assert len(cmp) == 1
    assert cmp.iloc[0]["diff_pct"] < -15
    assert "2010" not in cmp.iloc[0]["matched_years"]


def test_paired_summary_ci():
    cmp = pd.DataFrame({"diff_pct": [-20.0, -25.0, -18.0, -30.0]})
    s = paired_summary(cmp, n_boot=500)
    assert s["n"] == 4 and s["lo"] <= s["mean_diff_pct"] <= s["hi"] and s["hi"] < 0
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/test_postflood.py -q`
Expected: FAIL with `ModuleNotFoundError`

- [ ] **Step 3: Implement**

```python
# src/spring_river/hydro/postflood.py
"""Q4: do major floods reduce recharge? Post-flood base flow vs precip-matched
non-flood years (spec §2.2)."""
import numpy as np
import pandas as pd

from spring_river.hydro.baseflow import eckhardt_segmented


def _window(start: pd.Timestamp, months: int) -> tuple[pd.Timestamp, pd.Timestamp]:
    return start, start + pd.DateOffset(months=months)


def _window_mean(bf: pd.DataFrame, start: pd.Timestamp, end: pd.Timestamp) -> tuple[float, int]:
    w = bf[(bf["date"] >= start) & (bf["date"] < end)]["baseflow"].dropna()
    return (float(w.mean()) if len(w) else float("nan")), int(len(w))


def _window_precip(basin: pd.DataFrame, start: pd.Timestamp, end: pd.Timestamp) -> float:
    return float(basin[(basin["date"] >= start) & (basin["date"] < end)]["pcpn_in"].sum())


def post_event_baseflow(dv_q: pd.DataFrame, event_dates: pd.Series, months: int = 6) -> pd.DataFrame:
    bf = eckhardt_segmented(dv_q)
    rows = []
    for d in pd.to_datetime(event_dates):
        s, e = _window(d + pd.Timedelta(days=7), months)  # skip the recession's first week
        m, n = _window_mean(bf, s, e)
        rows.append({"event_date": d, "post_baseflow_mean_cfs": m, "post_days": n})
    return pd.DataFrame(rows)


def matched_comparison(
    dv_q: pd.DataFrame,
    basin_precip: pd.DataFrame,
    event_dates: pd.Series,
    months: int = 6,
    k: int = 3,
) -> pd.DataFrame:
    bf = eckhardt_segmented(dv_q)
    events = pd.to_datetime(event_dates)
    event_years = set(events.year)
    years = sorted(set(bf["date"].dt.year))
    rows = []
    for d in events:
        s, e = _window(d + pd.Timedelta(days=7), months)
        post_bf, _ = _window_mean(bf, s, e)
        post_p = _window_precip(basin_precip, s, e)
        cands = []
        for y in years:
            if any(abs(y - ey) <= 1 for ey in event_years):
                continue
            cs = s.replace(year=y)
            ce = cs + pd.DateOffset(months=months)
            m, n = _window_mean(bf, cs, ce)
            if n < months * 20:
                continue
            cands.append((abs(_window_precip(basin_precip, cs, ce) - post_p), y, m, _window_precip(basin_precip, cs, ce)))
        cands.sort()
        top = cands[:k]
        matched_bf = float(np.mean([c[2] for c in top])) if top else float("nan")
        matched_p = float(np.mean([c[3] for c in top])) if top else float("nan")
        rows.append(
            {
                "event_date": d,
                "post_bf_cfs": post_bf,
                "post_p_in": post_p,
                "matched_years": ",".join(str(c[1]) for c in top),
                "matched_bf_cfs": matched_bf,
                "matched_p_in": matched_p,
                "diff_cfs": post_bf - matched_bf,
                "diff_pct": 100.0 * (post_bf - matched_bf) / matched_bf if matched_bf else float("nan"),
            }
        )
    return pd.DataFrame(rows)


def paired_summary(cmp: pd.DataFrame, n_boot: int = 5000, seed: int = 0) -> dict:
    d = cmp["diff_pct"].dropna().to_numpy()
    rng = np.random.default_rng(seed)
    boots = np.array([rng.choice(d, len(d), replace=True).mean() for _ in range(n_boot)])
    lo, hi = np.percentile(boots, [2.5, 97.5])
    return {"n": int(len(d)), "mean_diff_pct": float(d.mean()), "lo": float(lo), "hi": float(hi)}
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/test_postflood.py -q`
Expected: 3 passed

- [ ] **Step 5: Commit**

```bash
git add src/spring_river/hydro/postflood.py tests/test_postflood.py
git commit -m "feat(study): Q4 post-flood base flow vs precip-matched years"
```

---

### Task 8: Analysis helpers and the Phase 4 runner (`docs/phase4_baseflow.md`)

**Files:**
- Create: `src/spring_river/analysis/__init__.py` (empty), `src/spring_river/analysis/common.py`, `src/spring_river/analysis/phase4.py`
- Modify: `Makefile`
- Test: `tests/test_analysis_common.py`

**Interfaces:**
- `common.py` produces:
  - `approval_variants(df: pd.DataFrame) -> dict[str, pd.DataFrame]` → `{"all": df, "approved": df[df["approved"]]}`.
  - `caption(source: str, df: pd.DataFrame) -> str` → `"source: {source}; period {min}–{max}; approved {frac:.0%}[, provisional from {date}]"`.
  - `fmt_trend(r: TrendResult, unit: str, per: str = "yr") -> str` → `"Sen slope {slope:.3g} {unit}/{per} (95% CI {lo:.3g} to {hi:.3g}); MK z={z:.2f}, p={p:.3f}; n={n}"`.
  - `sensitivity_lines(name: str, all_r: TrendResult, appr_r: TrendResult) -> list[str]` — one line per variant plus a `**CHANGED**` marker if the sign of the slope differs or the CI-includes-zero status differs.
  - `write_report(path: Path, lines: list[str]) -> None`.
- `phase4.py` produces `main()` that writes `docs/phase4_baseflow.md`, `reports/tables/phase4_attribution_{mammoth,hardy}.parquet`, `reports/tables/phase4_rating_drift.parquet`, `reports/tables/phase4_postflood.parquet`, and figures `phase4_min7_trend.png`, `phase4_residuals.png`, `phase4_rating_drift.png`, `phase4_postflood.png`.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_analysis_common.py
import pandas as pd

from spring_river.analysis.common import approval_variants, caption, fmt_trend, sensitivity_lines
from spring_river.stats.trends import TrendResult


def _df():
    d = pd.date_range("2020-01-01", periods=10, freq="D")
    return pd.DataFrame({"date": d, "value": 1.0, "approved": [True] * 7 + [False] * 3})


def test_approval_variants():
    v = approval_variants(_df())
    assert len(v["all"]) == 10 and len(v["approved"]) == 7


def test_caption_mentions_provisional():
    c = caption("USGS DV", _df())
    assert "period 2020-01-01–2020-01-10" in c and "approved 70%" in c and "provisional from 2020-01-08" in c


def test_fmt_trend_has_ci_and_n():
    r = TrendResult(30, 10, 1.5, 0.13, -2.0, -4.5, 0.4, 100)
    s = fmt_trend(r, "cfs")
    assert "-2 cfs/yr" in s and "95% CI -4.5 to 0.4" in s and "n=30" in s


def test_sensitivity_flags_sign_change():
    a = TrendResult(30, 10, 1.5, 0.13, -2.0, -4.5, 0.4, 100)
    b = TrendResult(28, -3, -0.5, 0.6, 0.5, -1.0, 2.0, 100)
    lines = sensitivity_lines("min7", a, b)
    assert any("CHANGED" in l for l in lines)
    assert not any("CHANGED" in l for l in sensitivity_lines("min7", a, a))
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_analysis_common.py -q`
Expected: FAIL with `ModuleNotFoundError`

- [ ] **Step 3: Implement `common.py`**

```python
# src/spring_river/analysis/common.py
"""Shared formatting/sensitivity helpers for the phase runners.
Enforces: captions carry source/period/approval; trend claims carry
test, effect size, CI, n; every analysis reported for all vs approved-only."""
from pathlib import Path

import pandas as pd

from spring_river.stats.trends import TrendResult


def approval_variants(df: pd.DataFrame) -> dict[str, pd.DataFrame]:
    return {"all": df, "approved": df[df["approved"]].reset_index(drop=True)}


def caption(source: str, df: pd.DataFrame) -> str:
    frac = float(df["approved"].mean()) if len(df) else float("nan")
    prov = df.loc[~df["approved"], "date"].min() if len(df) else None
    s = f"source: {source}; period {df['date'].min().date()}–{df['date'].max().date()}; approved {frac:.0%}"
    if pd.notna(prov):
        s += f", provisional from {prov.date()}"
    return s


def fmt_trend(r: TrendResult, unit: str, per: str = "yr") -> str:
    return (
        f"Sen slope {r.slope:.3g} {unit}/{per} (95% CI {r.slope_lo:.3g} to {r.slope_hi:.3g}); "
        f"MK z={r.z:.2f}, p={r.p:.3f}; n={r.n}"
    )


def _includes_zero(r: TrendResult) -> bool:
    return r.slope_lo <= 0 <= r.slope_hi


def sensitivity_lines(name: str, all_r: TrendResult, appr_r: TrendResult) -> list[str]:
    changed = (all_r.slope > 0) != (appr_r.slope > 0) or _includes_zero(all_r) != _includes_zero(appr_r)
    lines = [f"- {name} (all): {fmt_trend(all_r, '')}", f"- {name} (approved-only): {fmt_trend(appr_r, '')}"]
    if changed:
        lines.append(f"- **CHANGED**: {name} conclusion differs between all and approved-only data.")
    return lines


def write_report(path: Path, lines: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n")
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_analysis_common.py -q`
Expected: 4 passed

- [ ] **Step 5: Implement `phase4.py`**

```python
# src/spring_river/analysis/phase4.py
"""Phase 4 exit artifact: docs/phase4_baseflow.md (Q1, Q4, Q5).

Q1 primary series is the Mammoth Spring vent gauge (07069190, DV 1981->present,
no gaps) because the spring IS the river's base flow and Hardy's own record is
WY 2002+ only. Hardy min7 is reported as the secondary series.
"""
from datetime import date

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

from spring_river.analysis.common import approval_variants, caption, fmt_trend, sensitivity_lines, write_report
from spring_river.config import (
    DOCS_DIR, FIGURES_DIR, MAJOR_FLOOD_FT, PARAM_DISCHARGE, PARAM_STAGE, SITE_HARDY, SITE_MAMMOTH,
    START_DATE, TABLES_DIR,
)
from spring_river.hydro.baseflow import bfi_by_wy
from spring_river.hydro.lowflow import PREDICTORS, attribution_table, fit_attribution
from spring_river.hydro.postflood import matched_comparison, paired_summary
from spring_river.ingest import oni, prism, usgs
from spring_river.ingest.pull_all import IV_START
from spring_river.qa.rating import pair_iv, rating_shift_at_events, stage_at_flow
from spring_river.stats.trends import pettitt, trend_test


def _fit_section(label: str, dv_q: pd.DataFrame, basin: pd.DataFrame, oni_df: pd.DataFrame, lines: list[str]) -> dict:
    out = {}
    for variant, q in approval_variants(dv_q).items():
        tbl = attribution_table(q, basin, oni_df)
        fit = fit_attribution(tbl)
        out[variant] = (tbl, fit)
    tbl, fit = out["all"]
    tbl.to_parquet(TABLES_DIR / f"phase4_attribution_{label.lower()}.parquet")
    pt = pettitt(tbl.dropna(subset=["min7_cfs"])["min7_cfs"].to_numpy())
    wy_change = int(tbl.dropna(subset=["min7_cfs"])["wy"].iloc[pt.change_index])
    lines += [
        f"### {label}",
        "",
        f"- min7 raw trend: {fmt_trend(fit.min7_trend, 'log-cfs')}",
        f"- Pettitt change-point: after WY {wy_change} (K={pt.k:.0f}, p={pt.p:.3f}, n={pt.n})",
        f"- OLS log(min7) ~ {' + '.join(PREDICTORS)} (HC3): R²={fit.r2:.2f}, n={fit.n}",
    ]
    for k in PREDICTORS:
        lo, hi = fit.ci[k]
        lines.append(f"  - {k}: {fit.coef[k]:.4f} (95% CI {lo:.4f} to {hi:.4f})")
    lines += [
        f"- **Residual trend (non-climatic component): {fmt_trend(fit.residual_trend, 'log-cfs')}**",
        "",
        "Sensitivity:",
        *sensitivity_lines("residual trend", fit.residual_trend, out["approved"][1].residual_trend),
        "",
    ]
    return out


def main() -> None:
    end = date.today().isoformat()
    TABLES_DIR.mkdir(parents=True, exist_ok=True)
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    basin = prism.get_basin_pcpn(START_DATE, end)
    oni_df = oni.get_oni()
    mammoth = usgs.get_dv(SITE_MAMMOTH, PARAM_DISCHARGE, START_DATE, end)
    hardy = usgs.get_dv(SITE_HARDY, PARAM_DISCHARGE, START_DATE, end)

    lines = [f"# Phase 4 — base flow (Q1, Q4, Q5) — generated {date.today().isoformat()}", "", "## Q1 attribution", ""]
    fits = {"Mammoth": _fit_section("Mammoth", mammoth, basin, oni_df, lines),
            "Hardy": _fit_section("Hardy", hardy, basin, oni_df, lines)}

    # BFI trend (gap-segmented) on both series
    lines += ["### BFI trend (gap-segmented Eckhardt; Lyne-Hollick check)", ""]
    for label, q in (("Mammoth", mammoth), ("Hardy", hardy)):
        for method in ("eckhardt", "lyne_hollick"):
            s = bfi_by_wy(q, method=method).dropna()
            r = trend_test(s.to_numpy(), s.index.to_numpy(dtype="float64"))
            lines.append(f"- {label} BFI ({method}): {fmt_trend(r, 'BFI')}")
    lines.append("")

    # Figure: min7 series + residuals
    fig, axes = plt.subplots(2, 1, figsize=(11, 7), sharex=True)
    for label, color in (("Mammoth", "C0"), ("Hardy", "C1")):
        tbl, fit = fits[label]["all"]
        axes[0].plot(tbl["wy"], tbl["min7_cfs"], marker="o", color=color, label=f"{label} min7")
    axes[0].set_ylabel("7-day low flow (cfs)"); axes[0].legend()
    tbl, fit = fits["Mammoth"]["all"]
    d = tbl[tbl["complete"]].dropna(subset=["min7_cfs"] + PREDICTORS)
    axes[1].axhline(0, color="k", lw=0.5)
    axes[1].plot(d["wy"], fit.residual_trend.intercept + fit.residual_trend.slope * d["wy"], "r--", label="Sen residual trend")
    axes[1].set_ylabel("Mammoth OLS residual (log-cfs)"); axes[1].set_xlabel("water year"); axes[1].legend()
    fig.suptitle(f"Q1 base-flow attribution\n{caption(f'USGS DV {SITE_MAMMOTH} + {SITE_HARDY}', mammoth)}", fontsize=9)
    fig.tight_layout(rect=(0, 0, 1, 0.94)); fig.savefig(FIGURES_DIR / "phase4_min7_trend.png", dpi=150)
    lines += ["![min7](../reports/figures/phase4_min7_trend.png)", ""]

    # Q5 rating drift
    iv_q = usgs.get_iv(SITE_HARDY, PARAM_DISCHARGE, IV_START, end)
    iv_h = usgs.get_iv(SITE_HARDY, PARAM_STAGE, IV_START, end)
    pairs = pair_iv(iv_q, iv_h)
    sf = stage_at_flow(pairs)
    sf.to_parquet(TABLES_DIR / "phase4_rating_drift.parquet")
    peaks = usgs.get_peaks(SITE_HARDY)
    majors = peaks[peaks["gage_ht_ft"] >= MAJOR_FLOOD_FT]["date"]
    shifts = rating_shift_at_events(sf, majors)
    lines += ["## Q5 rating drift (stage at fixed discharge, Hardy IV pairs)", "",
              sf.pivot(index="wy", columns="flow_cfs", values="stage_median_ft").round(2).to_markdown(), "",
              "Shift across ≥16 ft events (WY of event → WY+1):", "", shifts.round(2).to_markdown(index=False), ""]
    for f in sf["flow_cfs"].unique():
        s = sf[sf["flow_cfs"] == f].dropna(subset=["stage_median_ft"])
        r = trend_test(s["stage_median_ft"].to_numpy(), s["wy"].to_numpy(dtype="float64"))
        lines.append(f"- stage at {f:.0f} cfs: {fmt_trend(r, 'ft')}")
    fig, ax = plt.subplots(figsize=(10, 4))
    for f in sf["flow_cfs"].unique():
        s = sf[sf["flow_cfs"] == f]
        ax.plot(s["wy"], s["stage_median_ft"], marker="o", label=f"{f:.0f} cfs")
    for d in majors:
        ax.axvline(d.year + (d.month >= 10), color="grey", lw=0.5, ls=":")
    ax.set_ylabel("stage (ft)"); ax.set_xlabel("water year"); ax.legend()
    ax.set_title(f"Q5 stage at fixed discharge; dotted = ≥16 ft flood WY\n{caption(f'USGS IV {SITE_HARDY}', iv_h.rename(columns={'datetime': 'date'}))}", fontsize=9)
    fig.tight_layout(); fig.savefig(FIGURES_DIR / "phase4_rating_drift.png", dpi=150)
    lines += ["", "![rating](../reports/figures/phase4_rating_drift.png)", ""]

    # Q4 post-flood recharge
    lines += ["## Q4 post-flood base flow vs precip-matched years", ""]
    for label, q in (("Mammoth", mammoth), ("Hardy", hardy)):
        cmp = matched_comparison(q, basin, majors)
        cmp.to_parquet(TABLES_DIR / f"phase4_postflood_{label.lower()}.parquet")
        s = paired_summary(cmp)
        lines += [f"### {label}", "", cmp.round(1).to_markdown(index=False), "",
                  f"- mean post-flood base-flow difference: {s['mean_diff_pct']:.1f}% (bootstrap 95% CI {s['lo']:.1f} to {s['hi']:.1f}); n={s['n']} events", ""]

    lines += [
        "## Limitations",
        "",
        "- Regional-skew, datum and USGS rating-shift records remain unobtained; Q5 rests on IV-derived stage-at-flow only.",
        "- Hardy series is WY 2002+ (n≤24); Mammoth Spring vent carries the 1981+ record.",
        "- Q4 n equals the number of ≥16 ft events in the Hardy peak file; CI is a bootstrap on a handful of events.",
        "- Basin precip is the 30 km West Plains PRISM buffer, not a dye-traced recharge polygon.",
    ]
    write_report(DOCS_DIR / "phase4_baseflow.md", lines)
    print(f"wrote {DOCS_DIR / 'phase4_baseflow.md'}")


if __name__ == "__main__":
    main()
```

Add to `Makefile`:

```make
phase4:
	uv run python -m spring_river.analysis.phase4
```

- [ ] **Step 6: Run the runner end-to-end and inspect**

Run: `make phase4 && head -60 docs/phase4_baseflow.md`
Expected: report written; every trend line carries slope, CI, n; no tracebacks. If the IV discharge pull for Hardy is not cached, `get_iv` fetches it (single range or per-year; see `pull_all._pull_iv` if NWIS rejects the range — copy that fallback into phase4 if needed).

- [ ] **Step 7: Run the full suite, commit**

```bash
uv run pytest -q
git add src/spring_river/analysis/__init__.py src/spring_river/analysis/common.py src/spring_river/analysis/phase4.py Makefile tests/test_analysis_common.py docs/phase4_baseflow.md reports/figures/phase4_*.png
git commit -m "feat(study): Phase 4 runner — Q1 attribution, Q4 post-flood, Q5 rating drift report"
```

---

### Task 9: POT declustering, annual counts, dispersion test (`hydro/pot.py`)

**Files:**
- Create: `src/spring_river/hydro/pot.py`
- Test: `tests/test_pot.py`

**Interfaces:**
- Consumes: daily max stage frame `date, value, approved`.
- Produces:
  - `pot_events(daily: pd.DataFrame, threshold: float, min_sep_days: int = 7) -> pd.DataFrame` — `start, end, peak_date, peak_value`; exceedance runs separated by fewer than `min_sep_days` non-exceeding days are merged.
  - `annual_counts(events: pd.DataFrame, wys: list[int]) -> pd.Series` indexed by `wy` (zeros for years with no events, only over `wys`).
  - `dispersion_test(counts: pd.Series) -> dict` → `{"n": int, "mean": float, "var": float, "dispersion": float, "p": float}` with `p` from `(n-1)·D ~ χ²(n-1)` two-sided.

- [ ] **Step 1: Write the failing tests**

```python
# tests/test_pot.py
import numpy as np
import pandas as pd

from spring_river.hydro.pot import annual_counts, dispersion_test, pot_events


def _stage():
    d = pd.date_range("2019-10-01", periods=400, freq="D")
    v = np.full(400, 5.0)
    v[10:13] = 9.0           # event 1
    v[15:16] = 8.5           # 2 days later -> merged into event 1
    v[100:101] = 12.0        # event 2
    v[300:302] = 8.2         # event 3 (WY 2021)
    return pd.DataFrame({"date": d, "value": v, "approved": True})


def test_declustering_merges_close_exceedances():
    ev = pot_events(_stage(), threshold=8.0, min_sep_days=7)
    assert len(ev) == 3
    assert ev.iloc[0]["peak_value"] == 9.0
    assert ev.iloc[0]["end"] == pd.Timestamp("2019-10-16")


def test_annual_counts_fills_zero_years():
    ev = pot_events(_stage(), threshold=8.0)
    c = annual_counts(ev, [2020, 2021, 2022])
    assert c.tolist() == [2, 1, 0]


def test_dispersion_test_poisson_like():
    rng = np.random.default_rng(0)
    c = pd.Series(rng.poisson(2.0, 40))
    r = dispersion_test(c)
    assert 0.5 < r["dispersion"] < 1.6 and r["p"] > 0.01
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/test_pot.py -q`
Expected: FAIL with `ModuleNotFoundError`

- [ ] **Step 3: Implement**

```python
# src/spring_river/hydro/pot.py
"""Partial-duration series: declustered peaks-over-threshold with 7-day
independence, annual counts, Poisson dispersion test (spec §2.3)."""
import pandas as pd
from scipy import stats

from spring_river.hydro.wateryear import water_year


def pot_events(daily: pd.DataFrame, threshold: float, min_sep_days: int = 7) -> pd.DataFrame:
    d = daily.sort_values("date").reset_index(drop=True)
    exc = d[d["value"] >= threshold]
    if exc.empty:
        return pd.DataFrame({"start": pd.Series(dtype="datetime64[ns]"), "end": pd.Series(dtype="datetime64[ns]"),
                             "peak_date": pd.Series(dtype="datetime64[ns]"), "peak_value": pd.Series(dtype="float64")})
    gap = exc["date"].diff().dt.days.fillna(0)
    cluster = (gap > min_sep_days).cumsum()
    rows = []
    for _, grp in exc.groupby(cluster):
        peak = grp.loc[grp["value"].idxmax()]
        rows.append({"start": grp["date"].min(), "end": grp["date"].max(),
                     "peak_date": peak["date"], "peak_value": float(peak["value"])})
    return pd.DataFrame(rows)


def annual_counts(events: pd.DataFrame, wys: list[int]) -> pd.Series:
    if events.empty:
        return pd.Series(0, index=pd.Index(wys, name="wy"), name="count")
    wy = water_year(events["peak_date"])
    c = wy.value_counts()
    return pd.Series([int(c.get(y, 0)) for y in wys], index=pd.Index(wys, name="wy"), name="count")


def dispersion_test(counts: pd.Series) -> dict:
    n = int(len(counts))
    mean = float(counts.mean())
    var = float(counts.var(ddof=1))
    if mean == 0:
        return {"n": n, "mean": mean, "var": var, "dispersion": float("nan"), "p": float("nan")}
    d = var / mean
    stat = (n - 1) * d
    cdf = stats.chi2.cdf(stat, n - 1)
    p = float(2 * min(cdf, 1 - cdf))
    return {"n": n, "mean": mean, "var": var, "dispersion": float(d), "p": p}
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/test_pot.py -q`
Expected: 3 passed

- [ ] **Step 5: Commit**

```bash
git add src/spring_river/hydro/pot.py tests/test_pot.py
git commit -m "feat(study): POT declustering, annual counts, dispersion test"
```

---

### Task 10: LP3 flood frequency with weighted skew, Grubbs-Beck, bootstrap CIs (`hydro/freq_lp3.py`)

**Files:**
- Create: `src/spring_river/hydro/freq_lp3.py`
- Test: `tests/test_freq_lp3.py`

**Interfaces:**
- Produces:
  - `@dataclass(frozen=True) LP3Fit(n: int, mean_log: float, sd_log: float, station_skew: float, weighted_skew: float, low_outlier_threshold_cfs: float, n_dropped: int)`
  - `station_skew(x: np.ndarray) -> float` (B17 bias-corrected sample skew).
  - `skew_mse(g: float, n: int) -> float` (B17B eq. 6).
  - `weighted_skew(gs: float, n: int, gr: float = REGIONAL_SKEW, mse_r: float = REGIONAL_SKEW_MSE) -> float`.
  - `grubbs_beck_threshold(logq: np.ndarray) -> float` (B17B eq. 8a; single low-outlier test).
  - `fit_lp3(peaks_cfs: np.ndarray, regional_skew: float | None = REGIONAL_SKEW, mse_r: float = REGIONAL_SKEW_MSE) -> LP3Fit` (drops peaks below the GB threshold, refits; `regional_skew=None` → station skew only).
  - `quantile(fit: LP3Fit, return_period: float) -> float` (cfs) via `scipy.stats.pearson3.ppf(1 - 1/T, skew)`.
  - `return_period(fit: LP3Fit, q_cfs: float) -> float`.
  - `bootstrap_quantiles(peaks_cfs, return_periods: tuple[float, ...], n_boot=2000, seed=0, **fit_kw) -> pd.DataFrame` — `return_period, q_cfs, q_lo, q_hi` (5–95%).
  - `stage_flow_fit(peaks: pd.DataFrame) -> tuple[float, float, float]` — log-log OLS `log10(peak_cfs) = a + b·log10(gage_ht_ft)`, returns `(a, b, r2)`; `stage_to_flow(a, b, stage_ft)`, `flow_to_stage(a, b, q_cfs)`.

- [ ] **Step 1: Write the failing tests**

```python
# tests/test_freq_lp3.py
import numpy as np
import pandas as pd
from scipy import stats

from spring_river.hydro.freq_lp3 import (
    bootstrap_quantiles, fit_lp3, flow_to_stage, grubbs_beck_threshold, quantile, return_period,
    skew_mse, stage_flow_fit, stage_to_flow, station_skew, weighted_skew,
)


def _lp3_sample(n=80, seed=0, mean=4.3, sd=0.3, skew=-0.3):
    rng = np.random.default_rng(seed)
    return 10 ** stats.pearson3.rvs(skew, loc=mean, scale=sd, size=n, random_state=rng)


def test_station_skew_symmetric_sample_near_zero():
    x = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9], dtype=float)
    assert abs(station_skew(x)) < 1e-9


def test_skew_mse_b17b_values():
    # B17B eq 6: |G|=0.2, n=50 -> A=-0.314, B=0.888 -> MSE=10^(A - B*log10(5))
    assert abs(skew_mse(0.2, 50) - 10 ** (-0.314 - 0.888 * np.log10(5))) < 1e-9


def test_weighted_skew_between_station_and_regional():
    gw = weighted_skew(0.4, 30, gr=-0.2, mse_r=0.302)
    assert -0.2 < gw < 0.4


def test_grubbs_beck_flags_low_outlier():
    logq = np.log10(_lp3_sample())
    logq[0] = 2.0  # absurdly low peak
    thr = grubbs_beck_threshold(logq)
    assert logq[0] < thr < np.median(logq)


def test_fit_and_quantile_roundtrip():
    x = _lp3_sample(n=200)
    fit = fit_lp3(x, regional_skew=None)
    q100 = quantile(fit, 100)
    assert abs(return_period(fit, q100) - 100) < 1e-6
    assert quantile(fit, 2) < quantile(fit, 10) < q100
    assert abs(fit.mean_log - 4.3) < 0.05


def test_bootstrap_ci_brackets_point_estimate():
    x = _lp3_sample()
    tbl = bootstrap_quantiles(x, (2, 10, 100), n_boot=200, regional_skew=None)
    assert list(tbl.columns) == ["return_period", "q_cfs", "q_lo", "q_hi"]
    assert (tbl["q_lo"] <= tbl["q_cfs"]).all() and (tbl["q_cfs"] <= tbl["q_hi"]).all()


def test_stage_flow_fit_roundtrip():
    h = np.linspace(6, 23, 24)
    q = 10 ** (2.0 + 1.8 * np.log10(h))
    a, b, r2 = stage_flow_fit(pd.DataFrame({"peak_cfs": q, "gage_ht_ft": h}))
    assert abs(a - 2.0) < 1e-9 and abs(b - 1.8) < 1e-9 and r2 > 0.999
    assert abs(flow_to_stage(a, b, stage_to_flow(a, b, 16.0)) - 16.0) < 1e-9
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/test_freq_lp3.py -q`
Expected: FAIL with `ModuleNotFoundError`

- [ ] **Step 3: Implement**

```python
# src/spring_river/hydro/freq_lp3.py
"""Log-Pearson III flood frequency (spec §2.3).

This is LP3 by method of moments with Bulletin 17B/17C-style weighted skew,
a single Grubbs-Beck low-outlier screen, and parametric-bootstrap CIs. It is
NOT the full Expected Moments Algorithm (no censored/historical-period
likelihood); PeakFQ/EMA is the documented follow-up. Regional skew comes from
config.REGIONAL_SKEW (approximate; see config comment).
"""
from dataclasses import dataclass

import numpy as np
import pandas as pd
from scipy import stats

from spring_river.config import REGIONAL_SKEW, REGIONAL_SKEW_MSE


@dataclass(frozen=True)
class LP3Fit:
    n: int
    mean_log: float
    sd_log: float
    station_skew: float
    weighted_skew: float
    low_outlier_threshold_cfs: float
    n_dropped: int


def station_skew(x: np.ndarray) -> float:
    x = np.asarray(x, dtype="float64")
    n = len(x)
    m, s = x.mean(), x.std(ddof=1)
    if s == 0:
        return 0.0
    return float(n / ((n - 1) * (n - 2)) * np.sum(((x - m) / s) ** 3))


def skew_mse(g: float, n: int) -> float:
    ag = abs(g)
    a = -0.33 + 0.08 * ag if ag <= 0.90 else -0.52 + 0.30 * ag
    b = 0.94 - 0.26 * ag if ag <= 1.50 else 0.55
    return float(10 ** (a - b * np.log10(n / 10)))


def weighted_skew(gs: float, n: int, gr: float = REGIONAL_SKEW, mse_r: float = REGIONAL_SKEW_MSE) -> float:
    mse_s = skew_mse(gs, n)
    return float((mse_r * gs + mse_s * gr) / (mse_r + mse_s))


def grubbs_beck_threshold(logq: np.ndarray) -> float:
    n = len(logq)
    kn = -0.9043 + 3.345 * np.sqrt(np.log10(n)) - 0.4046 * np.log10(n)
    return float(logq.mean() - kn * logq.std(ddof=1))


def fit_lp3(
    peaks_cfs: np.ndarray,
    regional_skew: float | None = REGIONAL_SKEW,
    mse_r: float = REGIONAL_SKEW_MSE,
) -> LP3Fit:
    x = np.log10(np.asarray(peaks_cfs, dtype="float64"))
    x = x[np.isfinite(x)]
    thr = grubbs_beck_threshold(x)
    kept = x[x >= thr]
    n_dropped = int(len(x) - len(kept))
    gs = station_skew(kept)
    gw = gs if regional_skew is None else weighted_skew(gs, len(kept), regional_skew, mse_r)
    return LP3Fit(len(kept), float(kept.mean()), float(kept.std(ddof=1)), gs, gw, float(10 ** thr), n_dropped)


def quantile(fit: LP3Fit, return_period: float) -> float:
    k = stats.pearson3.ppf(1 - 1 / return_period, fit.weighted_skew)
    return float(10 ** (fit.mean_log + k * fit.sd_log))


def return_period(fit: LP3Fit, q_cfs: float) -> float:
    k = (np.log10(q_cfs) - fit.mean_log) / fit.sd_log
    p_exc = 1 - stats.pearson3.cdf(k, fit.weighted_skew)
    return float(1 / p_exc) if p_exc > 0 else float("inf")


def bootstrap_quantiles(
    peaks_cfs: np.ndarray,
    return_periods: tuple[float, ...],
    n_boot: int = 2000,
    seed: int = 0,
    **fit_kw,
) -> pd.DataFrame:
    x = np.asarray(peaks_cfs, dtype="float64")
    fit = fit_lp3(x, **fit_kw)
    rng = np.random.default_rng(seed)
    sims = np.empty((n_boot, len(return_periods)))
    for i in range(n_boot):
        f = fit_lp3(rng.choice(x, len(x), replace=True), **fit_kw)
        sims[i] = [quantile(f, t) for t in return_periods]
    lo, hi = np.percentile(sims, [5, 95], axis=0)
    point = np.array([quantile(fit, t) for t in return_periods])
    return pd.DataFrame({"return_period": return_periods, "q_cfs": point,
                         "q_lo": np.minimum(lo, point), "q_hi": np.maximum(hi, point)})


def stage_flow_fit(peaks: pd.DataFrame) -> tuple[float, float, float]:
    d = peaks.dropna(subset=["peak_cfs", "gage_ht_ft"])
    d = d[(d["peak_cfs"] > 0) & (d["gage_ht_ft"] > 0)]
    x, y = np.log10(d["gage_ht_ft"].to_numpy()), np.log10(d["peak_cfs"].to_numpy())
    res = stats.linregress(x, y)
    return float(res.intercept), float(res.slope), float(res.rvalue**2)


def stage_to_flow(a: float, b: float, stage_ft: float) -> float:
    return float(10 ** (a + b * np.log10(stage_ft)))


def flow_to_stage(a: float, b: float, q_cfs: float) -> float:
    return float(10 ** ((np.log10(q_cfs) - a) / b))
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/test_freq_lp3.py -q`
Expected: 7 passed

- [ ] **Step 5: Commit**

```bash
git add src/spring_river/hydro/freq_lp3.py tests/test_freq_lp3.py
git commit -m "feat(study): LP3 flood frequency with weighted skew, Grubbs-Beck, bootstrap CIs"
```

---

### Task 11: Q6 inter-arrival test and antecedent conditions (`hydro/interarrival.py`)

**Files:**
- Create: `src/spring_river/hydro/interarrival.py`
- Test: `tests/test_interarrival.py`

**Interfaces:**
- Produces:
  - `interarrival_test(event_dates: pd.Series, n_boot: int = 2000, seed: int = 0) -> dict` → `{"n_events": int, "mean_gap_yr": float, "median_gap_yr": float, "cv": float, "ks_stat": float, "p_boot": float}` — KS statistic of gaps (years) vs exponential with the fitted rate; `p_boot` from parametric bootstrap (Lilliefors-style, because the rate is estimated).
  - `antecedent_conditions(dv_q: pd.DataFrame, basin_precip: pd.DataFrame, event_dates: pd.Series, bfi_days: int = 60, precip_days: int = 30) -> pd.DataFrame` — `event_date, bfi_prior, precip_prior_in, baseflow_prior_cfs`.

- [ ] **Step 1: Write the failing tests**

```python
# tests/test_interarrival.py
import numpy as np
import pandas as pd

from spring_river.hydro.interarrival import antecedent_conditions, interarrival_test


def test_regular_cadence_rejects_exponential():
    dates = pd.Series(pd.to_datetime([f"{y}-04-01" for y in range(1980, 2024, 4)]))
    r = interarrival_test(dates, n_boot=500)
    assert r["n_events"] == 11
    assert abs(r["mean_gap_yr"] - 4.0) < 0.05
    assert r["cv"] < 0.1
    assert r["p_boot"] < 0.05


def test_poisson_cadence_is_consistent_with_exponential():
    rng = np.random.default_rng(0)
    gaps = rng.exponential(3.0, 40)
    dates = pd.Series(pd.Timestamp("1900-01-01") + pd.to_timedelta(np.cumsum(gaps) * 365.25, unit="D"))
    r = interarrival_test(dates, n_boot=500)
    assert r["p_boot"] > 0.05


def test_antecedent_conditions_windows():
    d = pd.date_range("2019-10-01", periods=400, freq="D")
    dv_q = pd.DataFrame({"date": d, "value": 300.0, "approved": True})
    basin = pd.DataFrame({"date": d, "pcpn_in": 0.1})
    out = antecedent_conditions(dv_q, basin, pd.Series([pd.Timestamp("2020-06-01")]))
    assert abs(out.iloc[0]["precip_prior_in"] - 3.0) < 1e-9
    assert 0 < out.iloc[0]["bfi_prior"] <= 1
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/test_interarrival.py -q`
Expected: FAIL with `ModuleNotFoundError`

- [ ] **Step 3: Implement**

```python
# src/spring_river/hydro/interarrival.py
"""Q6: is the ~4-year major-flood cadence real? Inter-arrival distribution vs
exponential (parametric-bootstrap KS). Plus antecedent conditions before
≥14 ft events (spec §2.3)."""
import numpy as np
import pandas as pd
from scipy import stats

from spring_river.hydro.baseflow import eckhardt_segmented


def interarrival_test(event_dates: pd.Series, n_boot: int = 2000, seed: int = 0) -> dict:
    d = pd.to_datetime(event_dates).sort_values().to_numpy()
    gaps = np.diff(d).astype("timedelta64[D]").astype(float) / 365.25
    n = len(gaps)
    rate = 1 / gaps.mean()
    ks = stats.kstest(gaps, "expon", args=(0, 1 / rate)).statistic
    rng = np.random.default_rng(seed)
    sims = np.empty(n_boot)
    for i in range(n_boot):
        g = rng.exponential(1 / rate, n)
        sims[i] = stats.kstest(g, "expon", args=(0, g.mean())).statistic
    return {
        "n_events": int(len(d)),
        "mean_gap_yr": float(gaps.mean()),
        "median_gap_yr": float(np.median(gaps)),
        "cv": float(gaps.std(ddof=1) / gaps.mean()),
        "ks_stat": float(ks),
        "p_boot": float((sims >= ks).mean()),
    }


def antecedent_conditions(
    dv_q: pd.DataFrame,
    basin_precip: pd.DataFrame,
    event_dates: pd.Series,
    bfi_days: int = 60,
    precip_days: int = 30,
) -> pd.DataFrame:
    bf = eckhardt_segmented(dv_q)
    rows = []
    for d in pd.to_datetime(event_dates):
        w = bf[(bf["date"] >= d - pd.Timedelta(days=bfi_days)) & (bf["date"] < d)].dropna(subset=["baseflow"])
        p = basin_precip[(basin_precip["date"] >= d - pd.Timedelta(days=precip_days)) & (basin_precip["date"] < d)]
        rows.append(
            {
                "event_date": d,
                "bfi_prior": float(w["baseflow"].sum() / w["value"].sum()) if len(w) and w["value"].sum() > 0 else float("nan"),
                "precip_prior_in": float(p["pcpn_in"].sum()),
                "baseflow_prior_cfs": float(w["baseflow"].mean()) if len(w) else float("nan"),
            }
        )
    return pd.DataFrame(rows)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/test_interarrival.py -q`
Expected: 3 passed

- [ ] **Step 5: Commit**

```bash
git add src/spring_river/hydro/interarrival.py tests/test_interarrival.py
git commit -m "feat(study): Q6 inter-arrival bootstrap KS and antecedent conditions"
```

---

### Task 12: Phase 5 runner (`docs/phase5_floods.md`)

**Files:**
- Create: `src/spring_river/analysis/phase5.py`
- Modify: `Makefile`

**Interfaces:**
- Consumes: Tasks 1, 2, 9, 10, 11; `usgs.get_peaks`, `usgs.get_dv`, `usgs.get_iv`, `daily_max_stage`, `nwps.historic_crests`, `prism.get_basin_pcpn`, `common.*`.
- Produces: `docs/phase5_floods.md`; tables `phase5_lp3_{hardy,imboden}.parquet`, `phase5_return_periods_stage.parquet`, `phase5_pot_counts.parquet`; figures `phase5_freq_curves.png`, `phase5_pot_counts.png`.

- [ ] **Step 1: Implement**

```python
# src/spring_river/analysis/phase5.py
"""Phase 5 exit artifact: docs/phase5_floods.md (Q2, Q6, Q7, Q8).

Series decisions (data_inventory.md): Imboden 1915–2025 annual peaks (n=90)
is the long frequency series; Hardy 2002–2025 (n=24) is the site series;
the 1982-12-03 29.0 ft NWS crest is reported as a historical exceedance
only (no flow; not in the LP3 fit — EMA/PeakFQ follow-up).
"""
from datetime import date

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from spring_river.analysis.common import approval_variants, caption, fmt_trend, sensitivity_lines, write_report
from spring_river.config import (
    DOCS_DIR, FIGURES_DIR, MAJOR_FLOOD_FT, PARAM_DISCHARGE, PARAM_STAGE, REGIONAL_SKEW, SITE_HARDY, SITE_IMBODEN,
    START_DATE, TABLES_DIR,
)
from spring_river.hydro.freq_lp3 import (
    bootstrap_quantiles, fit_lp3, flow_to_stage, return_period, stage_flow_fit, stage_to_flow,
)
from spring_river.hydro.interarrival import antecedent_conditions, interarrival_test
from spring_river.hydro.pot import annual_counts, dispersion_test, pot_events
from spring_river.hydro.wateryear import daily_max_stage, water_year
from spring_river.ingest import nwps, prism, usgs
from spring_river.ingest.pull_all import IV_START
from spring_river.stats.permutation import conditional_rate_test
from spring_river.stats.trends import pettitt, trend_test

RETURN_PERIODS = (1.25, 2, 5, 10, 25, 50, 100)
STAGE_THRESHOLDS_FT = (8.0, 10.0, 14.0, 16.0, 20.0, 23.0)
SPLIT_WY = 2008


def _peaks_by_wy(peaks: pd.DataFrame) -> pd.DataFrame:
    p = peaks.assign(wy=water_year(peaks["date"]))
    return p.sort_values("peak_cfs", ascending=False).drop_duplicates("wy").sort_values("wy").reset_index(drop=True)


def _lp3_table(label: str, peaks: pd.DataFrame, lines: list[str], regional_skew: float | None) -> pd.DataFrame:
    x = peaks["peak_cfs"].dropna().to_numpy()
    fit = fit_lp3(x, regional_skew=regional_skew)
    tbl = bootstrap_quantiles(x, RETURN_PERIODS, regional_skew=regional_skew)
    tbl.to_parquet(TABLES_DIR / f"phase5_lp3_{label.lower()}.parquet")
    lines += [
        f"### {label} (n={fit.n}, WY {int(peaks['wy'].min())}–{int(peaks['wy'].max())}, "
        f"station skew {fit.station_skew:.2f}, weighted skew {fit.weighted_skew:.2f}, "
        f"low outliers dropped {fit.n_dropped} below {fit.low_outlier_threshold_cfs:.0f} cfs)",
        "",
        tbl.round(0).to_markdown(index=False),
        "",
    ]
    return tbl


def main() -> None:
    end = date.today().isoformat()
    TABLES_DIR.mkdir(parents=True, exist_ok=True); FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    hardy_pk = _peaks_by_wy(usgs.get_peaks(SITE_HARDY))
    imb_pk = _peaks_by_wy(usgs.get_peaks(SITE_IMBODEN))
    hardy_dv = usgs.get_dv(SITE_HARDY, PARAM_DISCHARGE, START_DATE, end)
    stage = daily_max_stage(usgs.get_iv(SITE_HARDY, PARAM_STAGE, IV_START, end))
    basin = prism.get_basin_pcpn(START_DATE, end)
    crests = nwps.historic_crests(nwps.get_gauge_info())

    lines = [f"# Phase 5 — floods (Q2, Q6, Q7, Q8) — generated {date.today().isoformat()}", "",
             "## Q8 LP3 flood frequency (5–95% bootstrap CI)", "",
             f"Regional skew {REGIONAL_SKEW} (approximate, see config); sensitivity row uses station skew only.", ""]
    hardy_tbl = _lp3_table("Hardy", hardy_pk, lines, REGIONAL_SKEW)
    _lp3_table("Hardy — station skew only", hardy_pk, lines, None)
    imb_tbl = _lp3_table("Imboden", imb_pk, lines, REGIONAL_SKEW)

    # stage thresholds -> flow -> return period (Hardy)
    a, b, r2 = stage_flow_fit(hardy_pk)
    fit_h = fit_lp3(hardy_pk["peak_cfs"].dropna().to_numpy())
    n_wy = len(hardy_pk)
    rows = []
    for h in STAGE_THRESHOLDS_FT:
        q = stage_to_flow(a, b, h)
        emp = int((hardy_pk["gage_ht_ft"] >= h).sum())
        hist_n = int((crests["stage_ft"] >= h).sum())
        rows.append({"stage_ft": h, "flow_cfs": q, "lp3_return_period_yr": return_period(fit_h, q),
                     "empirical_exceedances_2002_2025": emp,
                     "empirical_return_period_yr": n_wy / emp if emp else float("inf"),
                     "nws_crests_ge_stage_1982_2025": hist_n})
    rp = pd.DataFrame(rows)
    rp.to_parquet(TABLES_DIR / "phase5_return_periods_stage.parquet")
    lines += ["### Stage thresholds at Hardy", "",
              f"Stage→flow from the 24 annual-peak (stage, flow) pairs: log10 Q = {a:.3f} + {b:.3f}·log10 H (R²={r2:.3f}).", "",
              rp.round(1).to_markdown(index=False), "",
              "NWS crest count includes the 1982-12-03 29.0 ft record; the Hardy systematic record is WY 2002+.", ""]

    # Q2 stationarity
    lines += ["## Q2 stationarity", ""]
    for label, pk in (("Hardy", hardy_pk), ("Imboden", imb_pk)):
        x = np.log10(pk["peak_cfs"].to_numpy()); wy = pk["wy"].to_numpy(dtype="float64")
        r = trend_test(x, wy); pt = pettitt(x)
        lines += [f"- {label} annual peaks (log10 cfs): {fmt_trend(r, 'log10-cfs')}; "
                  f"Pettitt after WY {int(pk['wy'].iloc[pt.change_index])} (p={pt.p:.3f})"]
    pre = imb_pk[imb_pk["wy"] < SPLIT_WY]; post = imb_pk[imb_pk["wy"] >= SPLIT_WY]
    lines += ["", f"Imboden LP3 split at WY {SPLIT_WY}:", ""]
    _lp3_table(f"Imboden WY <{SPLIT_WY}", pre, lines, REGIONAL_SKEW)
    _lp3_table(f"Imboden WY ≥{SPLIT_WY}", post, lines, REGIONAL_SKEW)

    # POT (Hardy daily max stage, WY 2008+)
    lines += ["## Partial-duration series (Hardy daily max IV stage, 7-day declustering)", ""]
    wys = sorted(set(water_year(stage["date"])))
    counts = {}
    for variant, st in approval_variants(stage).items():
        for h in (8.0, 10.0, 14.0, 16.0):
            ev = pot_events(st, h)
            c = annual_counts(ev, wys)
            counts[(variant, h)] = c
            if variant == "all":
                dt = dispersion_test(c)
                r = trend_test(c.to_numpy(dtype="float64"), np.array(wys, dtype="float64"))
                lines.append(f"- ≥{h:.0f} ft: {int(c.sum())} events; mean {dt['mean']:.2f}/yr; "
                             f"dispersion {dt['dispersion']:.2f} (p={dt['p']:.3f}); count trend {fmt_trend(r, 'events')}")
    pot_tbl = pd.DataFrame({f"ge_{int(h)}ft_{v}": c for (v, h), c in counts.items()})
    pot_tbl.to_parquet(TABLES_DIR / "phase5_pot_counts.parquet")
    lines += ["", "Sensitivity (approved-only) totals: " +
              ", ".join(f"≥{int(h)} ft {int(c.sum())}" for (v, h), c in counts.items() if v == "approved"), ""]

    # Q6 inter-arrival of >=16 ft events: peaks file for WY<2008, POT for WY>=2008, plus 1982 crest
    major_pre = hardy_pk[(hardy_pk["wy"] < 2008) & (hardy_pk["gage_ht_ft"] >= MAJOR_FLOOD_FT)]["date"]
    major_post = pot_events(stage, MAJOR_FLOOD_FT)["peak_date"]
    majors = pd.concat([major_pre, major_post]).sort_values().reset_index(drop=True)
    majors_hist = pd.concat([crests[crests["stage_ft"] >= 29.0]["date"], majors]).sort_values().reset_index(drop=True)
    lines += ["## Q6 inter-arrival of ≥16 ft events", "",
              "Events: " + ", ".join(d.strftime("%Y-%m-%d") for d in majors), ""]
    for label, ev in (("2002–present", majors), ("with 1982 crest", majors_hist)):
        r = interarrival_test(ev)
        lines.append(f"- {label}: n={r['n_events']}, mean gap {r['mean_gap_yr']:.2f} yr, median {r['median_gap_yr']:.2f}, "
                     f"CV {r['cv']:.2f}; KS vs exponential {r['ks_stat']:.2f}, bootstrap p={r['p_boot']:.3f}")
    lines.append("")

    # Q7 quiet year after major
    ledger_like = hardy_pk.set_index("wy")["gage_ht_ft"].reindex(range(int(hardy_pk["wy"].min()), int(hardy_pk["wy"].max()) + 1))
    major = (ledger_like >= MAJOR_FLOOD_FT).to_numpy(); quiet = (ledger_like < 8.0).to_numpy()
    q7 = conditional_rate_test(major, quiet)
    lines += ["## Q7 quiet year (<8 ft peak) after a ≥16 ft year", "",
              f"- P(quiet | prior major) = {q7.rate_after_major:.2f} vs base rate {q7.base_rate:.2f}; "
              f"difference {q7.diff:+.2f} (bootstrap 95% CI {q7.diff_lo:+.2f} to {q7.diff_hi:+.2f}); "
              f"permutation p={q7.p:.3f}; n_major={q7.n_major}, n_years={q7.n_years}", ""]

    # antecedent conditions before >=14 ft
    mod = hardy_pk[hardy_pk["gage_ht_ft"] >= 14.0]["date"]
    ante = antecedent_conditions(hardy_dv, basin, mod)
    lines += ["## Antecedent conditions before ≥14 ft peaks (60-day BFI, 30-day basin precip)", "",
              ante.round(2).to_markdown(index=False), ""]

    # figure: frequency curves
    fig, ax = plt.subplots(figsize=(8, 5))
    for label, tbl in (("Hardy", hardy_tbl), ("Imboden", imb_tbl)):
        ax.plot(tbl["return_period"], tbl["q_cfs"], marker="o", label=label)
        ax.fill_between(tbl["return_period"], tbl["q_lo"], tbl["q_hi"], alpha=0.2)
    ax.set_xscale("log"); ax.set_yscale("log"); ax.set_xlabel("return period (yr)"); ax.set_ylabel("peak flow (cfs)"); ax.legend()
    ax.set_title(f"LP3 frequency curves, 5–95% bootstrap\nsource: USGS annual peaks {SITE_HARDY} (WY 2002–2025), {SITE_IMBODEN} (WY 1915–2025); peaks are approved", fontsize=9)
    fig.tight_layout(); fig.savefig(FIGURES_DIR / "phase5_freq_curves.png", dpi=150)
    fig, ax = plt.subplots(figsize=(10, 4))
    for h in (8.0, 10.0, 14.0, 16.0):
        ax.plot(wys, counts[("all", h)].to_numpy(), marker="o", label=f"≥{h:.0f} ft")
    ax.set_xlabel("water year"); ax.set_ylabel("events / yr"); ax.legend()
    ax.set_title(f"POT event counts\n{caption(f'USGS IV stage {SITE_HARDY} daily max', stage)}", fontsize=9)
    fig.tight_layout(); fig.savefig(FIGURES_DIR / "phase5_pot_counts.png", dpi=150)
    lines += ["![freq](../reports/figures/phase5_freq_curves.png)", "", "![pot](../reports/figures/phase5_pot_counts.png)", ""]

    lines += ["## Stationarity verdict", "",
              "Fill from the numbers above using the rule: 'non-stationary' only if the Imboden peak trend CI excludes zero "
              "AND the split-period 10-yr quantile CIs do not overlap; otherwise 'no detectable change in frequency; "
              "magnitude tier comparison rests on n=24 at Hardy'.", "",
              "## Limitations", "",
              "- LP3/MOM with weighted skew, not EMA; 1982 historical crest not in the fit. Regional skew approximate.",
              "- Hardy n=24; return periods beyond ~50 yr are extrapolation — CIs say so.",
              "- Stage↔flow mapping is a log-log fit to annual-peak pairs, not the USGS rating; rating shifts (Q5) propagate here.",
              "- POT and Q6 post-2008 events use daily MAX IV stage (upper bound vs a daily-mean product)."]
    write_report(DOCS_DIR / "phase5_floods.md", lines)
    print(f"wrote {DOCS_DIR / 'phase5_floods.md'}")


if __name__ == "__main__":
    main()
```

Add to `Makefile`:

```make
phase5:
	uv run python -m spring_river.analysis.phase5
```

- [ ] **Step 2: Run end-to-end, then replace the verdict placeholder with the actual verdict**

Run: `make phase5 && sed -n 1,80p docs/phase5_floods.md`
Expected: report and 4 tables written. Then edit the "Stationarity verdict" block in `phase5.py` to print the verdict computed from the numbers (implement as: `verdict = "non-stationary" if (imb_trend.slope_lo > 0 or imb_trend.slope_hi < 0) and not overlap else "no detectable change in flood frequency"` where `overlap` compares the 10-yr rows of the pre/post Imboden tables; re-run `make phase5`). The report must not ship with the instruction text.

- [ ] **Step 3: Full suite, commit**

```bash
uv run pytest -q
git add src/spring_river/analysis/phase5.py Makefile docs/phase5_floods.md reports/figures/phase5_*.png
git commit -m "feat(study): Phase 5 runner — LP3 return periods, stationarity, POT, Q6, Q7 report"
```

---

### Task 13: Q3 precipitation intensity indices with coverage gate (`climate/intensity.py`)

**Files:**
- Create: `src/spring_river/climate/__init__.py` (empty), `src/spring_river/climate/intensity.py`
- Test: `tests/test_intensity.py`

**Interfaces:**
- Consumes: precip frame `date, pcpn_in` (station or basin).
- Produces:
  - `INDEX_COLUMNS = ["total_in", "recharge_in", "growing_in", "days_ge_0p5", "days_ge_1", "days_ge_2", "max1_in", "max3_in", "top5_frac", "sdii_in"]`
  - `annual_indices(precip: pd.DataFrame, min_coverage: float = 0.9) -> pd.DataFrame` — one row per calendar `year` with `year, n_days, coverage` + `INDEX_COLUMNS`; all index columns NaN when `coverage < min_coverage`. `recharge_in` = Sep(year−1)–Feb(year); `growing_in` = Mar–Aug; `max3_in` = max rolling 3-day sum; `top5_frac` = sum of 5 wettest days / total; `sdii_in` = total / wet days (≥0.01 in).
  - `index_trends(idx: pd.DataFrame, q: float = 0.05) -> pd.DataFrame` — one row per index: `index, n, slope_per_decade, lo, hi, z, p, p_bh, significant_bh`.

- [ ] **Step 1: Write the failing tests**

```python
# tests/test_intensity.py
import numpy as np
import pandas as pd

from spring_river.climate.intensity import INDEX_COLUMNS, annual_indices, index_trends


def _precip(years=range(1990, 2020), seed=0):
    rng = np.random.default_rng(seed)
    d = pd.date_range(f"{min(years)}-01-01", f"{max(years)}-12-31", freq="D")
    p = np.where(rng.random(len(d)) < 0.25, rng.exponential(0.4, len(d)), 0.0)
    return pd.DataFrame({"date": d, "pcpn_in": p})


def test_annual_indices_shape_and_values():
    idx = annual_indices(_precip())
    assert list(idx.columns) == ["year", "n_days", "coverage"] + INDEX_COLUMNS
    row = idx[idx["year"] == 2000].iloc[0]
    assert row["coverage"] == 1.0
    assert row["days_ge_0p5"] >= row["days_ge_1"] >= row["days_ge_2"]
    assert row["max3_in"] >= row["max1_in"]
    assert 0 < row["top5_frac"] < 1


def test_coverage_gate_nulls_indices():
    p = _precip()
    p.loc[(p["date"].dt.year == 2005) & (p["date"].dt.month <= 3), "pcpn_in"] = np.nan
    idx = annual_indices(p, min_coverage=0.9)
    row = idx[idx["year"] == 2005].iloc[0]
    assert row["coverage"] < 0.9 and np.isnan(row["total_in"])


def test_index_trends_has_bh_column():
    tr = index_trends(annual_indices(_precip()))
    assert set(tr["index"]) == set(INDEX_COLUMNS)
    assert {"slope_per_decade", "lo", "hi", "p_bh", "significant_bh"} <= set(tr.columns)
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/test_intensity.py -q`
Expected: FAIL with `ModuleNotFoundError`

- [ ] **Step 3: Implement**

```python
# src/spring_river/climate/__init__.py
```
(empty)

```python
# src/spring_river/climate/intensity.py
"""Q3: precipitation regime indices per calendar year (spec §2.4) with a
coverage gate — a year missing >10% of days yields NaN, never a low total."""
import numpy as np
import pandas as pd

from spring_river.stats.multiple import benjamini_hochberg
from spring_river.stats.trends import trend_test

INDEX_COLUMNS = ["total_in", "recharge_in", "growing_in", "days_ge_0p5", "days_ge_1", "days_ge_2",
                 "max1_in", "max3_in", "top5_frac", "sdii_in"]
WET_DAY_IN = 0.01


def annual_indices(precip: pd.DataFrame, min_coverage: float = 0.9) -> pd.DataFrame:
    s = precip.set_index("date")["pcpn_in"].sort_index().astype("float64")
    s = s.reindex(pd.date_range(s.index.min(), s.index.max(), freq="D"))
    roll3 = s.rolling(3, min_periods=3).sum()
    rows = []
    for year in range(s.index.min().year, s.index.max().year + 1):
        y = s[str(year)]
        n_in_year = len(pd.date_range(f"{year}-01-01", f"{year}-12-31", freq="D"))
        cov = float(y.notna().sum() / n_in_year)
        row = {"year": year, "n_days": int(y.notna().sum()), "coverage": cov}
        if cov < min_coverage or y.dropna().empty:
            rows.append({**row, **{c: float("nan") for c in INDEX_COLUMNS}})
            continue
        rech = s[f"{year - 1}-09-01":f"{year}-02-28"]
        grow = s[f"{year}-03-01":f"{year}-08-31"]
        total = float(y.sum())
        wet = y[y >= WET_DAY_IN]
        rows.append({**row,
            "total_in": total,
            "recharge_in": float(rech.sum()) if rech.notna().mean() >= min_coverage else float("nan"),
            "growing_in": float(grow.sum()),
            "days_ge_0p5": int((y >= 0.5).sum()), "days_ge_1": int((y >= 1.0).sum()), "days_ge_2": int((y >= 2.0).sum()),
            "max1_in": float(y.max()), "max3_in": float(roll3[str(year)].max()),
            "top5_frac": float(y.nlargest(5).sum() / total) if total > 0 else float("nan"),
            "sdii_in": float(total / len(wet)) if len(wet) else float("nan")})
    return pd.DataFrame(rows)


def index_trends(idx: pd.DataFrame, q: float = 0.05) -> pd.DataFrame:
    rows = []
    for c in INDEX_COLUMNS:
        d = idx.dropna(subset=[c])
        r = trend_test(d[c].to_numpy(dtype="float64"), d["year"].to_numpy(dtype="float64"))
        rows.append({"index": c, "n": r.n, "slope_per_decade": 10 * r.slope, "lo": 10 * r.slope_lo,
                     "hi": 10 * r.slope_hi, "z": r.z, "p": r.p})
    out = pd.DataFrame(rows)
    rejected, adj = benjamini_hochberg(out["p"].to_numpy(), q)
    return out.assign(p_bh=adj, significant_bh=rejected)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/test_intensity.py -q`
Expected: 3 passed

- [ ] **Step 5: Commit**

```bash
git add src/spring_river/climate/__init__.py src/spring_river/climate/intensity.py tests/test_intensity.py
git commit -m "feat(study): Q3 annual precipitation intensity indices with coverage gate and BH trends"
```

---

### Task 14: Precip → spring-flow lag correlation (`climate/coupling.py`)

**Files:**
- Create: `src/spring_river/climate/coupling.py`
- Test: `tests/test_coupling.py`

**Interfaces:**
- Produces:
  - `monthly_series(precip: pd.DataFrame, dv_q: pd.DataFrame, min_days: int = 25) -> pd.DataFrame` — `month (Timestamp, MS), p_in, q_cfs` (NaN when either month has < `min_days` non-NaN days).
  - `lag_correlation(m: pd.DataFrame, max_lag: int = 12, n_boot: int = 1000, seed: int = 0) -> pd.DataFrame` — `lag, r, r_lo, r_hi, n` where `r` = Pearson between `p_in[t-lag]` and `log(q_cfs[t])` on anomalies (monthly climatology removed); CI by block bootstrap of 12-month blocks.
  - `response_lag(lc: pd.DataFrame) -> int` — lag with maximum `r`.

- [ ] **Step 1: Write the failing tests**

```python
# tests/test_coupling.py
import numpy as np
import pandas as pd

from spring_river.climate.coupling import lag_correlation, monthly_series, response_lag


def _coupled(lag_months=2, seed=0):
    rng = np.random.default_rng(seed)
    d = pd.date_range("1995-01-01", "2020-12-31", freq="D")
    p = np.where(rng.random(len(d)) < 0.3, rng.exponential(0.3, len(d)), 0.0)
    precip = pd.DataFrame({"date": d, "pcpn_in": p})
    mp = precip.set_index("date")["pcpn_in"].resample("MS").sum()
    q_month = 200 + 40 * mp.shift(lag_months).fillna(mp.mean())
    q = q_month.reindex(d, method="ffill") + rng.normal(0, 3, len(d))
    return precip, pd.DataFrame({"date": d, "value": q.to_numpy(), "approved": True})


def test_monthly_series_columns():
    m = monthly_series(*_coupled())
    assert list(m.columns) == ["month", "p_in", "q_cfs"]
    assert m["p_in"].notna().sum() > 300


def test_lag_correlation_peaks_at_true_lag():
    m = monthly_series(*_coupled(lag_months=2))
    lc = lag_correlation(m, max_lag=6, n_boot=100)
    assert list(lc.columns) == ["lag", "r", "r_lo", "r_hi", "n"]
    assert response_lag(lc) == 2
    best = lc[lc["lag"] == 2].iloc[0]
    assert best["r_lo"] <= best["r"] <= best["r_hi"]
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/test_coupling.py -q`
Expected: FAIL with `ModuleNotFoundError`

- [ ] **Step 3: Implement**

```python
# src/spring_river/climate/coupling.py
"""Monthly basin precip vs monthly spring/river flow, lags 0–12 months →
aquifer response time (spec §2.4). Anomalies (climatology removed) so the
shared seasonal cycle does not masquerade as coupling."""
import numpy as np
import pandas as pd


def monthly_series(precip: pd.DataFrame, dv_q: pd.DataFrame, min_days: int = 25) -> pd.DataFrame:
    p = precip.set_index("date")["pcpn_in"].astype("float64")
    q = dv_q.set_index("date")["value"].astype("float64")
    pm = p.resample("MS").agg(["sum", "count"])
    qm = q.resample("MS").agg(["mean", "count"])
    idx = pm.index.union(qm.index)
    out = pd.DataFrame({"month": idx})
    out["p_in"] = pm["sum"].where(pm["count"] >= min_days).reindex(idx).to_numpy()
    out["q_cfs"] = qm["mean"].where(qm["count"] >= min_days).reindex(idx).to_numpy()
    return out.reset_index(drop=True)


def _anomalies(m: pd.DataFrame) -> pd.DataFrame:
    d = m.copy()
    mon = d["month"].dt.month
    d["p_a"] = d["p_in"] - d.groupby(mon)["p_in"].transform("mean")
    lq = np.log(d["q_cfs"])
    d["q_a"] = lq - lq.groupby(mon).transform("mean")
    return d


def _lag_r(d: pd.DataFrame, lag: int) -> tuple[float, int]:
    x = d["p_a"].shift(lag)
    ok = x.notna() & d["q_a"].notna()
    if ok.sum() < 24:
        return float("nan"), int(ok.sum())
    return float(np.corrcoef(x[ok], d["q_a"][ok])[0, 1]), int(ok.sum())


def lag_correlation(m: pd.DataFrame, max_lag: int = 12, n_boot: int = 1000, seed: int = 0) -> pd.DataFrame:
    d = _anomalies(m)
    rng = np.random.default_rng(seed)
    n_blocks = len(d) // 12
    rows = []
    for lag in range(max_lag + 1):
        r, n = _lag_r(d, lag)
        boots = []
        for _ in range(n_boot):
            starts = rng.integers(0, len(d) - 12, n_blocks)
            sample = pd.concat([d.iloc[s : s + 12] for s in starts], ignore_index=True)
            boots.append(_lag_r(sample, lag)[0])
        boots = np.array([b for b in boots if not np.isnan(b)])
        lo, hi = (np.percentile(boots, [2.5, 97.5]) if len(boots) else (float("nan"), float("nan")))
        rows.append({"lag": lag, "r": r, "r_lo": float(min(lo, r)), "r_hi": float(max(hi, r)), "n": n})
    return pd.DataFrame(rows)


def response_lag(lc: pd.DataFrame) -> int:
    return int(lc.loc[lc["r"].idxmax(), "lag"])
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/test_coupling.py -q`
Expected: 2 passed

- [ ] **Step 5: Commit**

```bash
git add src/spring_river/climate/coupling.py tests/test_coupling.py
git commit -m "feat(study): monthly precip-to-flow lag correlation with block bootstrap"
```

---

### Task 15: Phase 6 runner (`docs/phase6_precip.md`) and `make analysis`

**Files:**
- Create: `src/spring_river/analysis/phase6.py`
- Modify: `Makefile`

**Interfaces:**
- Consumes: Tasks 13–14, `acis.get_station_pcpn`, `prism.get_basin_pcpn`, `usgs.get_dv`, `qa.crosscheck.precip_overlap`, `common.*`.
- Produces: `docs/phase6_precip.md`; tables `phase6_indices_{USC00238880,KUNO,basin}.parquet`, `phase6_index_trends.parquet`, `phase6_lag_correlation.parquet`; figures `phase6_indices.png`, `phase6_lag_correlation.png`.

- [ ] **Step 1: Implement**

```python
# src/spring_river/analysis/phase6.py
"""Phase 6 exit artifact: docs/phase6_precip.md (Q3 + coupling).

Series: USC00238880 (West Plains COOP, 1948→; primary for trend because
KUNO ASOS only starts 1998), KUNO (1998→; check), PRISM 30 km basin mean
(1981→). Also resolves the qa_report open item: KUNO-vs-COOP agreement is
re-tested on monthly totals, where the ~7 AM COOP observation-day offset
should wash out.
"""
from datetime import date

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from spring_river.analysis.common import caption, write_report
from spring_river.climate.coupling import lag_correlation, monthly_series, response_lag
from spring_river.climate.intensity import INDEX_COLUMNS, annual_indices, index_trends
from spring_river.config import DOCS_DIR, FIGURES_DIR, PARAM_DISCHARGE, SITE_MAMMOTH, START_DATE, TABLES_DIR
from spring_river.ingest import acis, prism, usgs
from spring_river.ingest.pull_all import PRECIP_SIDS


def _monthly_agreement(a: pd.DataFrame, b: pd.DataFrame) -> dict:
    ma = a.set_index("date")["pcpn_in"].resample("MS").agg(["sum", "count"])
    mb = b.set_index("date")["pcpn_in"].resample("MS").agg(["sum", "count"])
    j = ma.join(mb, lsuffix="_a", rsuffix="_b", how="inner")
    j = j[(j["count_a"] >= 25) & (j["count_b"] >= 25)]
    return {"months": int(len(j)), "r": float(np.corrcoef(j["sum_a"], j["sum_b"])[0, 1]),
            "ratio": float(j["sum_b"].sum() / j["sum_a"].sum())}


def main() -> None:
    end = date.today().isoformat()
    TABLES_DIR.mkdir(parents=True, exist_ok=True); FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    coop = acis.get_station_pcpn(PRECIP_SIDS[1], "1948-01-01", end)
    kuno = acis.get_station_pcpn(PRECIP_SIDS[0], START_DATE, end)
    basin = prism.get_basin_pcpn(START_DATE, end)
    mammoth = usgs.get_dv(SITE_MAMMOTH, PARAM_DISCHARGE, START_DATE, end)

    lines = [f"# Phase 6 — precipitation regime (Q3) — generated {date.today().isoformat()}", "",
             "## Station agreement on monthly totals (qa_report follow-up)", ""]
    ag = _monthly_agreement(kuno, coop)
    lines += [f"- KUNO vs USC00238880 monthly totals: r={ag['r']:.2f}, ratio COOP/KUNO={ag['ratio']:.2f}, n={ag['months']} months "
              f"(daily r was 0.42 in qa_report; monthly aggregation removes the observation-day offset).", ""]

    trends = {}
    for label, df in (("USC00238880", coop), ("KUNO", kuno), ("basin", basin)):
        idx = annual_indices(df)
        idx.to_parquet(TABLES_DIR / f"phase6_indices_{label}.parquet")
        tr = index_trends(idx).assign(series=label)
        trends[label] = tr
        # incomplete current year is gated by coverage automatically
        lines += [f"## {label}: index trends (Sen slope per decade, 95% CI; BH-adjusted p across {len(INDEX_COLUMNS)} indices)",
                  "", f"period {int(idx['year'].min())}–{int(idx['year'].max())}; years passing 90% coverage: {int(idx['total_in'].notna().sum())}", "",
                  tr.drop(columns="series").round(3).to_markdown(index=False), ""]
    pd.concat(trends.values()).to_parquet(TABLES_DIR / "phase6_index_trends.parquet")

    # coupling: basin precip -> Mammoth Spring flow
    m = monthly_series(basin, mammoth)
    lc = lag_correlation(m)
    lc.to_parquet(TABLES_DIR / "phase6_lag_correlation.parquet")
    lines += ["## Coupling: monthly basin precip → Mammoth Spring flow (anomaly correlation by lag)", "",
              lc.round(3).to_markdown(index=False), "",
              f"- response lag (max r): {response_lag(lc)} months", ""]

    fig, axes = plt.subplots(3, 1, figsize=(11, 9), sharex=True)
    idx = pd.read_parquet(TABLES_DIR / "phase6_indices_USC00238880.parquet")
    axes[0].bar(idx["year"], idx["total_in"]); axes[0].set_ylabel("annual total (in)")
    axes[1].plot(idx["year"], idx["days_ge_1"], marker="o"); axes[1].set_ylabel("days ≥ 1 in")
    axes[2].plot(idx["year"], idx["max1_in"], marker="o"); axes[2].set_ylabel("max 1-day (in)"); axes[2].set_xlabel("year")
    fig.suptitle("Q3 indices — USC00238880 (West Plains COOP); source: RCC-ACIS; years <90% coverage omitted", fontsize=9)
    fig.tight_layout(rect=(0, 0, 1, 0.95)); fig.savefig(FIGURES_DIR / "phase6_indices.png", dpi=150)
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.errorbar(lc["lag"], lc["r"], yerr=[lc["r"] - lc["r_lo"], lc["r_hi"] - lc["r"]], marker="o")
    ax.set_xlabel("lag (months)"); ax.set_ylabel("r (anomalies)")
    ax.set_title(f"basin precip → Mammoth Spring flow\n{caption(f'USGS DV {SITE_MAMMOTH} + PRISM 30 km', mammoth)}", fontsize=9)
    fig.tight_layout(); fig.savefig(FIGURES_DIR / "phase6_lag_correlation.png", dpi=150)
    lines += ["![indices](../reports/figures/phase6_indices.png)", "", "![lag](../reports/figures/phase6_lag_correlation.png)", "",
              "## Limitations", "",
              "- Station indices are point measurements; basin indices are a 4 km grid mean (smoother extremes by construction).",
              "- USC00238880 has 32 gaps > 7 days; years failing 90% coverage are NaN, not low.",
              "- Precip series carry no approval flag; the all/approved-only rule does not apply here. Mammoth flow used in coupling is 99% approved."]
    write_report(DOCS_DIR / "phase6_precip.md", lines)
    print(f"wrote {DOCS_DIR / 'phase6_precip.md'}")


if __name__ == "__main__":
    main()
```

Add to `Makefile` (and extend `.PHONY`):

```make
phase6:
	uv run python -m spring_river.analysis.phase6

analysis: ledger phase4 phase5 phase6
```

- [ ] **Step 2: Run end-to-end**

Run: `make phase6 && sed -n 1,60p docs/phase6_precip.md`
Expected: report, 5 tables, 2 figures. Note the COOP pull from 1948 creates a new cache key only if `get_station_pcpn` names include the start date — it does not (`acis_pcpn_USC00238880`), so the existing 1981+ cache is returned. Accept 1981+ for this run and record in the report that the COOP series starts 1981 in this build; a 1948 backfill is a separate `refresh=True` pull.

- [ ] **Step 3: Full suite, commit**

```bash
uv run pytest -q
git add src/spring_river/analysis/phase6.py Makefile docs/phase6_precip.md reports/figures/phase6_*.png
git commit -m "feat(study): Phase 6 runner — precip index trends, station agreement, precip-flow lag"
```

---

### Task 16: Reproducibility check, docs, and handoff

**Files:**
- Modify: `spring-river-study/CLAUDE.md` (Analysis order line), `spring-river-study/.gitignore` (confirm `reports/tables/*.parquet` policy — keep tables tracked; they are small)
- Modify: `spring_river_research.md` (append "Phase 4–6 decisions" section)

- [ ] **Step 1: Fresh-run check**

```bash
uv run pytest -q
make analysis 2>&1 | tail -20
git status --short
```
Expected: suite green; three reports regenerate identically (diff `docs/phase*_*.md` against the committed versions — only the `generated` date line may change).

- [ ] **Step 2: Record decisions in `spring_river_research.md`**

Append:

```markdown
## Phase 4–6 decisions — 2026-08-25

- Q1 primary series: Mammoth Spring vent DV (07069190). Hardy min7 secondary (WY 2002+).
- Trend stack: in-repo Mann-Kendall / Sen (Gilbert CI) / Pettitt (`stats/trends.py`); OLS via statsmodels HC3.
- BFI trends use gap-segmented Eckhardt with 30-day spin-up; Lyne-Hollick as check.
- Flood frequency: LP3/MOM + B17B weighted skew (REGIONAL_SKEW=-0.2 approx) + Grubbs-Beck + bootstrap CI. NOT EMA. 1982 crest reported as historical exceedance only. PeakFQ follow-up open.
- Stage↔flow at Hardy from annual-peak pairs (log-log). USGS rating shifts still unobtained → Q5/Q8 provisional.
- Precip station agreement re-tested monthly (Phase 6) per qa_report note.
```

- [ ] **Step 3: Update `CLAUDE.md` analysis-order line**

Replace `Phases 0–8 in plan.md. Do not start Phase 4+ until QA report is reviewed.` with `Phases 0–8 in plan.md. Phases 0–6 complete; Phase 7 (report assembly) next. Outputs: docs/phase4_baseflow.md, docs/phase5_floods.md, docs/phase6_precip.md.`

- [ ] **Step 4: Commit**

```bash
git add spring-river-study/CLAUDE.md spring-river-study/spring_river_research.md spring-river-study/reports/tables/*.parquet
git commit -m "docs(study): record Phase 4-6 decisions; mark phases complete"
```

- [ ] **Step 5: Independent adversarial review (Nick's standing rule)**

Run `superpowers:requesting-code-review` / the `codex-signoff` skill on the whole Phase 4–6 diff with the deliverables: confirm/refute the three reports' headline numbers, list what was missed, cite file:line. Fold accepted findings into a `fix(study):` commit before merging.

---

## Self-review

**Spec coverage.** §2.2 base flow: min7 ✔ (T5), Sep–Nov mean ✔ (`son_mean_cfs`, T5), Eckhardt + Lyne-Hollick + BFI/yr ✔ (T3), MK/Sen/Pettitt ✔ (T1), attribution OLS with ONI + residual trend ✔ (T4–5), rating drift 400/1000 cfs ✔ (T6), post-flood recharge ✔ (T7). §2.3 floods: LP3 with regional skew + low outliers + CIs ✔ (T10; EMA explicitly not done and documented), MK/Pettitt on peaks + split fits ✔ (T12), POT at 8/10/14/16 + dispersion ✔ (T9), inter-arrival vs exponential ✔ (T11), Q7 permutation ✔ (T2), antecedent BFI + 30-day precip ✔ (T11). §2.4 precip: totals/seasonal/intensity indices ✔ (T13), BH ✔ (T2/T13), cross-correlation lags 0–12 ✔ (T14). §2.5 seasonality/recession: **not covered** — peak-timing circular statistics and master recession curve are deferred to Phase 7 scope; flagged here so it is a conscious omission, not a silent one. §2.6: CIs everywhere, BH, plain-language effect sizes ✔. Spectral check for Q6: replaced by the CV + bootstrap KS (n≈8 makes a spectrum meaningless); stated in the report limitations.

**Placeholder scan.** Task 12 Step 2 deliberately contains an instruction to replace the verdict block with computed text before commit — that step is explicit and must be done, not shipped. No other TBD/TODO.

**Type consistency.** `TrendResult` fields used in `common.fmt_trend` match T1. `bfi_by_wy(df, min_days, method)` used in T5 and T8 with the T3 signature. `pot_events(daily, threshold, min_sep_days)` and `annual_counts(events, wys)` used in T12 as defined in T9. `fit_lp3(x, regional_skew=…)` keyword matches T10; `bootstrap_quantiles(..., regional_skew=None)` passes through `**fit_kw` ✔. `historic_crests` returns `date, stage_ft, flow_cfs` ✔ used in T12. `eckhardt_segmented` output has `date, value, baseflow` ✔ used in T7 and T11.
