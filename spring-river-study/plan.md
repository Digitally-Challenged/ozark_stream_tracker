# Spring River Hydrologic Regime Study — Research Spec for Claude Code

**Scope:** Spring River at Hardy, AR (USGS 07069305 / NWS HDYA4), 1981–2026, with recharge-basin precipitation and supporting gauges. **Deliverable:** Reproducible analysis pipeline + scientific report (HTML/PDF) with figures, tables, and stated uncertainty. **Working hypotheses:** Derived from the 2014–2026 screenshot review. Each is falsifiable below.

---

## 0. Research questions and hypotheses


| ID  | Question                                                     | Hypothesis from preliminary review                | Test                                                                                 |
| --- | ------------------------------------------------------------ | ------------------------------------------------- | ------------------------------------------------------------------------------------ |
| Q1  | Is base flow declining secularly, or tracking precipitation? | Drought-driven, not structural                    | Regress annual min flow on trailing recharge-season precip; trend-test the residuals |
| Q2  | Are floods getting bigger?                                   | Magnitude up (2008, 2025 tier), frequency flat    | B17C flood frequency with non-stationarity tests; POT counts by year                 |
| Q3  | Has rainfall intensity shifted (fewer, heavier events)?      | Weak/inconclusive                                 | Trend tests on ≥1"/≥2" day counts, max 1-day/3-day, top-5-day concentration          |
| Q4  | Do major floods reduce recharge (runoff vs infiltration)?    | Yes — post-flood floors are low                   | Compare post-flood base-flow recession vs precip-matched non-flood years             |
| Q5  | Is the stage floor decline a rating artifact?                | Partly                                            | Stage-at-fixed-discharge time series from IV data; USGS shift records                |
| Q6  | Is the ~4-year major-flood cadence real?                     | Modal, not periodic                               | Inter-arrival distribution vs Poisson; spectral check                                |
| Q7  | Post-major-flood quiet years (2018, 2026)?                   | Pattern, n=2                                      | Permutation test on next-year peak given prior-year major                            |
| Q8  | What are defensible return periods for 8/10/14/16/20/23 ft?  | 10 ft ≈ annual; 16 ft ≈ 4 yr; 22+ ft ≈ 1-in-15–25 | Bulletin 17C (EMA) with regional skew; report CIs                                    |


Answering Q1 and Q2 is the core. Q3–Q7 are supporting. Q8 is the practical output.

---

## 1. Data inventory

### 1.1 Streamflow / stage (USGS)


| Site                              | Role                | Notes                                                                                                                                                                     |
| --------------------------------- | ------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 07069305 Spring River at Hardy    | Primary             | Verify period of record for DV discharge, DV stage, IV, and annual peaks — the 1981 start may only hold for the NWS crest list, not USGS DV                               |
| 07069500 Spring River at Imboden  | Long-record proxy   | Record back to 1930s; use to extend flood-frequency series and cross-validate Hardy                                                                                       |
| Mammoth Spring / Warm Fork gauges | Base-flow partition | Search NWIS site service for active/inactive gauges on Spring River at Mammoth Spring and Warm Fork at Thayer; if a spring-discharge series exists it directly answers Q1 |


**Endpoints (verify which are live — USGS is migrating off legacy NWIS services):**

