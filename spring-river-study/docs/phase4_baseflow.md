# Phase 4 — base flow (Q1, Q4, Q5) — generated 2026-08-25

Every trend line reports Sen slope, 95% CI, MK z/p and n; every analysis is repeated on approved-only data and flagged **CHANGED** if the conclusion differs.

## Q1 attribution

Basin precip: PRISM 30 km buffer around West Plains, 1981-01-01–2026-08-24; ONI: CPC, 1950-01-01–2026-06-01.

### Mammoth

- Series: source: USGS DV 07069190 discharge; period 1981-02-25–2026-08-23; approved 99%, provisional from 2026-04-09
- min7 raw trend (log-cfs): Sen slope 0.000606 log-cfs/yr (95% CI -0.00298 to 0.00389); MK z=0.46, p=0.645; n=43
- Pettitt change-point: after WY 2008 (K=178, p=0.260, n=45)
- OLS log(min7) ~ p_recharge_in + p_recharge_prev_in + oni_recharge (HC3): R²=0.25, n=43
  - p_recharge_in: 0.0121 (95% CI 0.0064 to 0.0178)
  - p_recharge_prev_in: 0.0084 (95% CI 0.0005 to 0.0163)
  - oni_recharge: -0.0017 (95% CI -0.0343 to 0.0309)
- **Residual trend (non-climatic component): Sen slope 0.00165 log-cfs/yr (95% CI -0.00185 to 0.00465); MK z=0.94, p=0.346; n=43**

Sensitivity:
- residual trend (all): Sen slope 0.00165 /yr (95% CI -0.00185 to 0.00465); MK z=0.94, p=0.346; n=43
- residual trend (approved-only): Sen slope 0.00165 /yr (95% CI -0.00185 to 0.00465); MK z=0.94, p=0.346; n=43
- min7 raw trend (all): Sen slope 0.000606 /yr (95% CI -0.00298 to 0.00389); MK z=0.46, p=0.645; n=43
- min7 raw trend (approved-only): Sen slope 0.000606 /yr (95% CI -0.00298 to 0.00389); MK z=0.46, p=0.645; n=43

### Hardy

- Series: source: USGS DV 07069305 discharge; period 2001-10-01–2026-08-23; approved 99%, provisional from 2026-04-09
- min7 raw trend (log-cfs): Sen slope 0.023 log-cfs/yr (95% CI 0.00798 to 0.0361); MK z=3.05, p=0.002; n=24
- Pettitt change-point: after WY 2013 (K=110, p=0.013, n=24)
- OLS log(min7) ~ p_recharge_in + p_recharge_prev_in + oni_recharge (HC3): R²=0.04, n=24
  - p_recharge_in: -0.0004 (95% CI -0.0208 to 0.0200)
  - p_recharge_prev_in: 0.0104 (95% CI -0.0138 to 0.0345)
  - oni_recharge: 0.0411 (95% CI -0.0401 to 0.1223)
- **Residual trend (non-climatic component): Sen slope 0.0213 log-cfs/yr (95% CI 0.00938 to 0.0341); MK z=3.25, p=0.001; n=24**

Sensitivity:
- residual trend (all): Sen slope 0.0213 /yr (95% CI 0.00938 to 0.0341); MK z=3.25, p=0.001; n=24
- residual trend (approved-only): Sen slope 0.0213 /yr (95% CI 0.00938 to 0.0341); MK z=3.25, p=0.001; n=24
- min7 raw trend (all): Sen slope 0.023 /yr (95% CI 0.00798 to 0.0361); MK z=3.05, p=0.002; n=24
- min7 raw trend (approved-only): Sen slope 0.023 /yr (95% CI 0.00798 to 0.0361); MK z=3.05, p=0.002; n=24

### BFI trend (gap-segmented Eckhardt; Lyne-Hollick check)

- Mammoth BFI (eckhardt): Sen slope 2.31e-05 BFI/yr (95% CI -4.6e-05 to 0.000118); MK z=0.75, p=0.451; n=45
  - Mammoth BFI (eckhardt) (all): Sen slope 2.31e-05 /yr (95% CI -4.6e-05 to 0.000118); MK z=0.75, p=0.451; n=45
  - Mammoth BFI (eckhardt) (approved-only): Sen slope 8.99e-06 /yr (95% CI -6.24e-05 to 9.53e-05); MK z=0.33, p=0.739; n=44
