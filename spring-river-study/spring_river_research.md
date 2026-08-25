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
| Q1 | Drought-driven, not structural | **(2nd ed.)** Supported at Mammoth, source-dependent at Hardy. Mammoth residual trend −0.0013 log-cfs/yr (CI −0.0033 to +0.0012, n=42) — CI spans zero on all three basin series. Hardy residual +0.0203 (CI +0.0092 to +0.0291, n=24) on AORC, but the CI spans zero on both PRISM series (prism_polygon +0.0103, CI −0.0006 to 0.0191; prism_buffer +0.0068, CI −0.0014 to 0.0195). Hardy raw min7 rises (+0.023/yr, CI 0.007–0.036); antecedent precip explains part of it (R²=0.41 on AORC). |
| Q2 | Magnitude up, frequency flat | Not detectable. Imboden peaks +0.0011 log10-cfs/yr (CI −0.0012 to 0.0041, n=89); pre/post-2008 10-yr quantile CIs overlap. |
| Q3 | Weak/inconclusive | **(2nd ed.)** More intense but not detectably wetter. Basin (AORC, MoDNR polygon): 6/10 indices BH-significant — max 1-day +0.26 in/decade (CI 0.05–0.50), SDII +0.032 in/wet-day/decade (CI 0.020–0.046), days ≥ 1 in +1.38/decade (CI 0.49–2.22) — but annual total is **not** significant (+0.96 in/decade, CI −1.25 to 3.12, n=45); the first edition's significant +2.4 was a property of the oversized 30 km buffer. Recharge-season total flat-to-negative (−0.81, CI −1.99 to 0.60, n=44). Single-station tests low-power (COOP coverage gaps), but the 76-year West Plains 1948– record (COOP to Mar 1998, then KUNO raised by the measured 1.068 catch ratio) is not: only days ≥ 1 in is BH-significant (+0.70/decade, CI 0.26 to 1.15, n=76), with max 1-day and SDII CIs spanning zero — the gauge shows more wet days, not harder rain, and does not corroborate the basin intensification over 1949–2025. |
| Q4 | Floods reduce recharge | **(2nd ed.) Not supported — opposite sign.** 6-month post-flood base flow +26% (Mammoth, CI 16–41, 16 unique controls) and +31% (Hardy, CI 20–39, 10 controls), n=6; matched on precip + antecedent base flow, 30-day recession skip. Stable across all three basin sources. Descriptive, not causal. |
| Q5 | Partly a rating artifact | Supported. Stage at 1000 cfs −0.019 ft/yr (CI −0.021 to −0.016, n=19; local log-linear fit), 400 cfs −0.008 (CI −0.013 to −0.005); ±1-yr event shifts −0.18 to +0.02 ft — gradual drift dominates. |
| Q6 | Modal, not periodic | Consistent with memoryless: CV 1.01, bootstrap p=0.47, n=7. |
| Q7 | Pattern, n=2 | No support; P(quiet\|major)=0 vs base 0.08 (Clopper-Pearson diff −0.08 to +0.44), n_major=5. |
| Q8 | 10 ft≈annual; 16≈4 yr; 22+≈15–25 | 10 ft 1.4 yr; 16 ft 4.5 (empirical 4.0); 20 ft 12.5; 23 ft ~29 yr (n=24 → wide). |

## Phase 7 decisions — 2026-08-25

- §2.5 closed: `climate/seasonal.py` (circular mean, resultant length R, Rayleigh p — Zar 1999) and `hydro/recession.py` (local-peak recession runs, ln-linear k, matching-strip master curve). Runner `analysis/phase7.py` → `docs/phase7_seasonality.md`.
- Peak timing: Hardy POT ≥10 ft (n=17) mean 3 Mar, R=0.53, p=0.006; Hardy annual peaks (n=24) 3 Mar, R=0.43, p=0.012; Imboden annual peaks (n=89) 24 Feb, R=0.49, p<0.0001. Decadal R varies 0.31–0.94 with no drift.
- Recession: Hardy (peaks ≥10,000 cfs) median k 13.9 d, trend +0.06 d/yr (CI −0.22 to 0.40, n=16); Mammoth (peaks ≥488 cfs) median k 188 d, trend +0.22 d/yr (CI −1.03 to 1.70, n=80). No change in channel/aquifer drainage rate detectable.
- Report: Quarto 1.10.18 installed from the release tarball into `~/.local/opt` (cask needs sudo); `make report` sets `QUARTO_PYTHON` to the project venv (jupyter/ipykernel dev deps). Numbers in `reports/report.qmd` are read from `reports/tables/*.parquet` in code cells, not typed.

## Second edition — basin precipitation on the MoDNR polygon and AORC — 2026-08-25

Decisions: basin = MoDNR Mammoth Spring recharge polygon (`docs/gis/`, 361 mi² stated / ~349 mi²
equal-area, SE of West Plains toward Alton and Thayer); primary basin series = NOAA AORC v1.1
(1 km hourly, daily totals 24 h ending 12 UTC); PRISM recut to the same polygon as second opinion;
the 30 km West Plains buffer retained only for comparison; Alton COOP USC00230127 added to Phase 6.
`config.BASIN_PRECIP_SOURCE` selects the series (env-overridable, default `aorc`); `make compare`
writes `docs/precip_comparison.md`.

