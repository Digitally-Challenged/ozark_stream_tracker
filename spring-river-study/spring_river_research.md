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
| Q1 | Drought-driven, not structural | **(Phase 8)** Supported at Mammoth; **at Hardy the rise is a finding, not a source artefact**. Mammoth residual trend −0.0013 log-cfs/yr (CI −0.0033 to +0.0012, n=42) — but the PRISM fits are consistently, marginally negative and one specification (prism_polygon, 730-d window) has a CI excluding zero, so "≈0 on all three sources" overstates the agreement. Hardy residual +0.0203 (CI +0.0092 to +0.0291, n=24). The hedge is retired on two grounds that use no precipitation model: log(Hardy min7 / Mammoth min7) rises **+0.0124/yr (CI +0.0028 to +0.0219, p=0.0023, n=24)**, Pettitt after WY2014 (p=0.029); and dropping the never-significant ONI term makes the residual rise significant on **all three** sources (AORC +0.0213, PRISM-polygon +0.0116 p=0.021, buffer +0.0110 p=0.016). |
| Q2 | Magnitude up, frequency flat | **(Phase 8)** Not detectable — on a test that could have found it. Imboden peaks +0.0011 log10-cfs/yr (CI −0.0012 to 0.0041, n=89); pre/post-2008 10-yr quantile CIs overlap. The old conjunction rule only saw the centre of the distribution, so the upper tail was tested directly: q=0.90 quantile regression +0.0026 (CI −0.0017 to +0.0070) and top-quartile Sen +0.0008 (CI −0.0009 to +0.0039) — both span zero. A WY2008 mean shift (Welch p=0.028, Mann–Whitney p=0.050) is disclosed as **post hoc**: the split year was chosen after seeing the data (a 1980 split gives p=0.77). |
| Q3 | Weak/inconclusive | **(Phase 8 — REFRAMED)** **Not wetter, and no intensification detectable once the 2002 AORC radar onset is allowed for.** Annual total not significant (+0.96 in/decade, CI −1.25 to 3.12, n=45) and recharge-season total flat-to-negative (−0.81, CI −1.99 to 0.60, n=44) — the robust result, unaffected by the step term. The sharpness indices **step rather than trend**: with a 2002 step term SDII's slope is −0.002/decade (p=0.86) while its step is significant (p=0.001); days ≥1 in slope −0.93 (p=0.20), step p=0.0003. Within-era Sen slopes are flat-to-negative on every sharpness index (0 of 6 era combinations rising). Over identical years AORC SDII +36 % vs the West Plains gauge +1 %, and days ≥1 in +56 % vs +18 %, while the two products agree on annual total (+9 % vs +11 %) — a product change, not a weather change. Family-wise max-T (joint permutation, 5,000 draws) leaves 2/10 vs 6/10 under BH; the count is no longer used as a summary. The gauge fails to corroborate over its own 1949–2025 record and over AORC's identical window, and its one BH-significant index (days ≥1 in) survives at the measured catch ratio 1.068 but not at 1.00 or 1.034. PRISM shares AORC's inputs and is not an independent witness. |
| Q4 | Floods reduce recharge | **(Phase 8)** **Not supported — opposite sign at Mammoth; Hardy materially weakened.** Mammoth +26 % (CI 16–41) against a placebo mean of **+0.6 %** — 0 of 200 placebo trials reach it — and stable from a 15- to a 90-day skip: stands, and stronger than the CI alone suggests. Hardy +31 % (CI 20–39) against a placebo mean of **+9.7 %** that **11 %** of trials reach, falling to **+8.0 % (CI −8.1 to +22.8)** at a 90-day skip; placebo-corrected ≈ +21 %. About a third of Hardy's figure is procedural and part of the rest is recession water. n=6 events. Descriptive, not causal. |
| Q5 | Partly a rating artifact | **(Phase 8) Not an artifact — the channel really degraded, and the effect is understated.** Stage at 1000 cfs −0.019 ft/yr (CI −0.021 to −0.016, n=19), 400 cfs −0.008 (CI −0.013 to −0.005); event shifts −0.18 to +0.02 ft. The circularity objection (IV discharge is itself rating-derived) is answered by **field measurements**, where discharge and stage are both measured at the visit: stage at 400 cfs falls **−0.0149 ft/yr (CI −0.0219 to −0.0105, p<0.0001, n=20 WY 2003–2026)** — steeper, four years longer, and it brackets the 2006-09-23 event the shift table omits. Datum history reviewed: two revisions (340.91→342.49 ft pre-Dec 2022; 342.49→342.73 ft Dec 2022–Dec 2024), **no site move, nothing at WY2008**. The "~1 % agreement in every era" is corrected: era means are a few per cent either side of zero with sd several times larger, and are not independent evidence anyway (USGS shifts the rating to these measurements). |
| Q6 | Modal, not periodic | **(Phase 8)** **No cadence detectable — and none weaker than near-metronomic could have been.** CV 1.01, bootstrap p=0.47, n=7. At 6 gaps an exponential null routinely gives CV 0.42–1.50, and power is 0.23 at CV 0.7, 0.58 at CV 0.5, reaching 80 % only at CV≈0.35. Absence of evidence, not evidence of absence. |
| Q7 | Pattern, n=2 | **(Phase 8 — RECLASSIFIED) UNTESTABLE with the current record.** P(quiet\|major)=0 vs base 0.08 (Clopper-Pearson diff −0.08 to +0.44), n_major=5. Fisher power is 0.08 against a 2.5× effect and reaches 80 % only at a true conditional rate ≈0.8; the exact bound admits any rate in 0.00–0.52. The design produced **no result**, which is not a null result. |
| Q8 | 10 ft≈annual; 16≈4 yr; 22+≈15–25 | **(Phase 8)** 10 ft 1.4 yr; 16 ft 4.5 (empirical 4.0). At the major tier the systematic-only fit is **biased long ~20–30 %** because it excludes the known 1982 crest (29.0 ft, ≈156,000 cfs). With it as historical information (B17B weighting): H=44 yr → 20 ft 9.9, 23 ft 20.1; H=90 yr → 11.3 / 24.5. **Quote 20 ft as 10–13 yr and 23 ft as 20–29 yr**, not 12.5 and 29. Still inside the 5–95 % bootstrap band, so not refuted. The station-skew case moves 23 ft by <1 yr and is not the sensitivity that matters. |

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
was a property of the buffer, so the thesis becomes **[superseded by Phase 8: the buffer-vs-polygon trend difference is +0.27 in/decade with a CI spanning zero, and the intensity indices are a 2002 product step — see review.md]** — "more intense but not detectably wetter"; the
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

