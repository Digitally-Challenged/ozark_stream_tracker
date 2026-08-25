# Phase 4 — base flow (Q1, Q4, Q5) — generated 2026-08-25

Every trend line reports Sen slope, 95% CI, MK z/p and n; every analysis is repeated on approved-only data and flagged **CHANGED** if the conclusion differs.

## Q1 attribution

Basin precip: NOAA AORC v1.1 1 km hourly basin mean over the MoDNR Mammoth Spring recharge polygon (~349 mi²), daily totals 24 h ending 12 UTC [aorc], 1981-01-01–2026-01-01; ONI: CPC, 1950-01-01–2026-06-01.

Model: OLS log(min7) ~ p_trailing_in + p_trailing_prev_in + oni_trailing (HC3). Predictors are strictly antecedent to each water year's own min7 window: `p_trailing_in` = basin precip over the 365 days ending the day before that WY's 7-day min7 window STARTS (its end date minus 7 days); `p_trailing_prev_in` = the 365 days before that; `oni_trailing` = mean ONI over the 6 center-months ending in the month before that same window-start day (end date minus 7 days). (The earlier fixed Sep–Feb recharge total leaked precipitation that fell after most years' min7.) Precip predictors require ≥90% day coverage; ONI ≥4 of 6 months. Incomplete water years are excluded from the fit.

### Mammoth

- Series: source: USGS DV 07069190 discharge; period 1981-02-25–2026-08-23; approved 99%, provisional from 2026-04-09
- min7 raw trend (log-cfs): Sen slope 0.000319 log-cfs/yr (95% CI -0.00376 to 0.00357); MK z=0.13, p=0.897; n=42
- Pettitt change-point on min7: after WY 2008 (K=178, p=0.260, n=45)
- OLS log(min7) ~ p_trailing_in + p_trailing_prev_in + oni_trailing (HC3): R²=0.58, n=42
  - p_trailing_in: 0.0156 (95% CI 0.0111 to 0.0201)
  - p_trailing_prev_in: 0.0032 (95% CI -0.0007 to 0.0071)
  - oni_trailing: 0.0115 (95% CI -0.0232 to 0.0461)
- **Residual trend (non-climatic component): Sen slope -0.00126 log-cfs/yr (95% CI -0.00326 to 0.00122); MK z=-0.91, p=0.363; n=42**

Sensitivity (approved-only re-run of the full chain):
- residual trend (all): Sen slope -0.00126 /yr (95% CI -0.00326 to 0.00122); MK z=-0.91, p=0.363; n=42
- residual trend (approved-only): Sen slope -0.00126 /yr (95% CI -0.00326 to 0.00122); MK z=-0.91, p=0.363; n=42
- min7 raw trend (all): Sen slope 0.000319 /yr (95% CI -0.00376 to 0.00357); MK z=0.13, p=0.897; n=42
- min7 raw trend (approved-only): Sen slope 0.000319 /yr (95% CI -0.00376 to 0.00357); MK z=0.13, p=0.897; n=42
- Pettitt (approved-only): after WY 2008 (K=178, p=0.260, n=45)
- OLS (approved-only): R²=0.58, n=42
  - p_trailing_in: 0.0156 (95% CI 0.0111 to 0.0201)
  - p_trailing_prev_in: 0.0032 (95% CI -0.0007 to 0.0071)
  - oni_trailing: 0.0115 (95% CI -0.0232 to 0.0461)

### Hardy

- Series: source: USGS DV 07069305 discharge; period 2001-10-01–2026-08-23; approved 99%, provisional from 2026-04-09
- min7 raw trend (log-cfs): Sen slope 0.023 log-cfs/yr (95% CI 0.00736 to 0.0361); MK z=3.05, p=0.002; n=24
- Pettitt change-point on min7: after WY 2013 (K=110, p=0.013, n=24)
- OLS log(min7) ~ p_trailing_in + p_trailing_prev_in + oni_trailing (HC3): R²=0.41, n=24
  - p_trailing_in: 0.0231 (95% CI 0.0088 to 0.0375)
  - p_trailing_prev_in: 0.0164 (95% CI 0.0056 to 0.0272)
  - oni_trailing: 0.0479 (95% CI -0.0800 to 0.1757)
- **Residual trend (non-climatic component): Sen slope 0.0203 log-cfs/yr (95% CI 0.00915 to 0.0291); MK z=3.99, p=0.000; n=24**

Sensitivity (approved-only re-run of the full chain):
- residual trend (all): Sen slope 0.0203 /yr (95% CI 0.00915 to 0.0291); MK z=3.99, p=0.000; n=24
- residual trend (approved-only): Sen slope 0.0203 /yr (95% CI 0.00915 to 0.0291); MK z=3.99, p=0.000; n=24
- min7 raw trend (all): Sen slope 0.023 /yr (95% CI 0.00736 to 0.0361); MK z=3.05, p=0.002; n=24
- min7 raw trend (approved-only): Sen slope 0.023 /yr (95% CI 0.00736 to 0.0361); MK z=3.05, p=0.002; n=24
- Pettitt (approved-only): after WY 2013 (K=110, p=0.013, n=24)
- OLS (approved-only): R²=0.41, n=24
  - p_trailing_in: 0.0231 (95% CI 0.0088 to 0.0375)
  - p_trailing_prev_in: 0.0164 (95% CI 0.0056 to 0.0272)
  - oni_trailing: 0.0479 (95% CI -0.0800 to 0.1757)

## Q1c Hardy low-flow rise: evidence without a precipitation model

The published Hardy residual is source-dependent, which was reported as a reason not to call it a finding. Two checks say otherwise, and neither depends on a gridded precipitation product.

### Hardy against Mammoth Spring (no precipitation model)

Mammoth Spring is the best available climate control for Hardy: the same recharge climate, absorbing precipitation, ENSO, PET and any gridded-precip bias at once. If Hardy's rise were climate, it would vanish against Mammoth.

- **log(Hardy min7 / Mammoth min7) trend: Sen slope 0.0124 log-ratio/yr (95% CI 0.00278 to 0.0219); MK z=3.05, p=0.002; n=24**
- Pettitt change-point on the log ratio: after WY 2014 (K=101, p=0.029, n=24)
- the ratio rises by a factor 1.33 across WY 2002–2025.

### Precip-only fits (the ONI term dropped)

At n≈24 the never-significant ONI regressor costs a degree of freedom for nothing. Dropping it:

| series   | basin_source   |   n |     r2 |   resid_slope |      lo |     hi |      p |
|:---------|:---------------|----:|-------:|--------------:|--------:|-------:|-------:|
| Mammoth  | aorc           |  42 | 0.5734 |       -0.0012 | -0.0033 | 0.0012 | 0.2785 |
| Hardy    | aorc           |  24 | 0.3956 |        0.0213 |  0.0108 | 0.0293 | 0      |
| Mammoth  | prism_polygon  |  42 | 0.5156 |       -0.0022 | -0.0049 | 0      | 0.0537 |
| Hardy    | prism_polygon  |  24 | 0.5407 |        0.0116 |  0.0017 | 0.0208 | 0.0211 |
| Mammoth  | prism_buffer   |  42 | 0.4368 |       -0.0021 | -0.0051 | 0.0003 | 0.104  |
| Hardy    | prism_buffer   |  24 | 0.4353 |        0.011  |  0.0027 | 0.0227 | 0.0161 |

- Hardy's residual rise has a CI excluding zero on 3 of 3 basin sources; the source-dependence of the published figure was one weak regressor, not a fragile signal.
- **The rise is therefore reported as a finding, not as a source artefact.** Its cause is Q1c/Q5: the channel at Hardy degraded (see the field-measurement trend below), and the reach gains water the spring alone does not account for.

### Mammoth residual across basin sources and trailing windows

The 365-day predictor window is a convention. A karst spring with a ~188-day recession constant may remember rain for longer, so each source is refitted at 730 days as well (precip-only, ONI dropped).

| basin_source   |   window_days |   n |      r2 |   resid_slope |       lo |       hi |       p |
|:---------------|--------------:|----:|--------:|--------------:|---------:|---------:|--------:|
| aorc           |           365 |  42 | 0.57337 |      -0.00122 | -0.00331 |  0.00117 | 0.27848 |
| aorc           |           730 |  40 | 0.40855 |      -0.00199 | -0.00542 |  0.00091 | 0.18029 |
| prism_polygon  |           365 |  42 | 0.51561 |      -0.00219 | -0.00486 |  3e-05   | 0.05372 |
| prism_polygon  |           730 |  40 | 0.33036 |      -0.0035  | -0.00654 | -0.0004  | 0.03496 |
| prism_buffer   |           365 |  42 | 0.43682 |      -0.00206 | -0.00507 |  0.00034 | 0.10403 |
| prism_buffer   |           730 |  40 | 0.28478 |      -0.00326 | -0.0064  |  0.00017 | 0.05755 |

- specifications whose CI excludes zero (all on the negative side): 1 of 6 — prism_polygon at 730 d (p=0.035).
- **Correction to the published wording.** The Mammoth conclusion survives on the primary series, but '≈0 on all three sources' claims a unanimity the numbers do not support: the PRISM fits are consistently, marginally negative, and one specification's CI excludes zero. State it that way, with the same candour applied to Hardy.
- Settling it needs a basin series independent of PRISM's gauge network (Stage IV/MRMS 2002→, Livneh, nClimGrid-Daily) and a window pre-registered from spring recession or tracer transit rather than from convention.

### BFI trend (gap-segmented Eckhardt; Lyne-Hollick check)

- Mammoth BFI (eckhardt): Sen slope 2.31e-05 BFI/yr (95% CI -4.6e-05 to 0.000117); MK z=0.75, p=0.451; n=45
  - Mammoth BFI (eckhardt) (all): Sen slope 2.31e-05 /yr (95% CI -4.6e-05 to 0.000117); MK z=0.75, p=0.451; n=45
  - Mammoth BFI (eckhardt) (approved-only): Sen slope 8.99e-06 /yr (95% CI -6.31e-05 to 9.53e-05); MK z=0.33, p=0.739; n=44
- Mammoth BFI (lyne_hollick): Sen slope -6.9e-05 BFI/yr (95% CI -0.000346 to 0.000245); MK z=-0.44, p=0.660; n=45
  - Mammoth BFI (lyne_hollick) (all): Sen slope -6.9e-05 /yr (95% CI -0.000346 to 0.000245); MK z=-0.44, p=0.660; n=45
  - Mammoth BFI (lyne_hollick) (approved-only): Sen slope -0.000116 /yr (95% CI -0.000385 to 0.000222); MK z=-0.80, p=0.424; n=44
- Hardy BFI (eckhardt): Sen slope 0.00127 BFI/yr (95% CI -0.00135 to 0.00384); MK z=1.10, p=0.272; n=25
  - Hardy BFI (eckhardt) (all): Sen slope 0.00127 /yr (95% CI -0.00135 to 0.00384); MK z=1.10, p=0.272; n=25
  - Hardy BFI (eckhardt) (approved-only): Sen slope 0.000726 /yr (95% CI -0.00202 to 0.0032); MK z=0.57, p=0.568; n=24
- Hardy BFI (lyne_hollick): Sen slope 0.0039 BFI/yr (95% CI -0.00119 to 0.00879); MK z=1.66, p=0.097; n=25
  - Hardy BFI (lyne_hollick) (all): Sen slope 0.0039 /yr (95% CI -0.00119 to 0.00879); MK z=1.66, p=0.097; n=25
  - Hardy BFI (lyne_hollick) (approved-only): Sen slope 0.00295 /yr (95% CI -0.00202 to 0.00717); MK z=1.17, p=0.244; n=24

**What a null BFI trend is not.** BFI is a ratio, and at a spring-fed river it sits near 1, so it is nearly blind to a change in the absolute base-flow *rate*: base flow and total flow can both rise together and leave the ratio flat. These nulls are reported as stated, but they are **not evidence against a base-flow change** and must not be cited as corroboration of one. The min7 series and the Hardy/Mammoth ratio above carry that question.

![min7](../reports/figures/phase4_min7_trend.png)

## Q5 rating drift (stage at fixed discharge, Hardy IV pairs)

Pairs: source: USGS IV 07069305 discharge+stage; period 2007-10-01–2026-08-24; approved 98%, provisional from 2026-04-09; n=666986 matched 15-min pairs.

Stage at each target flow is a local log-linear fit (stage = a + b·log10 q) over pairs within ±20% of the target, evaluated at 400 and 1000 cfs, per water year (min 30 pairs per band).

|   wy |   400.0 |   1000.0 |
|-----:|--------:|---------:|
| 2008 |    3.27 |     3.94 |
| 2009 |    3.21 |     3.88 |
| 2010 |    3.03 |     3.79 |
| 2011 |    3.05 |     3.73 |
| 2012 |    3.04 |     3.76 |
| 2013 |    3.11 |     3.75 |
| 2014 |    3.05 |     3.71 |
| 2015 |    3.03 |     3.71 |
| 2016 |    3.04 |     3.65 |
| 2017 |    2.99 |     3.67 |
| 2018 |    3.01 |     3.63 |
| 2019 |    3.01 |     3.62 |
| 2020 |    3.01 |     3.62 |
| 2021 |    3.01 |     3.57 |
| 2022 |    3.01 |     3.57 |
| 2023 |    2.95 |     3.55 |
| 2024 |    2.96 |     3.53 |
| 2025 |    2.97 |     3.52 |
| 2026 |    2.95 |     3.56 |

Shift across ≥16 ft events: same local fit on pairs in the 365 days before vs the 365 days after each event date (n_before/n_after = pairs in each band).

| event_date          |   flow_cfs |   stage_before_ft |   stage_after_ft |   shift_ft |   n_before |   n_after |
|:--------------------|-----------:|------------------:|-----------------:|-----------:|-----------:|----------:|
| 2008-03-19 00:00:00 |        400 |              3.33 |             3.21 |      -0.12 |       8678 |     12473 |
| 2008-03-19 00:00:00 |       1000 |              4.02 |             3.88 |      -0.14 |       1845 |      4376 |
| 2009-10-30 00:00:00 |        400 |              3.21 |             3.03 |      -0.18 |       9634 |      7263 |
| 2009-10-30 00:00:00 |       1000 |              3.88 |             3.79 |      -0.08 |       6332 |      6189 |
| 2011-04-26 00:00:00 |        400 |              3.05 |             3.04 |      -0.01 |      18468 |      5578 |
| 2011-04-26 00:00:00 |       1000 |              3.83 |             3.73 |      -0.1  |       4003 |      9803 |
| 2017-04-30 00:00:00 |        400 |              2.99 |             3.01 |       0.02 |       3960 |     16859 |
| 2017-04-30 00:00:00 |       1000 |              3.65 |             3.66 |       0    |       7079 |      4930 |
| 2025-04-05 00:00:00 |        400 |              2.97 |             2.96 |      -0.01 |       3853 |     16078 |
| 2025-04-05 00:00:00 |       1000 |              3.53 |             3.52 |      -0.01 |       9474 |      1852 |

Event 2006-09-23 omitted from the shift table: no IV pairs within ±365 days (predates IV_START 2007-10-01).

- stage at 400 cfs: Sen slope -0.00791 ft/yr (95% CI -0.0132 to -0.00491); MK z=-4.41, p=0.000; n=19
  - stage at 400 cfs (all): Sen slope -0.00791 /yr (95% CI -0.0132 to -0.00491); MK z=-4.41, p=0.000; n=19
  - stage at 400 cfs (approved-only): Sen slope -0.00784 /yr (95% CI -0.0131 to -0.00483); MK z=-4.34, p=0.000; n=19
- stage at 1000 cfs: Sen slope -0.0187 ft/yr (95% CI -0.0214 to -0.0157); MK z=-5.46, p=0.000; n=19
  - stage at 1000 cfs (all): Sen slope -0.0187 /yr (95% CI -0.0214 to -0.0157); MK z=-5.46, p=0.000; n=19
  - stage at 1000 cfs (approved-only): Sen slope -0.0187 /yr (95% CI -0.0214 to -0.0157); MK z=-5.32, p=0.000; n=19

![rating](../reports/figures/phase4_rating_drift.png)

### Field-measured stage at fixed discharge (independent of the rating)

Source: USGS OGC API `field-measurements` and `channel-measurements` (`api.waterdata.usgs.gov/ogcapi/v0`), site 07069305; 502 readings over 134 visits with both a measured discharge and a measured stage, 2001-12-18–2026-08-18; 151 channel surveys.

Both numbers in each pair are *measured at the visit* — the discharge by wading or ADCP, not computed from the stage — so a decline here cannot be rating drift. Stage is normalised to 400 cfs along a single log-linear fit through the 330–520 cfs band, then averaged per water year.

- **field-measured stage at 400 cfs: Sen slope -0.0149 ft/yr (95% CI -0.0219 to -0.0105); MK z=-4.19, p=0.000; n=20**
- water years covered: 2003–2026 (20 with a qualifying visit; 33 visits).
- total fall over the record: 0.40 ft.
- This is steeper than the IV-derived figure and four years longer, and it brackets the 2006-09-23 event the shift table has to omit. It retires both the 'IV-derived only' limitation and the 'events before IV_START have no pairs' gap: **the channel really degraded; the rating followed it.**

|   wy |   stage_at_flow_ft |   n_visits |
|-----:|-------------------:|-----------:|
| 2003 |              3.361 |          2 |
| 2004 |              3.412 |          1 |
| 2005 |              3.48  |          1 |
| 2007 |              3.249 |          1 |
| 2008 |              3.176 |          1 |
| 2009 |              3.201 |          1 |
| 2011 |              3.029 |          2 |
| 2012 |              3.018 |          2 |
| 2014 |              3.091 |          2 |
| 2015 |              3.122 |          2 |
| 2016 |              3.076 |          1 |
| 2017 |              3.097 |          1 |
| 2018 |              2.988 |          2 |
| 2020 |              3.109 |          1 |
| 2021 |              3.075 |          1 |
| 2022 |              3.026 |          2 |
| 2023 |              2.993 |          2 |
| 2024 |              2.979 |          3 |
| 2025 |              3.016 |          1 |
| 2026 |              2.962 |          4 |

### Gauge datum

- current datum: 342.73 ft NAVD88 (±0.16, GNSS1 - Level 1 Quality Survey Grade Global Navigation Satellite System), from the `monitoring-locations` endpoint.
- The datum elevation carries **two revisions** (340.91→342.49 ft before Dec 2022; 342.49→342.73 ft between Dec 2022 and Dec 2024 — the value above). Both are post-2022 bookkeeping of the datum elevation: **no site move, and nothing at WY2008**, so neither can explain the low-flow step. `time-series-revisions` returns no rows for this site.

### Measured vs computed low flow, by era

Field-measured discharge below 800 cfs against the same day's published daily value (n=65 visits). Reported with its scatter: the era means are a few per cent either side of zero with a standard deviation several times larger, not '~1 % in every era'.

| era       |   n |   mean_pct |   median_pct |   sd_pct |
|:----------|----:|-----------:|-------------:|---------:|
| 2001–2007 |  16 |        1.3 |          1.8 |      5.1 |
| 2008–2014 |  21 |       -1.1 |         -1.3 |      4   |
| 2015–2025 |  25 |       -0.3 |         -0.1 |      3.3 |
| 2026      |   3 |        3.3 |          3.4 |      3.3 |

This agreement is **not independent evidence**: USGS shifts the rating to these very measurements, so close agreement shows only that the rating tracks them. The rating-independent evidence is the measured-stage decline above and the Hardy/Mammoth ratio in Q1c.

### Stage–discharge lookup

Pairs: source: USGS IV 07069305 discharge+stage; period 2007-10-01–2026-08-24; approved 98%, provisional from 2026-04-09. Median (and IQR in the parquet) of discharge over pairs within ±0.05 ft of each stage; `recent` = pairs from 2023-10-01 (WY 2024+); NaN where fewer than 20 pairs.

|   stage_ft |   whole_record_median_cfs |   recent_median_cfs |   n_whole |   n_recent |
|-----------:|--------------------------:|--------------------:|----------:|-----------:|
|        2.5 |                       nan |                 nan |         0 |          0 |
|        3.0 |                       396 |                 427 |    110130 |      23363 |
|        3.5 |                       834 |                 968 |     35941 |       4783 |
|        4.0 |                      1370 |                1620 |     23156 |       2933 |
|        5.0 |                      2780 |                2980 |      4828 |        378 |
|        6.0 |                      4550 |                4610 |      1184 |         99 |
|        8.0 |                      9480 |                9560 |       185 |         34 |
|       10.0 |                     15700 |                 nan |        72 |          2 |
|       12.0 |                     23300 |                 nan |        34 |          8 |
|       14.0 |                     31000 |                 nan |        39 |          2 |
|       16.0 |                       nan |                 nan |        11 |          1 |
|       18.0 |                       nan |                 nan |         7 |          2 |
|       20.0 |                       nan |                 nan |        10 |          6 |
|       22.0 |                       nan |                 nan |         7 |          1 |

Correlation: Pearson r of log10 stage vs log10 discharge = 0.9690; Spearman rho = 0.9634; n=666986 pairs. Annual-peak log-log fit log10 Q = 1.9538 + 2.2152·log10 H (R²=0.991, n=24 peaks).

Flow percentile → stage (Hardy DV discharge percentiles; median stage of recent pairs within ±3% of each flow):

|   percentile |   q_cfs |   stage_ft |   n_pairs |
|-------------:|--------:|-----------:|----------:|
|            5 |     328 |       2.87 |      2865 |
|           25 |     440 |       3    |      4485 |
|           50 |     690 |       3.23 |      3227 |
|           75 |    1230 |       3.73 |      1735 |
|           95 |    2859 |       4.91 |       379 |

![rating_curve](../reports/figures/phase4_rating_curve.png)

## Q4 post-flood base flow vs matched non-flood years

Post window: 6 months of Eckhardt base flow starting 30 days after the event (past the recession limb). Controls: the 3 non-flood years (no ≥16 ft event within ±1 yr) closest in standardized distance on same-calendar post-window precip AND antecedent base flow (mean over the 90 days before the event date). `pre_bf_cfs` / `matched_pre_bf_cfs` show the antecedent match; precip windows with < 90 % day coverage are NaN and drop out of the match distance.

### Mammoth

Series: source: USGS DV 07069190 discharge; period 1981-02-25–2026-08-23; approved 99%, provisional from 2026-04-09

| event_date          |   post_bf_cfs |   post_p_in |   pre_bf_cfs | matched_years   |   matched_bf_cfs |   matched_p_in |   matched_pre_bf_cfs |   diff_cfs |   diff_pct |
|:--------------------|--------------:|------------:|-------------:|:----------------|-----------------:|---------------:|---------------------:|-----------:|-----------:|
| 2006-09-23 00:00:00 |         349.4 |        25.3 |        218.3 | 2004,1987,2014  |            288.9 |           26.5 |                227.5 |       60.6 |       21   |
| 2008-03-19 00:00:00 |         338.4 |        26.5 |        234.4 | 1982,2003,1990  |            268.1 |           25.6 |                233.2 |       70.3 |       26.2 |
| 2009-10-30 00:00:00 |         362.2 |        25   |        275.6 | 2021,2013,2015  |            321.1 |           25.8 |                270.3 |       41.1 |       12.8 |
| 2011-04-26 00:00:00 |         307.4 |        23.2 |        226   | 2000,2001,1987  |            190   |           20.9 |                235.9 |      117.4 |       61.8 |
| 2017-04-30 00:00:00 |         275.5 |        14   |        267.6 | 1999,1986,1987  |            227.6 |           18   |                292.7 |       47.9 |       21   |
| 2025-04-05 00:00:00 |         354.6 |        24.1 |        358.6 | 1991,1988,2019  |            313.3 |           25   |                352.5 |       41.4 |       13.2 |

- mean post-flood base-flow difference: 26.0% (bootstrap 95% CI 15.7 to 41.0); n=6 events; 16 unique control years
- approved-only: 26.0% (bootstrap 95% CI 15.7 to 41.0); n=6 events; 16 unique control years
- CI reflects event-to-event variation only; matching uncertainty and control-year reuse are not propagated — descriptive, not causal.

### Hardy

Series: source: USGS DV 07069305 discharge; period 2001-10-01–2026-08-23; approved 99%, provisional from 2026-04-09

| event_date          |   post_bf_cfs |   post_p_in |   pre_bf_cfs | matched_years   |   matched_bf_cfs |   matched_p_in |   matched_pre_bf_cfs |   diff_cfs |   diff_pct |
|:--------------------|--------------:|------------:|-------------:|:----------------|-----------------:|---------------:|---------------------:|-----------:|-----------:|
| 2006-09-23 00:00:00 |        1231.9 |        25.3 |        251.3 | 2004,2014,2003  |            912.6 |           23.8 |                394   |      319.3 |       35   |
| 2008-03-19 00:00:00 |         787.6 |        26.5 |        721.8 | 2003,2004,2014  |            578.6 |           27.7 |                724.2 |      209   |       36.1 |
| 2009-10-30 00:00:00 |        1336.1 |        25   |        946.4 | 2013,2020,2022  |           1054.7 |           23.5 |                508.8 |      281.5 |       26.7 |
| 2011-04-26 00:00:00 |         698.1 |        23.2 |        632.4 | 2004,2014,2013  |            482.4 |           25.8 |                770.6 |      215.8 |       44.7 |
| 2017-04-30 00:00:00 |         600.3 |        14   |        903.5 | 2021,2022,2014  |            564.1 |           20.1 |               1133.1 |       36.2 |        6.4 |
| 2025-04-05 00:00:00 |         975.3 |        24.1 |       1270.9 | 2015,2002,2023  |            720.4 |           25.1 |               1279.2 |      254.9 |       35.4 |

- mean post-flood base-flow difference: 30.7% (bootstrap 95% CI 19.6 to 38.7); n=6 events; 10 unique control years
- approved-only: 30.7% (bootstrap 95% CI 19.6 to 38.7); n=6 events; 10 unique control years
- CI reflects event-to-event variation only; matching uncertainty and control-year reuse are not propagated — descriptive, not causal.

![postflood](../reports/figures/phase4_postflood.png)

### Placebo and skip-day sensitivity

With n=6 events, three nearest controls each and heavy control-year reuse, the procedure itself may produce an effect. The placebo runs the identical pipeline on random NON-flood pseudo-events keeping the real events' days-of-year, so what it returns is what 'no flood' looks like through this machinery. The skip-day sensitivity asks whether the effect is recession water still present in the post window rather than a change in base flow.

Placebo: 200 trials per series, seed 0.

| series   |   real_diff_pct |   placebo_mean |   placebo_sd |   placebo_p95 |   frac_ge_real |   corrected |   n_trials |
|:---------|----------------:|---------------:|-------------:|--------------:|---------------:|------------:|-----------:|
| Mammoth  |           26.01 |           0.6  |         6.94 |         11.54 |           0    |       25.41 |        200 |
| Hardy    |           30.72 |           9.73 |        17.06 |         37.73 |           0.11 |       20.99 |        200 |

Skip-day sensitivity (post window starts this many days after the event):

|   skip_days |   mean_diff_pct |   lo |   hi |   n | series   |
|------------:|----------------:|-----:|-----:|----:|:---------|
|          15 |            25.4 | 12.7 | 38.9 |   6 | Mammoth  |
|          30 |            26   | 15.7 | 41   |   6 | Mammoth  |
|          60 |            19.1 | 12.3 | 28   |   6 | Mammoth  |
|          90 |            21.9 | 11.7 | 31.3 |   6 | Mammoth  |
|          15 |            30.6 | 15.8 | 49   |   6 | Hardy    |
|          30 |            30.7 | 19.6 | 38.7 |   6 | Hardy    |
|          60 |            23.9 |  9.3 | 38.9 |   6 | Hardy    |
|          90 |             8   | -8.1 | 22.8 |   6 | Hardy    |

- **Mammoth**: placebo mean +0.6% (sd 6.9); 0.0% of placebo trials reach the real +26.0%; placebo-corrected effect +25.4%. At a 90-day skip the effect is +21.9% (CI 11.7 to 31.3).
- **Hardy**: placebo mean +9.7% (sd 17.1); 11.0% of placebo trials reach the real +30.7%; placebo-corrected effect +21.0%. At a 90-day skip the effect is +8.0% (CI -8.1 to 22.8) — the CI spans zero.

Reading: an effect worth reporting must sit far outside its own placebo distribution AND survive a later window start. Where the placebo is centred near zero and the effect holds at a long skip, the result stands and is stronger than the bootstrap CI alone suggests. Where a material fraction of placebo trials reach the reported figure and the effect decays as the window moves later, part of it is procedural and part is recession water: report the placebo-corrected value with this sensitivity, not the raw percentage.

## Change-points: what steps, and when

- Mammoth min7: after WY 2008 (K=178, p=0.260, n=45) — **not significant**; it must not be read as a step, and in particular must not be set beside a significant one as if the two agreed.
- Hardy min7: after WY 2013 (K=110, p=0.013, n=24)
- Hardy−Mammoth min7 **difference**: after WY 2014 (K=115, p=0.008, n=24).
- log(Hardy/Mammoth) **ratio**: after WY 2014 (K=101, p=0.029, n=24).

The difference and the ratio both locate the change at WY 2014, so on complete water years the two framings agree; the earlier WY2008-vs-WY2013 discrepancy was an artefact of including an incomplete final year. Synoptic seepage runs (Mammoth → South Fork → Hardy at low flow) are what would settle the cause.

## Limitations

- Regional-skew values and the USGS rating-shift tables remain unobtained. Q5 no longer rests on IV-derived stage-at-flow alone: the field-measurement trend above is independent of the rating, and the gauge datum records have now been reviewed (two post-2022 revisions, no site move, nothing at WY2008).
- Hardy series is WY 2002+ (n≤24); Mammoth Spring vent carries the 1981+ record.
- Q4 n equals the number of ≥16 ft events in the Hardy peak file; CI is a bootstrap on a handful of events and excludes matching uncertainty and control-year reuse (descriptive, not causal).
- Q5 shifts use ±365-day windows around each event; events before IV_START (2007-10-01) have no pairs and are omitted.
- Basin precip: NOAA AORC v1.1 1 km hourly basin mean over the MoDNR Mammoth Spring recharge polygon (~349 mi²), daily totals 24 h ending 12 UTC. The polygon excludes recharge shared with Bill Mac and Greer springs (separate MoDNR layers). AORC before 2002 has no radar input and shares gauge/Stage IV inputs with PRISM, so the two grids are not independent.