AORC pull: 45 years in 256 s. The AORC bucket ends at `2025.zarr`, so the daily series runs
1981-01-02 → 2025-12-31 (the 1981-01-01 and 2026-01-01 labels are NaN half-windows; 2024-06-18 and
2024-06-19 are NaN because 2024-06-18 is a wholly missing day — never filled). PRISM runs to within
a day of today.

Mean annual 1981–2025: aorc 47.5 in, prism_polygon 47.8 in, prism_buffer 47.7 in. Agreement aorc vs
prism_polygon: daily r 0.955, annual-total r 0.966, ratio PRISM/AORC 1.01 (n = 45 years).

### What changed (first edition → second edition, all-data variant)

| block      | metric                          | first edition (prism_buffer)         | aorc                                 | prism_polygon                        | prism_buffer                          |
|:-----------|:--------------------------------|:-------------------------------------|:-------------------------------------|:-------------------------------------|:--------------------------------------|
| q1_mammoth | p_trailing_in coef (log-cfs/in) |                                      | 0.0156 (0.0111 to 0.0201; n=42)      | 0.0139 (0.00912 to 0.0186; n=42)     | 0.013 (0.00893 to 0.0171; n=42)       |
| q1_mammoth | OLS R²                          |                                      | 0.577 (n=42)                         | 0.519 (n=42)                         | 0.446 (n=42)                          |
| q1_mammoth | residual trend (log-cfs/yr)     | −0.0022 (−0.0050 to +0.0005; n=42)   | -0.00126 (-0.00326 to 0.00122; n=42) | -0.00225 (-0.0048 to 0.000148; n=42) | -0.00222 (-0.00497 to 0.000453; n=42) |
| q4_mammoth | post-flood base-flow diff (%)   | 28 (20 to 42; n=6)                   | 26 (15.7 to 41; n=6)                 | 24.7 (16.5 to 35.4; n=6)             | 27.5 (19.8 to 42; n=6)                |
| q1_hardy   | p_trailing_in coef (log-cfs/in) |                                      | 0.0231 (0.00876 to 0.0375; n=24)     | 0.0246 (0.00567 to 0.0435; n=24)     | 0.023 (0.00967 to 0.0363; n=24)       |
| q1_hardy   | OLS R²                          |                                      | 0.408 (n=24)                         | 0.553 (n=24)                         | 0.47 (n=24)                           |
| q1_hardy   | residual trend (log-cfs/yr)     | +0.0068 (−0.0014 to 0.0195; n=24)    | 0.0203 (0.00915 to 0.0291; n=24)     | 0.0103 (-0.00061 to 0.0191; n=24)    | 0.00676 (-0.00135 to 0.0195; n=24)    |
| q4_hardy   | post-flood base-flow diff (%)   | 23 (13 to 35; n=6)                   | 30.7 (19.6 to 38.7; n=6)             | 32.9 (24 to 41.5; n=6)               | 22.9 (12.6 to 35.1; n=6)              |
| q3         | total_in slope/decade           | +2.4 (0.4 to 4.5; n=45)              | 0.96 (-1.25 to 3.12; n=45)           | 2.01 (-0.0612 to 4.2; n=45)          | 2.41 (0.355 to 4.46; n=45)            |
| q3         | total_in BH-significant         | yes                                  | no                                   | no                                   | yes                                   |
| q3         | recharge_in slope/decade        | −0.02 (−1.3 to 1.2; n=44)            | -0.806 (-1.99 to 0.602; n=44)        | -0.282 (-1.51 to 1.04; n=44)         | -0.0177 (-1.27 to 1.19; n=44)         |
| q3         | recharge_in BH-significant      | no                                   | no                                   | no                                   | no                                    |
| q3         | max1_in slope/decade            |                                      | 0.264 (0.0517 to 0.495; n=45)        | 0.28 (0.082 to 0.481; n=45)          | 0.28 (0.0967 to 0.528; n=45)          |
| q3         | max1_in BH-significant          |                                      | yes                                  | yes                                  | yes                                   |
| q3         | sdii_in slope/decade            |                                      | 0.0324 (0.0204 to 0.0461; n=45)      | 0.0217 (0.00838 to 0.0358; n=45)     | 0.0347 (0.0222 to 0.0486; n=45)       |
| q3         | sdii_in BH-significant          |                                      | yes                                  | yes                                  | yes                                   |
| coupling   | response lag (months)           |                                      | 1 (n=539)                            | 1 (n=545)                            | 1 (n=545)                             |
| coupling   | r at response lag               |                                      | 0.454 (0.412 to 0.519; n=539)        | 0.476 (0.437 to 0.54; n=545)         | 0.463 (0.422 to 0.526; n=545)         |

