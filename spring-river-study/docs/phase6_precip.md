# Phase 6 — precipitation regime (Q3) — generated 2026-08-25

Series: USC00238880 West Plains COOP (1981-01-01–2026-08-24; the 1981+ pull, unchanged — the other phases read this cache), KUNO ASOS (1998-04-01–2026-08-23), USC00230127 Alton COOP (1981-01-01–2026-08-03), West Plains 1948– (1948-07-01–2026-08-23; COOP USC00238880 through 1998-03-31; KUNO ASOS from 1998-04-01 raised by the COOP/KUNO catch ratio 1.068 measured on 282 overlapping months, so the record is on the town gauge's level; no day borrowed between gauges; 10331 KUNO days and 43 days KUNO missed after 1998-04-01), basin = NOAA AORC v1.1 1 km hourly basin mean over the MoDNR Mammoth Spring recharge polygon (~349 mi²), daily totals 24 h ending 12 UTC (1981-01-02–2025-12-31).

## Station agreement on monthly totals (qa_report follow-up)

- KUNO vs USC00238880 monthly totals (months with ≥25 days at both stations): r=0.86, ratio COOP/KUNO=1.07, n=282 months (1998-04 to 2026-06). Daily r was 0.42 in qa_report; monthly aggregation removes the ~7 AM observation-day offset.

## USC00238880: index trends (Sen slope per decade, 95% CI; BH-adjusted p across 10 indices)

- series span (non-missing days): 1981-01-01–2026-08-24
- index years 1981–2025; years passing 90% coverage: 34
- no index passes BH at q=0.05

| index       |   n |   slope_per_decade |     lo |    hi |     z |     p |   p_bh | significant_bh   |
|:------------|----:|-------------------:|-------:|------:|------:|------:|-------:|:-----------------|
| total_in    |  34 |              0.758 | -1.667 | 3.5   | 0.741 | 0.459 |  0.801 | False            |
| recharge_in |  30 |              0.233 | -1.58  | 1.869 | 0.357 | 0.721 |  0.801 | False            |
| growing_in  |  34 |              0.9   | -0.767 | 2.683 | 1.097 | 0.273 |  0.801 | False            |
| days_ge_0p5 |  34 |              0.75  | -0.789 | 2.083 | 0.954 | 0.34  |  0.801 | False            |
| days_ge_1   |  34 |              0     | -0.769 | 1.212 | 0.374 | 0.709 |  0.801 | False            |
| days_ge_2   |  34 |              0     | -0.476 | 0.455 | 0     | 1     |  1     | False            |
| max1_in     |  34 |              0.2   | -0.1   | 0.494 | 1.187 | 0.235 |  0.801 | False            |
| max3_in     |  34 |              0.508 |  0.072 | 0.91  | 2.491 | 0.013 |  0.127 | False            |
| top5_frac   |  34 |              0.002 | -0.006 | 0.011 | 0.563 | 0.573 |  0.801 | False            |
| sdii_in     |  34 |              0.004 | -0.013 | 0.019 | 0.534 | 0.594 |  0.801 | False            |

## KUNO: index trends (Sen slope per decade, 95% CI; BH-adjusted p across 10 indices)

- series span (non-missing days): 1998-04-01–2026-08-23
- index years 1999–2025; years passing 90% coverage: 27
- BH-significant: sdii_in (+0.0634/decade, 95% CI 0.033 to 0.09, n=27 years)

| index       |   n |   slope_per_decade |     lo |     hi |      z |     p |   p_bh | significant_bh   |
|:------------|----:|-------------------:|-------:|-------:|-------:|------:|-------:|:-----------------|
| total_in    |  27 |              4.279 | -0.557 | 10.261 |  1.709 | 0.087 |  0.226 | False            |
| recharge_in |  27 |              1.518 | -0.596 |  3.347 |  1.626 | 0.104 |  0.226 | False            |
| growing_in  |  27 |              3.4   | -1.075 |  7.131 |  1.584 | 0.113 |  0.226 | False            |
| days_ge_0p5 |  27 |              3.333 |  0     |  7.5   |  1.861 | 0.063 |  0.226 | False            |
| days_ge_1   |  27 |              1.429 | -0.769 |  3.077 |  1.3   | 0.194 |  0.277 | False            |
| days_ge_2   |  27 |              0.455 |  0     |  1.25  |  1.414 | 0.157 |  0.262 | False            |
| max1_in     |  27 |              0.25  | -0.21  |  0.75  |  1.209 | 0.227 |  0.283 | False            |
| max3_in     |  27 |              0.4   | -0.562 |  1.437 |  0.709 | 0.478 |  0.532 | False            |
| top5_frac   |  27 |             -0.003 | -0.024 |  0.019 | -0.208 | 0.835 |  0.835 | False            |
| sdii_in     |  27 |              0.063 |  0.033 |  0.09  |  3.377 | 0.001 |  0.007 | True             |

## USC00230127: index trends (Sen slope per decade, 95% CI; BH-adjusted p across 10 indices)

- series span (non-missing days): 1981-01-01–2026-08-03
- index years 1982–2025; years passing 90% coverage: 24
- no index passes BH at q=0.05

| index       |   n |   slope_per_decade |     lo |    hi |      z |     p |   p_bh | significant_bh   |
|:------------|----:|-------------------:|-------:|------:|-------:|------:|-------:|:-----------------|
| total_in    |  24 |              2.169 | -2.128 | 6.6   |  1.067 | 0.286 |  0.515 | False            |
| recharge_in |  21 |              0.678 | -1.324 | 2.725 |  0.876 | 0.381 |  0.545 | False            |
| growing_in  |  24 |              1.595 | -1.336 | 4.354 |  1.215 | 0.224 |  0.515 | False            |
| days_ge_0p5 |  24 |              0.801 | -1.538 | 3.478 |  0.774 | 0.439 |  0.549 | False            |
| days_ge_1   |  24 |              1.25  | -0.769 | 3.333 |  1.076 | 0.282 |  0.515 | False            |
| days_ge_2   |  24 |              0     | -0.455 | 0.667 |  0.484 | 0.628 |  0.691 | False            |
| max1_in     |  24 |              0.066 | -0.485 | 0.489 |  0.397 | 0.691 |  0.691 | False            |
| max3_in     |  24 |              0.412 | -0.25  | 1.076 |  1.364 | 0.172 |  0.515 | False            |
| top5_frac   |  24 |             -0.011 | -0.027 | 0.01  | -1.116 | 0.264 |  0.515 | False            |
| sdii_in     |  24 |              0.022 | -0.027 | 0.07  |  1.017 | 0.309 |  0.515 | False            |

## West Plains 1948–: index trends (Sen slope per decade, 95% CI; BH-adjusted p across 10 indices)

- series span (non-missing days): 1948-07-01–2026-08-23
- index years 1949–2025; years passing 90% coverage: 76
- BH-significant: days_ge_1 (+0.703/decade, 95% CI 0.256 to 1.15, n=76 years)

| index       |   n |   slope_per_decade |     lo |    hi |      z |     p |   p_bh | significant_bh   |
|:------------|----:|-------------------:|-------:|------:|-------:|------:|-------:|:-----------------|
| total_in    |  76 |              1.261 |  0.282 | 2.343 |  2.471 | 0.013 |  0.067 | False            |
| recharge_in |  74 |              0.566 | -0.062 | 1.08  |  1.731 | 0.083 |  0.167 | False            |
| growing_in  |  76 |              0.619 | -0.051 | 1.307 |  1.825 | 0.068 |  0.167 | False            |
| days_ge_0p5 |  76 |              0.818 |  0     | 1.525 |  2.183 | 0.029 |  0.097 | False            |
| days_ge_1   |  76 |              0.703 |  0.256 | 1.154 |  3.146 | 0.002 |  0.017 | True             |
| days_ge_2   |  76 |              0     |  0     | 0.323 |  1.581 | 0.114 |  0.19  | False            |
| max1_in     |  76 |              0.033 | -0.085 | 0.149 |  0.529 | 0.597 |  0.597 | False            |
| max3_in     |  76 |              0.065 | -0.105 | 0.235 |  0.789 | 0.43  |  0.537 | False            |
| top5_frac   |  76 |             -0.003 | -0.007 | 0.001 | -1.395 | 0.163 |  0.233 | False            |
| sdii_in     |  76 |              0.003 | -0.005 | 0.01  |  0.637 | 0.524 |  0.582 | False            |

## basin: index trends (Sen slope per decade, 95% CI; BH-adjusted p across 10 indices)

- series span (non-missing days): 1981-01-02–2025-12-31
- index years 1981–2025; years passing 90% coverage: 45
- BH-significant: growing_in (+1.46/decade, 95% CI 0.207 to 2.9, n=45 years), days_ge_1 (+1.38/decade, 95% CI 0.488 to 2.22, n=45 years), days_ge_2 (+0.286/decade, 95% CI -0 to 0.625, n=45 years), max1_in (+0.264/decade, 95% CI 0.0517 to 0.495, n=45 years), top5_frac (+0.00988/decade, 95% CI 0.00264 to 0.0177, n=45 years), sdii_in (+0.0324/decade, 95% CI 0.0204 to 0.0461, n=45 years)

| index       |   n |   slope_per_decade |     lo |    hi |      z |     p |   p_bh | significant_bh   |
|:------------|----:|-------------------:|-------:|------:|-------:|------:|-------:|:-----------------|
| total_in    |  45 |              0.96  | -1.25  | 3.124 |  0.851 | 0.395 |  0.395 | False            |
| recharge_in |  44 |             -0.806 | -1.993 | 0.602 | -1.163 | 0.245 |  0.306 | False            |
| growing_in  |  45 |              1.464 |  0.207 | 2.898 |  2.181 | 0.029 |  0.049 | True             |
| days_ge_0p5 |  45 |              1.745 |  0     | 3.333 |  2.049 | 0.04  |  0.058 | False            |
| days_ge_1   |  45 |              1.379 |  0.488 | 2.222 |  2.947 | 0.003 |  0.016 | True             |
| days_ge_2   |  45 |              0.286 |  0     | 0.625 |  2.181 | 0.029 |  0.049 | True             |
| max1_in     |  45 |              0.264 |  0.052 | 0.495 |  2.358 | 0.018 |  0.046 | True             |
| max3_in     |  45 |              0.147 | -0.12  | 0.534 |  1.086 | 0.278 |  0.308 | False            |
| top5_frac   |  45 |              0.01  |  0.003 | 0.018 |  2.514 | 0.012 |  0.04  | True             |
| sdii_in     |  45 |              0.032 |  0.02  | 0.046 |  4.373 | 0     |  0     | True             |

## Station vs basin: reading the divergence

- BH-significant indices per series: USC00238880 0/10, KUNO 1/10, USC00230127 0/10, West Plains 1948– 1/10, basin 6/10.
- USC00238880 years failing 90% coverage (excluded from its trend tests): 1997, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2019, 2020, 2021. The 2011–2021 hole removes most of the recent wet decade from the station test, so its null result is low power, not evidence against the basin trend.
- `recharge_in` uses a stricter gate than the other indices: coverage is judged against the full Sep (year-1)–Feb (year) calendar season, so it is NaN for any year whose season straddles a series start or a gap (e.g. a series beginning 1 Jan has no recharge value for its first year). Its n can therefore be smaller than the other indices' n for the same series, never larger.
- Basin values are NOAA AORC v1.1 1 km hourly basin mean over the MoDNR Mammoth Spring recharge polygon (~349 mi²), daily totals 24 h ending 12 UTC; station gaps enter a gridded product only through its gauge blending. Treat the basin trends as the Q3 headline and the station tests as a consistency check.
- USC00230127 (Alton) has no data 1983–1994 and 2012–2016; 24 years pass the 90 % coverage gate, so its trend test is a consistency check only.
- **West Plains 1948–**: two instruments, one at a time — USC00238880 daily values through 1998-03-31, then the KUNO ASOS (West Plains Municipal Airport, 10.7 mi north of and 120 ft above the town gauge) from 1998-04-01, raised by the measured COOP/KUNO catch ratio 1.068. The two gauges differ systematically by ~7 % on monthly totals, so the airport values are put on the town gauge's level rather than left as a step at 1998-04-01. **No day is borrowed between gauges**: a day the period's own instrument missed stays NaN, its year still judged on coverage; nothing is interpolated. Taking KUNO from 1998 closes the 2011–2021 volunteer-absence hole: 76 years pass the 90 % coverage gate, against 34 for USC00238880 alone, 27 for KUNO and 24 for USC00230127. It is the highest-power station test in the study. Its result, not the gap-ridden COOP null, is the station-level check on the basin trends.
- Reading the West Plains 1948–, from its numbers: over the 76 complete years (1949–2025) the BH-significant indices are days_ge_1, while the intensity indices (max1_in, max3_in, sdii_in, top5_frac) have CIs spanning zero. With the coverage problem removed, the gauge does not reproduce the basin series' apparent intensification. Phase 8 (below) tests the two candidate explanations and rejects the point-vs-areal / record-length one: the gauge fails to corroborate over AORC's *identical* window too, and the basin indices step at the 2002 radar onset rather than trending. The parsimonious reading is that the intensification is in the product.

## Q3 step test: is the AORC intensity signal a trend or a 2002 product change?

AORC v1.1 gains radar (Stage IV/MRMS) input at 2002. A monotone trend test cannot distinguish a trend from a step at a known input change, so the basin indices are refitted as OLS index ~ year + I(year ≥ 2002) with HC3 errors. `slope_per_decade` is the trend that survives once the step is allowed for.

| index       |   n |   slope_per_decade |   slope_lo_per_decade |   slope_hi_per_decade |   slope_p |   step |   step_lo |   step_hi |   step_p |   step_p_bh | step_significant_bh   |
|:------------|----:|-------------------:|----------------------:|----------------------:|----------:|-------:|----------:|----------:|---------:|------------:|:----------------------|
| total_in    |  45 |            -2.1171 |               -5.5151 |                1.2808 |    0.222  | 9.3359 |    0.2873 |   18.3844 |   0.0432 |      0.1079 | False                 |
| recharge_in |  44 |            -2.0867 |               -4.583  |                0.4095 |    0.1013 | 3.6132 |   -2.5398 |    9.7663 |   0.2498 |      0.2715 | False                 |
| growing_in  |  45 |             0.0484 |               -2.7321 |                2.829  |    0.9728 | 5.5343 |   -2.8468 |   13.9153 |   0.1956 |      0.2445 | False                 |
| days_ge_0p5 |  45 |             0.1901 |               -2.1358 |                2.516  |    0.8727 | 4.6616 |   -1.0429 |   10.366  |   0.1092 |      0.1733 | False                 |
| days_ge_1   |  45 |            -0.9323 |               -2.3669 |                0.5023 |    0.2028 | 6.8953 |    3.1555 |   10.635  |   0.0003 |      0.003  | True                  |
| days_ge_2   |  45 |            -0.4323 |               -1.0615 |                0.1969 |    0.1781 | 2.4727 |    0.6901 |    4.2552 |   0.0066 |      0.0218 | True                  |
| max1_in     |  45 |            -0.0225 |               -0.48   |                0.435  |    0.9231 | 0.8597 |   -0.2244 |    1.9437 |   0.1201 |      0.1733 | False                 |
| max3_in     |  45 |            -0.0902 |               -0.9041 |                0.7236 |    0.8279 | 1.0786 |   -0.844  |    3.0012 |   0.2715 |      0.2715 | False                 |
| top5_frac   |  45 |             0.0034 |               -0.0089 |                0.0158 |    0.5876 | 0.022  |   -0.0058 |    0.0498 |   0.1213 |      0.1733 | False                 |
| sdii_in     |  45 |            -0.0022 |               -0.0272 |                0.0227 |    0.8604 | 0.1137 |    0.0462 |    0.1813 |   0.001  |      0.0048 | True                  |

- storm-sharpness indices with a significant step at 2002: sdii_in, days_ge_1; with a residual trend CI spanning zero: sdii_in, days_ge_1, max1_in of 3 tested.
- within-era Sen slopes: 0 of 6 sharpness-index/era combinations have a CI excluding zero on the rising side.

### Within-era Sen slopes (per decade)

| era       | index       |   n |   slope_per_decade |      lo |     hi |     p |
|:----------|:------------|----:|-------------------:|--------:|-------:|------:|
| 1981–2001 | total_in    |  21 |             -3.945 | -10.485 |  3.439 | 0.349 |
| 1981–2001 | recharge_in |  20 |             -2.258 |  -7.262 |  3.311 | 0.315 |
| 1981–2001 | growing_in  |  21 |             -1.066 |  -3.366 |  1.38  | 0.526 |
| 1981–2001 | days_ge_0p5 |  21 |             -0     |  -5     |  5     | 1     |
| 1981–2001 | days_ge_1   |  21 |             -0     |  -2.5   |  2.632 | 0.855 |
| 1981–2001 | days_ge_2   |  21 |             -0     |  -0     |  0.556 | 0.922 |
| 1981–2001 | max1_in     |  21 |              0.071 |  -0.694 |  0.672 | 0.786 |
| 1981–2001 | max3_in     |  21 |             -0.099 |  -0.702 |  0.751 | 0.833 |
| 1981–2001 | top5_frac   |  21 |              0.02  |  -0.007 |  0.046 | 0.124 |
| 1981–2001 | sdii_in     |  21 |              0.008 |  -0.025 |  0.042 | 0.695 |
| 2002–2025 | total_in    |  24 |             -1.584 |  -7.618 |  4.95  | 0.568 |
| 2002–2025 | recharge_in |  24 |             -1.32  |  -4.99  |  1.853 | 0.413 |
| 2002–2025 | growing_in  |  24 |              1.229 |  -4.539 |  5.28  | 0.747 |
| 2002–2025 | days_ge_0p5 |  24 |             -0     |  -3.636 |  5     | 1     |
| 2002–2025 | days_ge_1   |  24 |             -1.348 |  -4     |  0.769 | 0.185 |
| 2002–2025 | days_ge_2   |  24 |             -0     |  -1.667 | -0     | 0.243 |
| 2002–2025 | max1_in     |  24 |             -0.057 |  -0.613 |  0.675 | 0.862 |
| 2002–2025 | max3_in     |  24 |             -0.291 |  -0.911 |  0.999 | 0.503 |
| 2002–2025 | top5_frac   |  24 |             -0.012 |  -0.027 |  0.006 | 0.224 |
| 2002–2025 | sdii_in     |  24 |             -0.007 |  -0.051 |  0.034 | 0.637 |

### Pre/post-2002 means: AORC vs the gauge over identical years

Both series restricted to the calendar years both cover, so this is not a comparison of different periods. If the change were meteorological the two products would move together; if it is a change in the product's inputs, only the gridded series moves.

| series            | index       |   n_pre |   n_post |   pre_mean |   post_mean |   pct_change |
|:------------------|:------------|--------:|---------:|-----------:|------------:|-------------:|
| AORC basin        | total_in    |      20 |       24 |     45.459 |      49.666 |        9.256 |
| AORC basin        | recharge_in |      19 |       24 |     22.412 |      21.697 |       -3.188 |
| AORC basin        | growing_in  |      20 |       24 |     22.665 |      28.227 |       24.539 |
| AORC basin        | days_ge_0p5 |      20 |       24 |     28     |      32.708 |       16.815 |
| AORC basin        | days_ge_1   |      20 |       24 |      8.15  |      12.75  |       56.442 |
| AORC basin        | days_ge_2   |      20 |       24 |      1     |       2.5   |      150     |
| AORC basin        | max1_in     |      20 |       24 |      2.427 |       3.263 |       34.456 |
| AORC basin        | max3_in     |      20 |       24 |      3.822 |       4.687 |       22.624 |
| AORC basin        | top5_frac   |      20 |       24 |      0.192 |       0.223 |       16.131 |
| AORC basin        | sdii_in     |      20 |       24 |      0.294 |       0.4   |       35.89  |
| West Plains 1948– | total_in    |      20 |       24 |     45.75  |      50.578 |       10.553 |
| West Plains 1948– | recharge_in |      18 |       24 |     22.292 |      21.062 |       -5.517 |
| West Plains 1948– | growing_in  |      20 |       24 |     23.188 |      29.583 |       27.577 |
| West Plains 1948– | days_ge_0p5 |      20 |       24 |     30.65  |      33.542 |        9.434 |
| West Plains 1948– | days_ge_1   |      20 |       24 |     13.5   |      15.958 |       18.21  |
| West Plains 1948– | days_ge_2   |      20 |       24 |      3.05  |       3.75  |       22.951 |
| West Plains 1948– | max1_in     |      20 |       24 |      3.179 |       3.69  |       16.057 |
| West Plains 1948– | max3_in     |      20 |       24 |      4.123 |       5.385 |       30.625 |
| West Plains 1948– | top5_frac   |      20 |       24 |      0.251 |       0.247 |       -1.737 |
| West Plains 1948– | sdii_in     |      20 |       24 |      0.431 |       0.437 |        1.358 |

### Family-wise count (max-T permutation)

Year labels permuted jointly across the 10 indices (5000 draws, seed 0), so the null preserves the correlation between them that a per-index BH correction ignores.

| index       |   abs_z |   p_maxt | survives   |
|:------------|--------:|---------:|:-----------|
| total_in    |  0.8511 |   0.959  | False      |
| recharge_in |  1.1631 |   0.8146 | False      |
| growing_in  |  2.1815 |   0.1706 | False      |
| days_ge_0p5 |  2.0495 |   0.2222 | False      |
| days_ge_1   |  2.9469 |   0.0174 | True       |
| days_ge_2   |  2.1812 |   0.1712 | False      |
| max1_in     |  2.3575 |   0.1098 | False      |
| max3_in     |  1.0858 |   0.8564 | False      |
| top5_frac   |  2.5141 |   0.0784 | False      |
| sdii_in     |  4.3727 |   0.0002 | True       |

- indices surviving max-T: 2/10 vs 6/10 under BH. Subordinate to the step test above: under it none of these is a trend.

### West Plains 1948– catch-ratio sensitivity and the 1998 splice

The whole KUNO era is scaled by one constant measured on the period it is applied to, so any error in it maps one-for-one into the trend. Which indices pass BH at each ratio:

- catch ratio 1.000: no index passes BH at q=0.05
- catch ratio 1.034: no index passes BH at q=0.05
- catch ratio 1.068: days_ge_1
- catch ratio 1.100: total_in, days_ge_1

A residual step term at the 1998 instrument change (OLS index ~ year + I(year ≥ 1998), HC3) on the ratio-adjusted record:

| index       |   n |   slope_per_decade |   slope_lo_per_decade |   slope_hi_per_decade |   slope_p |    step |   step_lo |   step_hi |   step_p |   step_p_bh | step_significant_bh   |
|:------------|----:|-------------------:|----------------------:|----------------------:|----------:|--------:|----------:|----------:|---------:|------------:|:----------------------|
| total_in    |  76 |             1.7203 |               -0.0597 |                3.5002 |    0.0582 | -2.6911 |  -10.5059 |    5.1238 |   0.4997 |      0.7058 | False                 |
| recharge_in |  74 |             1.3744 |                0.2596 |                2.4892 |    0.0157 | -5.1562 |  -10.141  |   -0.1713 |   0.0426 |      0.2209 | False                 |
| growing_in  |  76 |             0.4375 |               -0.6405 |                1.5154 |    0.4264 |  2.0953 |   -3.3008 |    7.4915 |   0.4466 |      0.7058 | False                 |
| days_ge_0p5 |  76 |             1.0848 |               -0.3003 |                2.4699 |    0.1248 | -1.6652 |   -7.3316 |    4.0011 |   0.5646 |      0.7058 | False                 |
| days_ge_1   |  76 |             0.8484 |                0.0821 |                1.6146 |    0.03   | -0.5824 |   -4.0405 |    2.8757 |   0.7413 |      0.7413 | False                 |
| days_ge_2   |  76 |             0.2536 |               -0.0549 |                0.5622 |    0.1071 | -0.4624 |   -1.9702 |    1.0454 |   0.5478 |      0.7058 | False                 |
| max1_in     |  76 |             0.1088 |               -0.0935 |                0.311  |    0.2919 | -0.2157 |   -1.111  |    0.6796 |   0.6368 |      0.7075 | False                 |
| max3_in     |  76 |             0.0126 |               -0.3196 |                0.3448 |    0.9409 |  0.6645 |   -0.7618 |    2.0907 |   0.3612 |      0.7058 | False                 |
| top5_frac   |  76 |            -0.0049 |               -0.0114 |                0.0016 |    0.1399 |  0.0089 |   -0.0194 |    0.0372 |   0.5371 |      0.7058 | False                 |
| sdii_in     |  76 |             0.0137 |                0.0005 |                0.0268 |    0.0418 | -0.0557 |   -0.11   |   -0.0015 |   0.0442 |      0.2209 | False                 |

- indices with a significant 1998 step: recharge_in, sdii_in — the mean ratio does not fully homogenise the splice (KUNO's tipping bucket counts more small events than a volunteer observer, deflating KUNO-era SDII).
- indices whose trend the pooled fit suppresses (slope p<0.05 with the step, not BH-significant without): recharge_in, sdii_in.
- the COOP-only era (1949–1997) is the homogeneous baseline; no ratio is applied to it.

### Q3 reading

Thesis, from the three tables above:

1. **Totals are not rising.** Annual and Sep–Feb recharge-season totals have CIs spanning zero on every series and are unaffected by the step term. This is the most robust Q3 result and the only one to state without qualification.
2. **The AORC sharpness indices step at 2002 and trend flat-to-negative within each era.** The apparent intensification coincides with the documented change in the product's inputs, not with a change in the weather: over identical years the gridded SDII and days ≥ 1 in rise sharply while the co-located gauge barely moves, and the two products nevertheless agree on how much rain fell.
3. **No intensification is detectable at the gauge**, over its full 1949–2025 record or over AORC's own identical window; what significance there is rests on a knife-edge catch ratio.
4. PRISM over the same polygon shares Stage IV/MRMS and gauge inputs with AORC and is not an independent witness. The correct statement is that **no intensification is detectable over the recharge area once the product discontinuity is allowed for** — not that the basin became more intense.

## Buffer vs polygon: was the first edition's rise a property of the geometry?

- annual totals of the two geometries correlate r=0.984 (n=45 years).
- trend of the buffer−polygon difference: Sen slope 0.0272 in/yr (95% CI -0.0091 to 0.0678); MK z=1.52, p=0.129; n=45.

The difference series has no detectable trend, so the geometries do not differ detectably in how their totals evolve. The first edition's significant annual-total rise and this edition's null are the same estimate either side of a p-value threshold — a threshold crossing, not an attribution to the 30 km buffer. Both geometries give a positive annual-total slope that is not separable from zero at this n.

## Coupling: monthly basin precip → Mammoth Spring flow (anomaly correlation by lag)

Monthly anomalies (climatology removed; log flow), lags 0–12 months, 1000 12-month block-bootstrap resamples for the CI (both variants, 1 s). Table: all data.

|   lag |     r |   r_lo |   r_hi |   n |
|------:|------:|-------:|-------:|----:|
|     0 | 0.288 |  0.237 |  0.344 | 538 |
|     1 | 0.454 |  0.412 |  0.519 | 539 |
|     2 | 0.34  |  0.274 |  0.397 | 540 |
|     3 | 0.267 |  0.18  |  0.329 | 540 |
|     4 | 0.209 |  0.133 |  0.256 | 540 |
|     5 | 0.152 |  0.061 |  0.203 | 540 |
|     6 | 0.14  |  0.05  |  0.199 | 540 |
|     7 | 0.101 |  0.021 |  0.166 | 540 |
|     8 | 0.062 | -0.029 |  0.145 | 539 |
|     9 | 0.015 | -0.087 |  0.094 | 538 |
|    10 | 0.007 | -0.068 |  0.087 | 537 |
|    11 | 0.047 | -0.033 |  0.132 | 536 |
|    12 | 0.009 | -0.08  |  0.108 | 535 |

- response lag (max r): 1 months, r=0.45 (95% CI 0.41 to 0.52), n=539 months

### Sensitivity: all vs approved-only Mammoth flow

- response lag (all data): 1 months, r=0.45 (95% CI 0.41 to 0.52), n=539 months
- response lag (approved-only flow): 1 months, r=0.45 (95% CI 0.41 to 0.52), n=539 months
- unchanged: same response lag and overlapping r CIs.

## Coupling at daily resolution (what the 1-month lag actually means)

The monthly analysis above bins to calendar months, so its lag-1 maximum is the coarsest bin that contains both a fast onset and a long tail. At daily resolution (day-of-year climatology removed from both series):

- peak cross-correlation at **2 day(s)** after the rain (r=0.140, n=16,381 days).
- beyond the peak the correlation decays monotonically to within sampling noise (largest single-day rise +0.0006 in an r of 0.14), out to 60 days — **no local maximum near 30 days**.
- Report both: **onset within days; monthly correlation maximised at lag 1 month.** The monthly figure is a statistic about binned anomalies, not an aquifer transit time.

|   lag_days |      r |     n |
|-----------:|-------:|------:|
|          0 | 0.0983 | 16379 |
|          1 | 0.1348 | 16380 |
|          2 | 0.1399 | 16381 |
|          3 | 0.1391 | 16382 |
|          4 | 0.1374 | 16383 |
|          5 | 0.1357 | 16384 |
|          6 | 0.1341 | 16385 |
|          7 | 0.1318 | 16386 |
|          8 | 0.1293 | 16387 |
|          9 | 0.1268 | 16388 |
|         10 | 0.1238 | 16389 |
|         11 | 0.1231 | 16390 |
|         12 | 0.1221 | 16391 |
|         13 | 0.1205 | 16392 |
|         14 | 0.1193 | 16393 |
|         15 | 0.1182 | 16394 |
|         16 | 0.1172 | 16395 |
|         17 | 0.1162 | 16396 |
|         18 | 0.1138 | 16397 |
|         19 | 0.1119 | 16398 |
|         20 | 0.1093 | 16399 |
|         21 | 0.1082 | 16400 |
|         22 | 0.1087 | 16401 |
|         23 | 0.1082 | 16402 |
|         24 | 0.1066 | 16403 |
|         25 | 0.1046 | 16404 |
|         26 | 0.1025 | 16405 |
|         27 | 0.1014 | 16406 |
|         28 | 0.0997 | 16407 |
|         29 | 0.0982 | 16408 |
|         30 | 0.0973 | 16409 |
|         31 | 0.0961 | 16410 |
|         32 | 0.0924 | 16411 |
|         33 | 0.0897 | 16412 |
|         34 | 0.0886 | 16413 |
|         35 | 0.088  | 16414 |
|         36 | 0.0877 | 16415 |
|         37 | 0.0875 | 16416 |
|         38 | 0.0858 | 16417 |
|         39 | 0.0854 | 16418 |
|         40 | 0.0848 | 16419 |
|         41 | 0.0838 | 16420 |
|         42 | 0.0822 | 16421 |
|         43 | 0.081  | 16422 |
|         44 | 0.0816 | 16423 |
|         45 | 0.0811 | 16424 |
|         46 | 0.0803 | 16425 |
|         47 | 0.0796 | 16426 |
|         48 | 0.0784 | 16427 |
|         49 | 0.0776 | 16428 |
|         50 | 0.0777 | 16429 |
|         51 | 0.0772 | 16430 |
|         52 | 0.0775 | 16431 |
|         53 | 0.077  | 16432 |
|         54 | 0.0756 | 16433 |
|         55 | 0.0752 | 16433 |
|         56 | 0.075  | 16433 |
|         57 | 0.0736 | 16433 |
|         58 | 0.0722 | 16433 |
|         59 | 0.0709 | 16433 |
|         60 | 0.0699 | 16433 |

![indices](../reports/figures/phase6_indices.png)

Figure: annual total, days ≥ 1 in, and max 1-day precip at USC00238880; source RCC-ACIS StnData; period 1981-01-01–2026-08-24; years with <90% daily coverage omitted; approval N/A — station precip carries no approval flag.

![lag](../reports/figures/phase6_lag_correlation.png)

Figure: source: USGS DV 07069190 + NOAA AORC v1.1 1 km hourly basin mean over the MoDNR Mammoth Spring recharge polygon (~349 mi²), daily totals 24 h ending 12 UTC; period 1981-02-25–2026-08-23; approved 99%, provisional from 2026-04-09.

## Limitations

- Station indices are point measurements; basin indices are a gridded areal mean (NOAA AORC v1.1 1 km hourly basin mean over the MoDNR Mammoth Spring recharge polygon (~349 mi²), daily totals 24 h ending 12 UTC) — smoother extremes by construction.
- The USC00238880 series used for the station trend above is the 1981+ pull, so its window matches KUNO/basin. The 1948–1980 record **is** now pulled (separate `_1948` cache) but feeds only the West Plains 1948–; the 1981+ COOP series the other analyses read is unchanged.
- USC00238880 has 32 gaps > 7 days (qa_report); years failing 90% coverage are NaN, not low. KUNO years before 1998 are NaN by coverage.
- Precip series carry no approval flag; the all/approved-only rule does not apply to the index trends. It does apply to the coupling (Mammoth flow carries flags) and is reported above. Mammoth flow used in coupling: source: USGS DV 07069190; period 1981-02-25–2026-08-23; approved 99%, provisional from 2026-04-09.
- Lag-correlation CI is a 12-month block bootstrap of the lagged pairs; it preserves within-year serial correlation but not dependence across block boundaries, so it is mildly optimistic.
- **AORC has no radar input before 2002.** Its storm-sharpness indices step at that date; the step test above, not the monotone trend test, is the Q3 headline. PRISM over the same polygon shares Stage IV/MRMS and gauge inputs and is not an independent witness. Settling this needs NOAA's AORC v1.1 homogeneity documentation, a one-cell AORC re-pull at the gauge coordinate (the cache keeps only the polygon mean), or an independent grid with no 2002 input change (nClimGrid-Daily, Livneh).
- The West Plains 1948– record's KUNO era rests on one catch ratio measured on the period it is applied to; the sensitivity above shows which results survive which ratio. A quantile (wet-day-frequency) matching between COOP and KUNO over the overlapping months, with the adjustment uncertainty propagated into the trend CI, would replace it.
- The daily cross-correlation removes a day-of-year climatology estimated from the same record, and its r values carry no CI; it is reported to locate the onset, not to size the coupling.
