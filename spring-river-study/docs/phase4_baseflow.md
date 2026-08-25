# Phase 4 — base flow (Q1, Q4, Q5) — generated 2026-08-25

Every trend line reports Sen slope, 95% CI, MK z/p and n; every analysis is repeated on approved-only data and flagged **CHANGED** if the conclusion differs.

## Q1 attribution

Basin precip: NOAA AORC v1.1 1 km hourly basin mean over the MoDNR Mammoth Spring recharge polygon (~349 mi²), daily totals 24 h ending 12 UTC [aorc], 1981-01-01–2026-01-01; ONI: CPC, 1950-01-01–2026-06-01.

Model: OLS log(min7) ~ p_trailing_in + p_trailing_prev_in + oni_trailing (HC3). Predictors are strictly antecedent to each water year's own min7 window: `p_trailing_in` = basin precip over the 365 days ending the day before that WY's min7 end date; `p_trailing_prev_in` = the 365 days before that; `oni_trailing` = mean ONI over the 6 months ending the month before the min7 end date. (The earlier fixed Sep–Feb recharge total leaked precipitation that fell after most years' min7.) Precip predictors require ≥90% day coverage; ONI ≥4 of 6 months. Incomplete water years are excluded from the fit.

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

Post window: 6 months of Eckhardt base flow starting 30 days after the event (past the recession limb). Controls: the 3 non-flood years (no ≥16 ft event within ±1 yr) closest in standardized distance on same-calendar post-window precip AND antecedent base flow (mean over the 90 days before the event date). `pre_bf_cfs` / `matched_pre_bf_cfs` show the antecedent match.

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

## Limitations

- Regional-skew, datum and USGS rating-shift records remain unobtained; Q5 rests on IV-derived stage-at-flow only.
- Hardy series is WY 2002+ (n≤24); Mammoth Spring vent carries the 1981+ record.
- Q4 n equals the number of ≥16 ft events in the Hardy peak file; CI is a bootstrap on a handful of events and excludes matching uncertainty and control-year reuse (descriptive, not causal).
- Q5 shifts use ±365-day windows around each event; events before IV_START (2007-10-01) have no pairs and are omitted.
- Basin precip: NOAA AORC v1.1 1 km hourly basin mean over the MoDNR Mammoth Spring recharge polygon (~349 mi²), daily totals 24 h ending 12 UTC. The polygon excludes recharge shared with Bill Mac and Greer springs (separate MoDNR layers). AORC before 2002 has no radar input and shares gauge/Stage IV inputs with PRISM, so the two grids are not independent.
