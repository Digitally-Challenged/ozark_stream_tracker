# Spring River Phase 7 (Seasonality/recession + Report assembly) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development or superpowers:executing-plans. Steps use `- [ ]` checkboxes.

**Goal:** Close spec §2.5 (peak timing, recession) and deliver `reports/report.html` from `make report` per spec §4 Phase 7 and the §7 outline, with a consolidated limitations section and a fresh-clone reproducibility check.

**Architecture:** Two pure modules (`climate/seasonal.py`, `hydro/recession.py`) + a runner (`analysis/phase7.py`) writing `docs/phase7_seasonality.md` and tables/figures, mirroring Phases 4–6. `reports/report.qmd` is a Quarto document (jupyter engine, project venv) whose numbers come from `reports/tables/*.parquet` via small Python cells, and whose figures are the committed PNGs. Prose is synthesis only; per-phase detail stays in `docs/phase*.md` (linked).

**Tech Stack:** Python 3.12, pandas/numpy/scipy, matplotlib, Quarto (brew cask), `jupyter` + `ipykernel` as dev deps.

**Spec:** `spring-river-study/plan.md` §2.5, §2.6, §4 Phase 7, §7; results in `docs/phase4_baseflow.md`, `phase5_floods.md`, `phase6_precip.md`, `review_phase4-6.md`.

## Global Constraints

- Same project rules as the Phase 4–6 plan (water year, no interpolation across >7-day gaps, captions with source/period/approval, trend claims with effect size + CI + n, all/approved-only sensitivity, `uv run pytest -q` green, one commit per task).
- Branch: `study/phase7-report`.
- `make report` must build from a fresh clone given `data/raw` (documented: raw cache is git-ignored; `make data` repopulates from the network).

## File map

| Path | Responsibility |
|---|---|
| `src/spring_river/climate/seasonal.py` | `circular_stats`, `peak_timing_by_period` |
| `src/spring_river/hydro/recession.py` | `recession_segments`, `fit_k`, `event_k_table`, `master_recession` |
| `src/spring_river/analysis/phase7.py` | runner → `docs/phase7_seasonality.md`, `phase7_*.parquet/png` |
| `reports/report.qmd` | Quarto report (§7 outline) |
| `reports/_quarto.yml` | render config (html, toc, self-contained) |
| `Makefile` | `phase7`, `report`, `analysis` includes phase7 |
| `pyproject.toml` | dev deps `jupyter`, `ipykernel` |
| `tests/test_seasonal.py`, `tests/test_recession.py` | unit tests |

---

### Task 1: Peak-timing circular statistics (`climate/seasonal.py`)

**Interfaces:**
- `circular_stats(dates: pd.Series) -> dict` → `{"n", "mean_doy" (1–366), "mean_date_label" ("dd Mon"), "R" (mean resultant length 0–1), "rayleigh_p"}`; angle = 2π·(doy−1)/365.25; Rayleigh p ≈ exp(−n·R²)·(1 + (2z − z²)/(4n) − …) — use the simple `exp(-z)` with `z = n R²` corrected as `p = exp(sqrt(1+4n+4(n²−R_n²)) − (1+2n))` where `R_n = nR` (Zar 1999); `n < 3` → NaN.
- `peak_timing_by_period(dates: pd.Series, period_years: int = 10, start_year: int | None = None) -> pd.DataFrame` — one row per period (`period` label like "2008–2017"), plus a final "all" row; columns `period, n, mean_doy, mean_date_label, R, rayleigh_p`.

**Tests** (`tests/test_seasonal.py`): (a) all dates on Apr 15 → R≈1, mean_doy≈105; (b) uniform monthly dates → R small, rayleigh_p > 0.05; (c) dates straddling Dec/Jan (Dec 20, Jan 10) → mean near Jan 1 (doy ~365/1), not July; (d) `peak_timing_by_period` returns expected period labels and an "all" row.

### Task 2: Recession analysis (`hydro/recession.py`)