## Phase 8 — adversarial review of the conclusions — 2026-08-25

Four independent reviewers (three domain attackers — base flow and gauge, floods, precipitation — plus a
generalist) were given every conclusion with its numbers and told to refute it, to state what would falsify
it, and to run their own checks. Verdicts and the punch list: `review.md`; reports: `docs/review_phase8/`.
Of 24 claims: 11 stand, 9 weakened, 3 refuted, 1 untestable. Everything below is computed by the phase
runners, not transcribed.

**Conclusions that changed.**

- **Q3 reframed (refuted as stated).** "More intense, not detectably wetter" → *totals are not rising, and no
  intensification is detectable over the recharge area once the 2002 AORC radar onset is allowed for*. The
  sharpness indices step at the documented change in the product's inputs and trend flat-to-negative within
  each era; the co-located gauge does not move with them over identical years while the annual totals agree.
  The "6/10 BH-significant" count is removed from the abstract and synthesis (max-T leaves 2/10).
- **Q7 reclassified** from "no support" to **untestable with the current record**: the design produced no
  result, not a null result (Fisher power 0.08 against a 2.5× effect).
- **Q6 restated**: "memoryless" → "no cadence detectable, and none weaker than near-metronomic could have
  been", with the power statement attached.
- **Q8 requoted**: 20 ft 10–13 yr and 23 ft **20–29 yr** with the 1982 crest as historical information, which
  replaces the station-skew case as the headline sensitivity.
- **Q4 Hardy weakened**: reported with its placebo (+9.7 %, 11 % of trials reach the effect) and the 90-day
  skip result (+8.0 %, CI spans zero). Mammoth stands and is stronger than claimed (placebo +0.6 %, 0/200).

**Conclusions that became stronger.**

- **Q1 Hardy**: the low-flow rise is a finding. Led by the Hardy/Mammoth min7 ratio (+0.0124/yr, p=0.002),
  which involves no precipitation model, plus precip-only fits significant on all three sources.
- **Q5**: the field-measurement stage decline (−0.015 ft/yr, p<0.0001) retires the "IV-derived only"
  limitation and the "no datum records reviewed" limitation.
- **Q2**: now rests on a pre-registered upper-tail test (q=0.90 quantile regression) rather than a
  conjunction rule that could barely fail.

**Corrections of wording and number.**

- Mammoth "≈0 on all three sources" → the PRISM fits are consistently, marginally negative (one CI excludes
  zero).
- Buffer-vs-polygon → a p-value threshold crossing, not an attribution to the geometry (difference trend
  +0.27 in/decade, CI spans zero, r=0.984).
- West Plains days ≥1 in → reported with the catch-ratio sensitivity 1.00–1.10, plus the residual 1998 splice
  step in SDII and the recharge season.
- Coupling → "onset within 2 days; monthly correlation maximised at lag 1 month". The monthly figure is a
  bin, not a transit time.
- BFI's null is **not** evidence against a base-flow change (a ratio near 1 is nearly blind to the absolute
  rate); Pettitt p-values now sit beside their years, and Mammoth's WY2008 change-point is not significant
  (p=0.26). On complete water years the Hardy−Mammoth difference and the ratio both locate the change at
  WY2014 — the earlier WY2008-vs-WY2013 discrepancy was an incomplete-final-year artefact.
- §6.1 → effective n by water-year block (Hardy 11 of 16 events; Mammoth 32 of 80), 7 Mammoth fits with
  r²<0.75 flagged, and a Watson–Williams test across decades: no drift on the long Imboden series (p=0.32),
  though the three-decade Hardy annual-peak series does reject a common mean (p=0.027).

**Still open.** NOAA's AORC v1.1 homogeneity documentation and a one-cell AORC re-pull at the gauge
coordinate; an independent gridded product with no 2002 input change (nClimGrid-Daily, Livneh);
quantile-based COOP/KUNO homogenisation; PeakFQ/EMA with the 1982 crest; synoptic seepage runs
Mammoth → South Fork → Hardy; the USGS shift tables (field and channel measurements are now in hand).