- New: [`https://api.waterdata.usgs.gov/ogcapi/v0/`](https://api.waterdata.usgs.gov/ogcapi/v0/) (daily values, monitoring locations)
- Legacy: [`https://waterservices.usgs.gov/nwis/dv/`](https://waterservices.usgs.gov/nwis/dv/), `/iv/`, `/peak/` (annual peaks), `/site/`
- Python: `dataretrieval` (USGS-maintained) — `nwis.get_dv`, `nwis.get_iv`, `nwis.get_discharge_peaks`, `nwis.get_info`
- Parameters: 00060 discharge (cfs), 00065 gage height (ft)
- Pull approval status flags (A = approved, P = provisional) and preserve them

If the separate repo already wraps this, treat it as the source of truth and confirm it exposes: DV discharge, DV stage, annual peaks, and IV for at least 2007+ (rating-drift analysis needs sub-daily pairs).

### 1.2 Precipitation


| Source                                                                              | Station / product                                                                    | Use                                                     |
| ----------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------ | ------------------------------------------------------- |
| RCC-ACIS ([`https://data.rcc-acis.org/StnData`](https://data.rcc-acis.org/StnData)) | West Plains ASOS (KUNO) + West Plains COOP; Mammoth Spring, AR COOP; Thayer, MO COOP | Daily precip, no API key required; primary point series |
| NCEI GHCN-Daily via CDO API v2                                                      | Same stations                                                                        | Cross-check; needs token                                |
| PRISM daily (4 km)                                                                  | Basin-averaged precip over the Mammoth Spring recharge area                          | Removes single-station noise; needed for Q1/Q4          |
| NWS SGF year-end summaries                                                          | 2013–2023 annual totals (already pulled)                                             | Validation only                                         |


**Recharge basin polygon:** Mammoth Spring's dye-traced recharge area lies in Howell/Oregon Counties, MO (West Plains region). Pull the delineation from Missouri Geological Survey / USGS dye-trace publications; if unavailable, use a 30 km buffer around West Plains as a stated approximation and run sensitivity on the radius.

### 1.3 Supporting

- NWS NWPS API: [`https://api.water.noaa.gov/nwps/v1/gauges/HDYA4`](https://api.water.noaa.gov/nwps/v1/gauges/HDYA4) — flood categories, historic crests, ratings
- US Drought Monitor county time series (Howell MO, Fulton AR, Sharp AR)
- USGS groundwater levels (NWIS `gwlevels`) — Ozark aquifer observation wells in Howell County, if any with 10+ yr record
- ENSO index (ONI) — covariate for interannual precip

---

## 2. Methods

### 2.1 Data QA (before any analysis)

- Gap map per series; flag gaps &gt; 7 days; never interpolate across floods
- Provisional vs approved split; sensitivity-check all conclusions on approved-only data
- Datum and rating-shift history from USGS site file; annotate on all stage plots
- Cross-check Hardy vs Imboden daily discharge: regression residuals identify Hardy record problems
- Precip station homogeneity: ASOS vs COOP overlap period; flag station moves

### 2.2 Base flow (Q1, Q4, Q5)

- Series: annual minimum 7-day mean discharge (7-day low flow) per water year; also Sep–Nov mean
- Base-flow separation: Eckhardt recursive filter (α = 0.98, BFImax fit) and Lyne-Hollick as a check; report base-flow index (BFI) per year
- Trend: Mann-Kendall + Sen's slope on 7-day low flow; Pettitt change-point test
- Attribution model: `min7 ~ P_recharge(Sep–Feb, t) + P(t−1) + ENSO` — OLS and a simple linear reservoir; residual trend test isolates non-climatic decline
- Rating drift: from IV data, stage at 400 cfs and at 1,000 cfs per water year; discontinuities at major floods confirm channel change
- Post-flood recharge (Q4): for each ≥16 ft event, compare 6-month-post base flow against precip-matched years without a major flood

### 2.3 Floods (Q2, Q6, Q7, Q8)

- Annual peak series from NWIS peak file (Hardy; Imboden for extension)
- Bulletin 17C: Expected Moments Algorithm, regional skew from USGS Arkansas/Missouri skew maps, low-outlier handling, 5–95% CIs. Implement in Python or call USGS PeakFQ; document which
- Non-stationarity: Mann-Kendall on peaks; Pettitt; compare B17C fits for 1981–2007 vs 2008–2026
- Partial duration series: declustered POT events (7-day independence) at 8/10/14/16 ft; counts per year; Poisson dispersion test
- Inter-arrival analysis for ≥16 ft events; test against exponential
- Q7: permutation test — is P(next-year peak &lt; 8 ft | major flood this year) higher than base rate?
- Antecedent conditions: BFI and 30-day precip before each ≥14 ft event

### 2.4 Precipitation regime (Q3)

- Annual totals, recharge-season (Sep–Feb) totals, growing-season (Mar–Aug) totals
- Intensity indices: days ≥0.5/1.0/2.0"; max 1-day and 3-day; fraction of annual total from top 5 days; simple daily intensity index (total / wet days)
- Trend tests on each; report effect sizes with CIs, not just p-values
- Cross-correlation: monthly basin precip vs monthly base flow, lags 0–12 months → aquifer response time

### 2.5 Seasonality and recession

- Peak timing: circular mean and concentration per decade
- Master recession curve; per-event recession constant k; trend in k (channel/aquifer change)

### 2.6 Statistical hygiene

- 45 years is short for return periods beyond ~50 yr; report CIs and say so
- Multiple comparisons across Q3 indices: Benjamini-Hochberg
- All trend claims paired with a plain-language effect size (e.g., "−4 cfs/decade, 95% CI …")

---

## 3. Repo layout

```
spring-river-study/
├── CLAUDE.md                 # project brief, conventions, data contract
├── pyproject.toml            # pinned deps
├── Makefile                  # make data | make analysis | make report
├── data/
│   ├── raw/                  # API pulls, never edited (gitignored, cached)
│   ├── interim/              # QA'd, gap-flagged
│   └── processed/            # analysis-ready parquet
├── src/spring_river/
│   ├── ingest/               # usgs.py, acis.py, prism.py, nwps.py, drought.py
│   ├── qa/                   # gaps.py, rating.py, crosscheck.py
│   ├── hydro/                # baseflow.py, recession.py, pot.py, freq_b17c.py
│   ├── climate/              # intensity.py, seasonal.py
│   ├── stats/                # trends.py (MK, Sen, Pettitt), permutation.py
│   └── viz/                  # consistent figure styling
├── notebooks/                # exploration only; nothing load-bearing
├── reports/
│   ├── report.qmd            # Quarto source
│   ├── figures/
│   └── tables/
└── tests/                    # unit tests for filters, B17C, POT declustering

```

**Stack:** Python 3.12, pandas, numpy, scipy, statsmodels, pymannkendall, dataretrieval, requests, matplotlib, Quarto for the report. Optional: `hydrofunctions`, `baseflow` package for Eckhardt.

---

## 4. Execution phases (Claude Code task order)


| Phase | Task                                                                                                                                                                                                                            | Exit criterion                                                             |
| ----- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------- |
| 0     | Data inventory: query NWIS site/peak/DV services for 07069305 and 07069500; list period of record per parameter; identify Mammoth Spring gauge; list ACIS stations within 40 km of West Plains with ≥90% completeness 1981–2026 | `data_[inventory.md](http://inventory.md)` with exact date ranges and gaps |
| 1     | Ingestion modules with caching and retry; raw pulls saved with request metadata                                                                                                                                                 | `make data` runs clean from empty cache                                    |
| 2     | QA: gap maps, provisional flags, Hardy–Imboden cross-check, precip homogeneity                                                                                                                                                  | `qa_[report.md](http://report.md)` with figures                            |
| 3     | Descriptive: annual ledger table (peak, ≥8/10/14/16 counts, 7-day low, BFI, annual + recharge-season precip)                                                                                                                    | `annual_ledger.parquet` + figure                                           |
| 4     | Base-flow attribution (Q1, Q4, Q5)                                                                                                                                                                                              | Residual trend result with CI                                              |
| 5     | Flood frequency (Q2, Q6, Q7, Q8)                                                                                                                                                                                                | B17C table with CIs; stationarity verdict                                  |
| 6     | Precip regime (Q3)                                                                                                                                                                                                              | Index trend table                                                          |
| 7     | Report assembly; limitations section; reproducibility check on a fresh clone                                                                                                                                                    | `report.html` builds from `make report`                                    |
| 8     | Adversarial review pass: prompt Claude Code to attack each conclusion, list what would falsify it                                                                                                                               | [`review.md`](http://review.md)                                            |


---

## 5. [CLAUDE.md](http://CLAUDE.md) draft

```markdown
# Spring River Study

## Purpose
Quantify the hydrologic regime of Spring River at Hardy, AR (USGS 07069305) 1981–2026:
base-flow trend and attribution, flood frequency and stationarity, precipitation
regime over the Mammoth Spring recharge basin. Output is a reproducible report.

## Conventions
- Water year (Oct–Sep) for all annual hydrologic stats; calendar year for precip totals
  unless stated. Recharge season = Sep–Feb.
- Units: cfs, feet (NGVD/NAVD as reported by USGS — record datum), inches.
- Every figure: source, period, approval status in caption.
- Every trend claim: test name, effect size, CI, n. No bare p-values.
- Provisional data: analysis runs twice (all / approved-only); flag any conclusion
  that changes.
- Never interpolate across gaps > 7 days. Never edit data/raw.

## Data contract
See docs/data_inventory.md. Ingest modules must be idempotent and cached.

## Analysis order
Phases 0–8 in docs/spec.md. Do not start Phase 4+ until QA report is reviewed.

## Style
Scientific, terse. Thesis → evidence → limitation. No hedging language in place
of numbers.

```

---

## 6. Known risks and open items

1. **Period of record.** If Hardy DV discharge starts after 1981, the long series comes from Imboden and Hardy is the 2000s+ series. Decide in Phase 0; do not assume.
2. **Legacy NWIS retirement.** Confirm endpoint status on day one; `dataretrieval` tracks the migration.
3. **Recharge basin polygon.** Literature pull required. If the dye-trace map isn't obtainable, state the buffer approximation in the report.
4. **Rating shifts.** USGS shift/measurement data may need a separate request; without it, Q5 relies on IV-derived stage-at-flow, which is adequate but weaker.
5. **Short record for extremes.** 22+ ft events: two in 18 years. Return-period CIs will be wide. Report them honestly; the practical number is the empirical rate.
6. **Station changes at West Plains.** ASOS (KUNO) and COOP may differ; choose one primary and document.

---

## 7. Report outline

1. Abstract (one paragraph, numbers-first)
2. Setting: gauge, spring, recharge basin, flood categories
3. Data and QA
4. Base-flow regime: trend, attribution, rating drift
5. Flood regime: frequency, stationarity, return periods, antecedent conditions
6. Precipitation regime: totals, seasonality, intensity
7. Coupling: precip → spring → river response times
8. Synthesis: what changed, what didn't, what's uncertain
9. Practical thresholds (paddling bands, flood exposure, monitoring alerts)
10. Limitations and next steps
11. Appendices: data tables, code references, B17C parameters