**Interfaces:**
- `recession_segments(dv_q: pd.DataFrame, min_peak_cfs: float, min_days: int = 10, max_rise_frac: float = 0.02) -> list[pd.DataFrame]` — after each local peak ≥ `min_peak_cfs` in a gap-free segment (`segment_gapfree`), take the run of days while `q[t] <= q[t-1]·(1+max_rise_frac)` and `q[t] > 0`; keep runs ≥ `min_days`; each frame has `date, value, t_days` (0 at peak).
- `fit_k(seg: pd.DataFrame, skip_days: int = 3) -> tuple[float, float]` → `(k_days, r2)` from OLS `ln q = a − t/k` on days ≥ `skip_days` (skips the quickflow crest).
- `event_k_table(dv_q, min_peak_cfs, **kw) -> pd.DataFrame` — `peak_date, peak_cfs, n_days, k_days, r2, wy`.
- `master_recession(segments, n_points: int = 60) -> pd.DataFrame` — matching-strip approximation: normalise each segment by its day-`skip` flow, then median of ln(q/q0) at each `t`; columns `t_days, ln_ratio_median, ln_ratio_q25, ln_ratio_q75, n`.

**Tests** (`tests/test_recession.py`): synthetic exponential recession q = 5000·exp(−t/20) after a peak recovers k≈20 (±0.5) with r2>0.99; a 20-day gap splits segments; a rise > 2% ends the segment; `event_k_table` has one row per qualifying peak.

### Task 3: Phase 7 runner

`analysis/phase7.py` → `docs/phase7_seasonality.md`:
- Peak timing: (i) Hardy POT ≥10 ft event peak dates (WY 2008+, daily-max IV stage) by decade; (ii) Hardy annual-peak dates (2002+); (iii) Imboden annual-peak dates (1937+) by decade — this is the long series. Table + a polar/rose figure (`phase7_peak_timing.png`) with month labels.
- Recession: Hardy DV, `min_peak_cfs = 10000` (≈ 8 ft), per-event k table; `trend_test(k, wy)` with CI/n; Pettitt; master recession figure (`phase7_master_recession.png`); same for Mammoth Spring (`min_peak_cfs` = 90th percentile of Mammoth DV) as the aquifer-side check.
- All/approved-only sensitivity for the k trend (CHANGED rule via `sensitivity_lines`).
- Tables: `phase7_peak_timing.parquet`, `phase7_recession_k_{hardy,mammoth}.parquet`, `phase7_master_recession_{hardy,mammoth}.parquet`.
- Makefile: `phase7` target; `analysis: ledger phase4 phase5 phase6 phase7`.

### Task 4: Quarto report

- `pyproject.toml` dev deps: `jupyter>=1.0`, `ipykernel>=6`; `uv sync`.
- `reports/_quarto.yml`: `project: {type: default}`, `format: html: {toc: true, embed-resources: true, number-sections: true}`, `execute: {echo: false, warning: false}`, `jupyter: python3`.
- `reports/report.qmd` sections per spec §7: 1 Abstract (numbers-first, values read from tables in a setup cell and inserted with inline `{python}` expressions); 2 Setting (gauge, spring, recharge basin approximation, NWS categories); 3 Data and QA (link `docs/qa_report.md`; approval fractions; gap summary); 4 Base-flow regime (phase 4 figures + numbers); 5 Flood regime (phase 5); 6 Precipitation regime (phase 6); 7 Coupling (lag correlation); 8 Synthesis (what changed / didn't / uncertain — the hypothesis table from `spring_river_research.md`, generated from tables); 9 Practical thresholds (stage return-period table; paddling/flood/alert bands stated as ranges); 10 Limitations (consolidated from all phase reports + review overrules); 11 Appendices (data tables, code refs, LP3 parameters, review record link).
- Every figure gets a caption with source/period/approval (copy from the phase report captions).
- Makefile: `report: analysis` → `cd reports && QUARTO_PYTHON=../.venv/bin/python quarto render report.qmd`.

### Task 5: Reproducibility check + docs

- Fresh clone into the scratchpad, `uv sync`, copy `data/raw` from this worktree (documented), `make analysis report` → `reports/report.html` builds; diff the three phase docs vs committed (only date lines differ).
- Update `CLAUDE.md` (Phase 7 done; Phase 8 next), `spring_river_research.md` (Phase 7 decisions), memory.
- Commit; merge `study/phase7-report` → main with merge commit; push.