- Mammoth BFI (lyne_hollick): Sen slope -6.9e-05 BFI/yr (95% CI -0.000346 to 0.000247); MK z=-0.44, p=0.660; n=45
  - Mammoth BFI (lyne_hollick) (all): Sen slope -6.9e-05 /yr (95% CI -0.000346 to 0.000247); MK z=-0.44, p=0.660; n=45
  - Mammoth BFI (lyne_hollick) (approved-only): Sen slope -0.000116 /yr (95% CI -0.000382 to 0.000222); MK z=-0.80, p=0.424; n=44
- Hardy BFI (eckhardt): Sen slope 0.00127 BFI/yr (95% CI -0.00133 to 0.00384); MK z=1.10, p=0.272; n=25
  - Hardy BFI (eckhardt) (all): Sen slope 0.00127 /yr (95% CI -0.00133 to 0.00384); MK z=1.10, p=0.272; n=25
  - Hardy BFI (eckhardt) (approved-only): Sen slope 0.000726 /yr (95% CI -0.00197 to 0.0032); MK z=0.57, p=0.568; n=24
- Hardy BFI (lyne_hollick): Sen slope 0.0039 BFI/yr (95% CI -0.00113 to 0.00879); MK z=1.66, p=0.097; n=25
  - Hardy BFI (lyne_hollick) (all): Sen slope 0.0039 /yr (95% CI -0.00113 to 0.00879); MK z=1.66, p=0.097; n=25
  - Hardy BFI (lyne_hollick) (approved-only): Sen slope 0.00295 /yr (95% CI -0.002 to 0.00717); MK z=1.17, p=0.244; n=24

![min7](../reports/figures/phase4_min7_trend.png)

## Q5 rating drift (stage at fixed discharge, Hardy IV pairs)

Pairs: source: USGS IV 07069305 discharge+stage; period 2007-10-01–2026-08-24; approved 98%, provisional from 2026-04-09; n=666986 matched 15-min pairs.

|   wy |   400.0 |   1000.0 |
|-----:|--------:|---------:|
| 2008 |    3.24 |     3.93 |
| 2009 |    3.2  |     3.87 |
| 2010 |    3.05 |     3.78 |
| 2011 |    3.03 |     3.67 |
| 2012 |    3.04 |     3.76 |
| 2013 |    3.08 |     3.75 |
| 2014 |    3.06 |     3.7  |
| 2015 |  nan    |     3.71 |
| 2016 |    3.05 |     3.65 |
| 2017 |    3.02 |     3.67 |
| 2018 |    3    |     3.62 |
| 2019 |    3.02 |     3.63 |
| 2020 |  nan    |     3.62 |
| 2021 |    3.01 |     3.61 |
| 2022 |    3.01 |     3.57 |
| 2023 |    2.96 |     3.54 |
| 2024 |    2.95 |     3.53 |
| 2025 |    2.97 |     3.51 |
| 2026 |    2.95 |     3.56 |

Shift across ≥16 ft events (WY of event → WY+1):

| event_date          |   flow_cfs |   stage_before_ft |   stage_after_ft |   shift_ft |
|:--------------------|-----------:|------------------:|-----------------:|-----------:|
| 2006-09-23 00:00:00 |        400 |            nan    |           nan    |     nan    |
| 2006-09-23 00:00:00 |       1000 |            nan    |           nan    |     nan    |
| 2008-03-19 00:00:00 |        400 |              3.24 |             3.2  |      -0.04 |
| 2008-03-19 00:00:00 |       1000 |              3.93 |             3.87 |      -0.06 |
| 2009-10-30 00:00:00 |        400 |              3.05 |             3.03 |      -0.02 |
| 2009-10-30 00:00:00 |       1000 |              3.78 |             3.67 |      -0.11 |
| 2011-04-26 00:00:00 |        400 |              3.03 |             3.04 |       0.01 |
| 2011-04-26 00:00:00 |       1000 |              3.67 |             3.76 |       0.09 |
| 2017-04-30 00:00:00 |        400 |              3.02 |             3    |      -0.02 |
| 2017-04-30 00:00:00 |       1000 |              3.67 |             3.62 |      -0.05 |
| 2025-04-05 00:00:00 |        400 |              2.97 |             2.95 |      -0.02 |
| 2025-04-05 00:00:00 |       1000 |              3.51 |             3.56 |       0.05 |

- stage at 400 cfs: Sen slope -0.00903 ft/yr (95% CI -0.0146 to -0.00583); MK z=-4.26, p=0.000; n=17
  - stage at 400 cfs (all): Sen slope -0.00903 /yr (95% CI -0.0146 to -0.00583); MK z=-4.26, p=0.000; n=17
  - stage at 400 cfs (approved-only): Sen slope -0.00866 /yr (95% CI -0.014 to -0.00538); MK z=-4.17, p=0.000; n=17
