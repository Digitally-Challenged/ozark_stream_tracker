# Spring River research notes

## Phase 0 pre-check — verified 2026-08-24 (live API queries)

### USGS NWIS period of record (site service, `seriesCatalogOutput=true`)

| Site | Series | Begin | End | Count |
|---|---|---|---|---|
| 07069305 Hardy | DV discharge (00060) | 2001-10-01 | 2026-08-23 | 9,083 |
| 07069305 Hardy | DV stage (00065) | — | — | none |
| 07069305 Hardy | IV discharge | 2001-10-01 | present | |
| 07069305 Hardy | IV stage | 2007-10-01 | present | |
| 07069305 Hardy | Annual peaks | 2002-03-20 | 2025-04-05 | 24 |
| 07069500 Imboden | DV discharge | 1936-04-01 | 2026-08-23 | 30,261 |
| 07069500 Imboden | IV discharge | 1992-10-01 | present | |
| 07069500 Imboden | IV stage | 2007-10-01 | present | |
| 07069500 Imboden | Annual peaks | 1915-08 | 2025-04-05 | 90 |

**Spec risk #1 resolved:** the 1981 start does NOT hold for USGS data. Hardy is a
WY 2002+ discharge series with sub-daily stage from WY 2008. Imboden is the long
record for flood frequency (90 annual peaks, 1915–2025). There is no USGS daily
stage product at Hardy — daily stage statistics must be derived from IV.

### NWS NWPS HDYA4 (`api.water.noaa.gov/nwps/v1/gauges/HDYA4`)

- Flood categories (ft): action 8, minor 10, moderate 14, major 16 — matches spec.
- Historic crest list: 21 entries (one duplicate). Only entry before 2002 is the
  **record crest 29.0 ft on 1982-12-03** (flow not reported). Top crests:

| Date | Stage (ft) | Flow (cfs) |
|---|---|---|
| 1982-12-03 | 29.00 | n/a |
| 2025-04-05 | 22.82 | n/a |
| 2008-03-19 | 22.29 | 80,700 |
| 2008-04-11 | 20.81 | 70,081 |
| 2011-04-26 | 20.71 | 69,624 |
| 2009-10-30 | 17.41 | 48,273 |
| 2006-09-23 | 16.75 | n/a |
| 2017-04-30 | 16.65 | n/a |

**Implication for Q8 / spec risk #5:** the "22+ ft events: two in 18 years"
framing omits the 1982 29-ft crest. Any return-period statement for 22+ ft must
account for it (as a historical peak in B17C terms), and the 1981–2001 gap in
Hardy data means the 1982 crest is a censored-record observation, not part of a
systematic series. Imboden's 1915+ peaks are the defensible long series.

### Open items carried into the plan

- ACIS station sids for West Plains (KUNO vs COOP) — confirmed at Task 4/7 runtime.
- Mammoth Spring / Warm Fork gauge search — Task 7.
- Recharge-basin polygon: 30 km West Plains buffer approximation until a dye-trace
  delineation is obtained.

## Phase 4–6 decisions — 2026-08-25

- Q1 primary series: Mammoth Spring vent DV (07069190, 1981→, no gaps). Hardy min7 secondary (WY 2002+, n=24).
- Trend stack: in-repo Mann-Kendall / Sen (Gilbert CI) / Pettitt (`stats/trends.py`); OLS via statsmodels HC3.
- BFI trends use gap-segmented Eckhardt with 30-day spin-up; Lyne-Hollick as check.
- Flood frequency: LP3/MOM + B17B weighted skew (`REGIONAL_SKEW=-0.2`, approximate) + Grubbs-Beck + bootstrap CI. NOT EMA. 1982 crest reported as historical exceedance only. PeakFQ follow-up open.
- Imboden NWIS peak file actually starts WY 1937 (n=89), not 1915 as the site catalog implied.
- Stage↔flow at Hardy from annual-peak pairs (log-log, R²=0.99). USGS rating shifts still unobtained → Q5/Q8 provisional.
- Precip station agreement re-tested monthly (r=0.86), resolving the qa_report daily-r=0.42 item as an observation-time artifact.
- Lag-correlation bootstrap resamples 12-month blocks of already-lagged pairs (fixed 2026-08-25 after review).
- Codex adversarial review (NEEDS-CHANGES, 9 blocking) folded in the same day — see `docs/review_phase4-6.md`. Material effects: Q1 predictors made strictly antecedent (Hardy residual trend lost significance); LP3 keeps low outliers by default (Imboden 100-yr 161k → 145k cfs); basin recharge-season precip trend flipped sign to ~0 once the coverage gate was corrected.

### Headline results vs. working hypotheses

| Q | Hypothesis | Result |
|---|---|---|
| Q1 | Drought-driven, not structural | Supported (post-review, antecedent predictors). Mammoth residual trend −0.0022 log-cfs/yr (CI −0.0050 to +0.0005, n=42); Hardy residual +0.0068 (CI −0.0014 to 0.0195, n=24). Hardy raw min7 *rises* (+0.023/yr, CI 0.007–0.036) but trailing-365-day precip (ending before the min7 window starts) explains it (R²=0.47). |
| Q2 | Magnitude up, frequency flat | Not detectable. Imboden peaks +0.0011 log10-cfs/yr (CI −0.0012 to 0.0041, n=89); pre/post-2008 10-yr quantile CIs overlap. |
| Q3 | Weak/inconclusive | Basin (PRISM): 9/10 indices up (total +2.4 in/decade, CI 0.4–4.5, n=45); recharge-season total flat (−0.02, CI −1.3 to 1.2, n=44). Station tests low-power (COOP coverage gaps). |
| Q4 | Floods reduce recharge | **Not supported — opposite sign.** 6-month post-flood base flow +28% (Mammoth, CI 20–42, 15 unique controls) and +23% (Hardy, CI 13–35, 11 controls), n=6; matched on precip + antecedent base flow, 30-day recession skip. Descriptive, not causal. |
| Q5 | Partly a rating artifact | Supported. Stage at 1000 cfs −0.019 ft/yr (CI −0.021 to −0.016, n=19; local log-linear fit), 400 cfs −0.008 (CI −0.013 to −0.005); ±1-yr event shifts −0.18 to +0.02 ft — gradual drift dominates. |
| Q6 | Modal, not periodic | Consistent with memoryless: CV 1.01, bootstrap p=0.47, n=7. |
| Q7 | Pattern, n=2 | No support; P(quiet\|major)=0 vs base 0.08 (Clopper-Pearson diff −0.08 to +0.44), n_major=5. |
| Q8 | 10 ft≈annual; 16≈4 yr; 22+≈15–25 | 10 ft 1.4 yr; 16 ft 4.5 (empirical 4.0); 20 ft 12.5; 23 ft ~29 yr (n=24 → wide). |