Interpretation: the precipitation coefficient tightened at Mammoth exactly as `docs/precip_sources.md`
predicted — the p_trailing coefficient rose from 0.013 to 0.0156 log-cfs/in and OLS R² from 0.446 to
0.577. The table splits that gain between the two changes. Geometry alone (the same PRISM product moved
from the 30 km buffer onto the traced recharge polygon) accounts for the smaller half: 0.013 → 0.0139
log-cfs/in and R² 0.446 → 0.519. The product change (PRISM → AORC on that same polygon) supplies the
rest: 0.0139 → 0.0156 and R² 0.519 → 0.577. So the traced basin and the 1 km hourly analysis each
contribute, with the finer grid contributing slightly more of the R² gain than the geometry does. Coupling did not move (lag 1 month, r 0.45 on every source). Two conclusions did
change. **Q3: the annual-total trend lost BH significance on both polygon series** (aorc +0.96 in/decade,
CI −1.25 to 3.12; prism_polygon +2.01, CI −0.06 to 4.20) — the first edition's significant +2.4 in/decade
was a property of the buffer, so the thesis becomes "more intense but not detectably wetter"; the
intensity indices (max 1-day, SDII, days ≥ 1 in) stay significant on all three sources. **Q1 Hardy: the
residual trend is +0.0203 log-cfs/yr (CI 0.0092 to 0.0291, n=24) on AORC**, where both PRISM series give
CIs spanning zero — on the primary series Hardy's rising min7 is *not* fully explained by antecedent
precipitation. That is source-dependent (two of three sources say zero) at n=24 and R²=0.41, and is
reported as such rather than as a finding. No all/approved-only `**CHANGED**` flag appeared in either
phase document.

### West Plains 1948– record (Task 10, revised Task 11)

The West Plains COOP gauge (`USC00238880`, volunteer-read, 1948-07-01→, −91.874/36.727, 1105 ft)
has ~675 missing days scattered through 2011–2021, so twelve calendar years fail the 90 % coverage
gate and the recent wet decade drops out of its trend test. The West Plains Municipal Airport ASOS
(`KUNO`, 1998-04-01→, −91.905/36.879, 1226 ft — 10.7 mi north of and 120 ft above the town gauge)
is essentially complete. Monthly totals at the two gauges agree at r = 0.86, and over the 282
months with ≥ 25 days at both the **COOP/KUNO catch ratio is 1.068** — the ASOS undercatches
slightly, as ASOS gauges generally do.

`climate/westplains.py` runs the two instruments one at a time: COOP as measured through
1998-03-31, then KUNO × 1.068 for every day KUNO reported (10,331 days), which raises the airport
values onto the town gauge's level so the 1998 handover is not a step. **No day is borrowed between
gauges**: the 43 days KUNO missed after 1998-04-01 stay NaN rather than falling back to COOP, and
nothing is interpolated — each year is still judged on the same 90 % coverage gate. The 1948 COOP
pull uses its own cache (`acis_pcpn_USC00238880_1948`, via the `cache_suffix` argument), so the
1981+ COOP series the ledger and other phases read is untouched.

Result: **76 index years pass the coverage gate (1949–2025)**, against 34 for COOP alone, 27 for
KUNO and 24 for Alton — the longest and highest-power station test in the study. Its ten index
trends (Sen slope per decade, 95 % CI, BH across 10 indices):

| index | slope/decade | 95 % CI | n | BH-significant |
|:------|-------------:|:--------|--:|:---------------|
| total_in | +1.26 in | 0.282 to 2.34 | 76 | no (p_BH 0.067) |
| recharge_in | +0.566 in | −0.062 to 1.08 | 74 | no |
| growing_in | +0.619 in | −0.051 to 1.31 | 76 | no |
| days_ge_0p5 | +0.818 | −0.000 to 1.53 | 76 | no |
| days_ge_1 | +0.703 | 0.256 to 1.15 | 76 | **yes** (p_BH 0.017) |
| days_ge_2 | −0.000 | −0.000 to 0.323 | 76 | no |
| max1_in | +0.033 in | −0.085 to 0.149 | 76 | no |
| max3_in | +0.065 in | −0.105 to 0.235 | 76 | no |
| top5_frac | −0.003 | −0.007 to 0.001 | 76 | no |
| sdii_in | +0.003 in/wet-day | −0.005 to 0.010 | 76 | no |

Interpretation, from the numbers: over the 76 complete years (1949–2025) the gauge shows **more wet
days, not harder rain**.
The one BH-significant index is the count of days ≥ 1 in; max 1-day and SDII — the two indices
carrying the basin series' intensification signal over 1981–2025 — have CIs spanning zero at the
gauge. The annual total's Sen CI excludes zero (+1.26, 0.282 to 2.34) but does not survive BH
correction across the ten indices. So the record corrects the "station tests are low-power" caveat
rather than confirming the basin thesis: with the power problem removed, the gauge does not
corroborate intensification over the longer window. That is a genuine point-vs-areal and
1948-vs-1981 difference, not a coverage artifact, and the prose now says so.