- stage at 1000 cfs: Sen slope -0.0192 ft/yr (95% CI -0.021 to -0.015); MK z=-5.18, p=0.000; n=19
  - stage at 1000 cfs (all): Sen slope -0.0192 /yr (95% CI -0.021 to -0.015); MK z=-5.18, p=0.000; n=19
  - stage at 1000 cfs (approved-only): Sen slope -0.0192 /yr (95% CI -0.021 to -0.015); MK z=-5.11, p=0.000; n=19

![rating](../reports/figures/phase4_rating_drift.png)

## Q4 post-flood base flow vs precip-matched years

### Mammoth

Series: source: USGS DV 07069190 discharge; period 1981-02-25–2026-08-23; approved 99%, provisional from 2026-04-09

| event_date          |   post_bf_cfs |   post_p_in | matched_years   |   matched_bf_cfs |   matched_p_in |   diff_cfs |   diff_pct |
|:--------------------|--------------:|------------:|:----------------|-----------------:|---------------:|-----------:|-----------:|
| 2006-09-23 00:00:00 |         334.8 |        28.3 | 2004,2015,2022  |            284   |           27.3 |       50.9 |       17.9 |
| 2008-03-19 00:00:00 |         358.3 |        35.9 | 2002,2015,2019  |            364.6 |           33   |       -6.2 |       -1.7 |
| 2009-10-30 00:00:00 |         369.4 |        18.8 | 1985,1995,2023  |            251   |           18.4 |      118.4 |       47.2 |
| 2011-04-26 00:00:00 |         336.2 |        22.8 | 1990,1982,1992  |            284.8 |           22.8 |       51.4 |       18   |
| 2017-04-30 00:00:00 |         302.2 |        17.2 | 1987,1997,2001  |            222.2 |           18.2 |       80   |       36   |
| 2025-04-05 00:00:00 |         373.6 |        29.9 | 1993,2015,2020  |            337.6 |           29.1 |       36   |       10.7 |

- mean post-flood base-flow difference: 21.3% (bootstrap 95% CI 9.0 to 34.4); n=6 events
- approved-only: 21.3% (bootstrap 95% CI 9.0 to 34.4); n=6 events

### Hardy

Series: source: USGS DV 07069305 discharge; period 2001-10-01–2026-08-23; approved 99%, provisional from 2026-04-09

| event_date          |   post_bf_cfs |   post_p_in | matched_years   |   matched_bf_cfs |   matched_p_in |   diff_cfs |   diff_pct |
|:--------------------|--------------:|------------:|:----------------|-----------------:|---------------:|-----------:|-----------:|
| 2006-09-23 00:00:00 |        1196.1 |        28.3 | 2004,2015,2022  |            890.4 |           27.3 |      305.7 |       34.3 |
| 2008-03-19 00:00:00 |        1174.9 |        35.9 | 2002,2015,2019  |           1184.2 |           33   |       -9.3 |       -0.8 |
| 2009-10-30 00:00:00 |        1361.7 |        18.8 | 2023,2013,2014  |            842.1 |           19.7 |      519.6 |       61.7 |
| 2011-04-26 00:00:00 |         986.2 |        22.8 | 2004,2021,2022  |            702.3 |           23   |      283.8 |       40.4 |
| 2017-04-30 00:00:00 |         794.4 |        17.2 | 2022,2023,2021  |            669.9 |           20.5 |      124.5 |       18.6 |
| 2025-04-05 00:00:00 |        1160.5 |        29.9 | 2015,2020,2013  |            984.5 |           28.9 |      176   |       17.9 |

- mean post-flood base-flow difference: 28.7% (bootstrap 95% CI 12.5 to 45.4); n=6 events
- approved-only: 28.7% (bootstrap 95% CI 12.5 to 45.4); n=6 events

![postflood](../reports/figures/phase4_postflood.png)

## Limitations

- Regional-skew, datum and USGS rating-shift records remain unobtained; Q5 rests on IV-derived stage-at-flow only.
- Hardy series is WY 2002+ (n≤24); Mammoth Spring vent carries the 1981+ record.
- Q4 n equals the number of ≥16 ft events in the Hardy peak file; CI is a bootstrap on a handful of events.
- Basin precip is the 30 km West Plains PRISM buffer, not a dye-traced recharge polygon.
