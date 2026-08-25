# Phase 4 — base flow (Q1, Q4, Q5) — generated 2026-08-25

Every trend line reports Sen slope, 95% CI, MK z/p and n; every analysis is repeated on approved-only data and flagged **CHANGED** if the conclusion differs.

## Q1 attribution

Basin precip: PRISM 30 km buffer around West Plains, 1981-01-01–2026-08-24; ONI: CPC, 1950-01-01–2026-06-01.

Model: OLS log(min7) ~ p_trailing_in + p_trailing_prev_in + oni_trailing (HC3). Predictors are strictly antecedent to each water year's own min7 window: `p_trailing_in` = basin precip over the 365 days ending the day before that WY's min7 end date; `p_trailing_prev_in` = the 365 days before that; `oni_trailing` = mean ONI over the 6 months ending the month before the min7 end date. (The earlier fixed Sep–Feb recharge total leaked precipitation that fell after most years' min7.) Precip predictors require ≥90% day coverage; ONI ≥4 of 6 months. Incomplete water years are excluded from the fit.

### Mammoth

- Series: source: USGS DV 07069190 discharge; period 1981-02-25–2026-08-23; approved 99%, provisional from 2026-04-09
- min7 raw trend (log-cfs): Sen slope 0.000319 log-cfs/yr (95% CI -0.00376 to 0.00357); MK z=0.13, p=0.897; n=42
- Pettitt change-point on min7: after WY 2008 (K=178, p=0.260, n=45)
- OLS log(min7) ~ p_trailing_in + p_trailing_prev_in + oni_trailing (HC3): R²=0.45, n=42
  - p_trailing_in: 0.0130 (95% CI 0.0089 to 0.0171)
  - p_trailing_prev_in: 0.0007 (95% CI -0.0035 to 0.0049)
  - oni_trailing: 0.0189 (95% CI -0.0222 to 0.0600)
- **Residual trend (non-climatic component): Sen slope -0.00222 log-cfs/yr (95% CI -0.00497 to 0.000453); MK z=-1.71, p=0.087; n=42**

Sensitivity (approved-only re-run of the full chain):
- residual trend (all): Sen slope -0.00222 /yr (95% CI -0.00497 to 0.000453); MK z=-1.71, p=0.087; n=42
- residual trend (approved-only): Sen slope -0.00222 /yr (95% CI -0.00497 to 0.000453); MK z=-1.71, p=0.087; n=42
- min7 raw trend (all): Sen slope 0.000319 /yr (95% CI -0.00376 to 0.00357); MK z=0.13, p=0.897; n=42
- min7 raw trend (approved-only): Sen slope 0.000319 /yr (95% CI -0.00376 to 0.00357); MK z=0.13, p=0.897; n=42
- Pettitt (approved-only): after WY 2008 (K=178, p=0.260, n=45)
- OLS (approved-only): R²=0.45, n=42
  - p_trailing_in: 0.0130 (95% CI 0.0089 to 0.0171)
  - p_trailing_prev_in: 0.0007 (95% CI -0.0035 to 0.0049)
  - oni_trailing: 0.0189 (95% CI -0.0222 to 0.0600)

### Hardy

- Series: source: USGS DV 07069305 discharge; period 2001-10-01–2026-08-23; approved 99%, provisional from 2026-04-09
- min7 raw trend (log-cfs): Sen slope 0.023 log-cfs/yr (95% CI 0.00736 to 0.0361); MK z=3.05, p=0.002; n=24
- Pettitt change-point on min7: after WY 2013 (K=110, p=0.013, n=24)
- OLS log(min7) ~ p_trailing_in + p_trailing_prev_in + oni_trailing (HC3): R²=0.47, n=24
  - p_trailing_in: 0.0230 (95% CI 0.0097 to 0.0363)
  - p_trailing_prev_in: 0.0173 (95% CI 0.0046 to 0.0300)
  - oni_trailing: 0.0779 (95% CI -0.0465 to 0.2022)
- **Residual trend (non-climatic component): Sen slope 0.00676 log-cfs/yr (95% CI -0.00135 to 0.0195); MK z=1.76, p=0.078; n=24**

Sensitivity (approved-only re-run of the full chain):
- residual trend (all): Sen slope 0.00676 /yr (95% CI -0.00135 to 0.0195); MK z=1.76, p=0.078; n=24
- residual trend (approved-only): Sen slope 0.00676 /yr (95% CI -0.00135 to 0.0195); MK z=1.76, p=0.078; n=24
- min7 raw trend (all): Sen slope 0.023 /yr (95% CI 0.00736 to 0.0361); MK z=3.05, p=0.002; n=24
- min7 raw trend (approved-only): Sen slope 0.023 /yr (95% CI 0.00736 to 0.0361); MK z=3.05, p=0.002; n=24
- Pettitt (approved-only): after WY 2013 (K=110, p=0.013, n=24)
- OLS (approved-only): R²=0.47, n=24
  - p_trailing_in: 0.0230 (95% CI 0.0097 to 0.0363)
  - p_trailing_prev_in: 0.0173 (95% CI 0.0046 to 0.0300)
  - oni_trailing: 0.0779 (95% CI -0.0465 to 0.2022)

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

## Q4 post-flood base flow vs matched non-flood years

Post window: 6 months of Eckhardt base flow starting 30 days after the event (past the recession limb). Controls: the 3 non-flood years (no ≥16 ft event within ±1 yr) closest in standardized distance on same-calendar post-window precip AND antecedent base flow (mean over the 90 days before the event date). `pre_bf_cfs` / `matched_pre_bf_cfs` show the antecedent match.

### Mammoth

Series: source: USGS DV 07069190 discharge; period 1981-02-25–2026-08-23; approved 99%, provisional from 2026-04-09

| event_date          |   post_bf_cfs |   post_p_in |   pre_bf_cfs | matched_years   |   matched_bf_cfs |   matched_p_in |   matched_pre_bf_cfs |   diff_cfs |   diff_pct |
|:--------------------|--------------:|------------:|-------------:|:----------------|-----------------:|---------------:|---------------------:|-----------:|-----------:|
| 2006-09-23 00:00:00 |         349.4 |        26.4 |        218.3 | 2004,1987,1982  |            287.3 |           26.5 |                223.3 |       62.2 |       21.6 |
| 2008-03-19 00:00:00 |         338.4 |        26.8 |        234.4 | 1996,2003,1990  |            281.6 |           26.6 |                228.9 |       56.8 |       20.2 |
| 2009-10-30 00:00:00 |         362.2 |        22.3 |        275.6 | 2013,1993,2002  |            304.9 |           21   |                267.1 |       57.3 |       18.8 |
| 2011-04-26 00:00:00 |         307.4 |        22.6 |        226   | 2000,2001,2003  |            188.3 |           22.1 |                223.6 |      119.1 |       63.3 |
| 2017-04-30 00:00:00 |         275.5 |        14.1 |        267.6 | 1987,1986,1999  |            227.6 |           16.6 |                292.7 |       47.9 |       21   |
| 2025-04-05 00:00:00 |         354.6 |        26.1 |        358.6 | 2019,1993,1984  |            295.2 |           27.2 |                344.9 |       59.4 |       20.1 |

- mean post-flood base-flow difference: 27.5% (bootstrap 95% CI 19.8 to 42.0); n=6 events; 15 unique control years
- approved-only: 27.5% (bootstrap 95% CI 19.8 to 42.0); n=6 events; 15 unique control years
- CI reflects event-to-event variation only; matching uncertainty and control-year reuse are not propagated — descriptive, not causal.

### Hardy

Series: source: USGS DV 07069305 discharge; period 2001-10-01–2026-08-23; approved 99%, provisional from 2026-04-09

| event_date          |   post_bf_cfs |   post_p_in |   pre_bf_cfs | matched_years   |   matched_bf_cfs |   matched_p_in |   matched_pre_bf_cfs |   diff_cfs |   diff_pct |
|:--------------------|--------------:|------------:|-------------:|:----------------|-----------------:|---------------:|---------------------:|-----------:|-----------:|
| 2006-09-23 00:00:00 |        1231.9 |        26.4 |        251.3 | 2004,2003,2014  |            912.6 |           22.7 |                394   |      319.3 |       35   |
| 2008-03-19 00:00:00 |         787.6 |        26.8 |        721.8 | 2021,2014,2004  |            734.3 |           27.6 |                803.7 |       53.3 |        7.3 |
| 2009-10-30 00:00:00 |        1336.1 |        22.3 |        946.4 | 2013,2020,2014  |           1103.1 |           24.3 |                509.6 |      233   |       21.1 |
| 2011-04-26 00:00:00 |         698.1 |        22.6 |        632.4 | 2004,2014,2003  |            471.6 |           26.3 |                698.4 |      226.5 |       48   |
| 2017-04-30 00:00:00 |         600.3 |        14.1 |        903.5 | 2021,2022,2023  |            522.7 |           18.5 |               1347   |       77.6 |       14.8 |
| 2025-04-05 00:00:00 |         975.3 |        26.1 |       1270.9 | 2015,2019,2002  |            875.4 |           28.4 |               1339.5 |       99.9 |       11.4 |

- mean post-flood base-flow difference: 22.9% (bootstrap 95% CI 12.6 to 35.1); n=6 events; 11 unique control years
- approved-only: 22.9% (bootstrap 95% CI 12.6 to 35.1); n=6 events; 11 unique control years
- CI reflects event-to-event variation only; matching uncertainty and control-year reuse are not propagated — descriptive, not causal.

![postflood](../reports/figures/phase4_postflood.png)

## Limitations

- Regional-skew, datum and USGS rating-shift records remain unobtained; Q5 rests on IV-derived stage-at-flow only.
- Hardy series is WY 2002+ (n≤24); Mammoth Spring vent carries the 1981+ record.
- Q4 n equals the number of ≥16 ft events in the Hardy peak file; CI is a bootstrap on a handful of events and excludes matching uncertainty and control-year reuse (descriptive, not causal).
- Q5 shifts use ±365-day windows around each event; events before IV_START (2007-10-01) have no pairs and are omitted.
- Basin precip is the 30 km West Plains PRISM buffer, not a dye-traced recharge polygon.
