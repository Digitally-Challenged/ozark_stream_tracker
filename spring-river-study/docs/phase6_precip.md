# Phase 6 — precipitation regime (Q3) — generated 2026-08-25

Series: USC00238880 West Plains COOP (1981-01-01–2026-08-24; COOP series 1981+ in this build — the ACIS cache is keyed on station id, so the 1948 request returned the cached 1981+ pull; a 1948 backfill needs a `refresh=True` pull), KUNO ASOS (1998-04-01–2026-08-23), PRISM 30 km basin mean (1981-01-01–2026-08-23).

## Station agreement on monthly totals (qa_report follow-up)

- KUNO vs USC00238880 monthly totals (months with ≥25 days at both stations): r=0.86, ratio COOP/KUNO=1.07, n=282 months (1998-04 to 2026-06). Daily r was 0.42 in qa_report; monthly aggregation removes the ~7 AM observation-day offset.

## USC00238880: index trends (Sen slope per decade, 95% CI; BH-adjusted p across 10 indices)

- series span (non-missing days): 1981-01-01–2026-08-24
- index years 1981–2025; years passing 90% coverage: 34
- no index passes BH at q=0.05

| index       |   n |   slope_per_decade |     lo |    hi |     z |     p |   p_bh | significant_bh   |
|:------------|----:|-------------------:|-------:|------:|------:|------:|-------:|:-----------------|
| total_in    |  34 |              0.758 | -1.66  | 3.5   | 0.741 | 0.459 |  0.742 | False            |
| recharge_in |  31 |              0.65  | -1.193 | 2.569 | 0.85  | 0.395 |  0.742 | False            |
| growing_in  |  34 |              0.9   | -0.681 | 2.683 | 1.097 | 0.273 |  0.742 | False            |
| days_ge_0p5 |  34 |              0.75  | -0.789 | 2.143 | 0.954 | 0.34  |  0.742 | False            |
| days_ge_1   |  34 |              0     | -0.769 | 1.25  | 0.374 | 0.709 |  0.787 | False            |
| days_ge_2   |  34 |              0     | -0.476 | 0.465 | 0     | 1     |  1     | False            |
| max1_in     |  34 |              0.2   | -0.097 | 0.494 | 1.187 | 0.235 |  0.742 | False            |
| max3_in     |  34 |              0.508 |  0.075 | 0.91  | 2.462 | 0.014 |  0.138 | False            |
| top5_frac   |  34 |              0.002 | -0.006 | 0.011 | 0.563 | 0.573 |  0.742 | False            |
| sdii_in     |  34 |              0.004 | -0.013 | 0.019 | 0.534 | 0.594 |  0.742 | False            |

## KUNO: index trends (Sen slope per decade, 95% CI; BH-adjusted p across 10 indices)

- series span (non-missing days): 1998-04-01–2026-08-23
- index years 1999–2025; years passing 90% coverage: 27
- BH-significant: sdii_in (+0.0634/decade, 95% CI 0.0337 to 0.09)

| index       |   n |   slope_per_decade |     lo |     hi |      z |     p |   p_bh | significant_bh   |
|:------------|----:|-------------------:|-------:|-------:|-------:|------:|-------:|:-----------------|
| total_in    |  27 |              4.279 | -0.539 | 10.261 |  1.709 | 0.087 |  0.218 | False            |
| recharge_in |  27 |              1.533 | -0.527 |  3.347 |  1.751 | 0.08  |  0.218 | False            |
| growing_in  |  27 |              3.4   | -1.017 |  7.131 |  1.584 | 0.113 |  0.226 | False            |
| days_ge_0p5 |  27 |              3.333 |  0     |  7.5   |  1.861 | 0.063 |  0.218 | False            |
| days_ge_1   |  27 |              1.429 | -0.769 |  3.158 |  1.3   | 0.194 |  0.277 | False            |
| days_ge_2   |  27 |              0.455 |  0     |  1.333 |  1.414 | 0.157 |  0.262 | False            |
| max1_in     |  27 |              0.25  | -0.2   |  0.75  |  1.209 | 0.227 |  0.283 | False            |
| max3_in     |  27 |              0.4   | -0.55  |  1.438 |  0.709 | 0.478 |  0.532 | False            |
| top5_frac   |  27 |             -0.003 | -0.024 |  0.019 | -0.208 | 0.835 |  0.835 | False            |
| sdii_in     |  27 |              0.063 |  0.034 |  0.09  |  3.377 | 0.001 |  0.007 | True             |

## basin: index trends (Sen slope per decade, 95% CI; BH-adjusted p across 10 indices)

- series span (non-missing days): 1981-01-01–2026-08-23
- index years 1981–2025; years passing 90% coverage: 45
- BH-significant: total_in (+2.41/decade, 95% CI 0.355 to 4.48), growing_in (+2.32/decade, 95% CI 0.898 to 3.76), days_ge_0p5 (+2.5/decade, 95% CI 1.11 to 4.29), days_ge_1 (+1.45/decade, 95% CI 0.714 to 2.26), days_ge_2 (+0.27/decade, 95% CI 0 to 0.588), max1_in (+0.28/decade, 95% CI 0.0967 to 0.529), max3_in (+0.283/decade, 95% CI 0.0432 to 0.653), top5_frac (+0.00756/decade, 95% CI 0.000256 to 0.0149), sdii_in (+0.0347/decade, 95% CI 0.0222 to 0.0488)

| index       |   n |   slope_per_decade |     lo |    hi |     z |     p |   p_bh | significant_bh   |
|:------------|----:|-------------------:|-------:|------:|------:|------:|-------:|:-----------------|
| total_in    |  45 |              2.409 |  0.355 | 4.483 | 2.279 | 0.023 |  0.028 | True             |
| recharge_in |  45 |              0.249 | -1.034 | 1.484 | 0.323 | 0.747 |  0.747 | False            |
| growing_in  |  45 |              2.316 |  0.898 | 3.758 | 3.121 | 0.002 |  0.005 | True             |
| days_ge_0p5 |  45 |              2.5   |  1.111 | 4.286 | 3.326 | 0.001 |  0.003 | True             |
| days_ge_1   |  45 |              1.446 |  0.714 | 2.258 | 3.332 | 0.001 |  0.003 | True             |
| days_ge_2   |  45 |              0.27  |  0     | 0.588 | 2.305 | 0.021 |  0.028 | True             |
| max1_in     |  45 |              0.28  |  0.097 | 0.529 | 2.886 | 0.004 |  0.008 | True             |
| max3_in     |  45 |              0.283 |  0.043 | 0.653 | 2.299 | 0.022 |  0.028 | True             |
| top5_frac   |  45 |              0.008 |  0     | 0.015 | 2.025 | 0.043 |  0.048 | True             |
| sdii_in     |  45 |              0.035 |  0.022 | 0.049 | 4.471 | 0     |  0     | True             |

## Station vs basin: reading the divergence

- BH-significant indices per series: USC00238880 0/10, KUNO 1/10, basin 9/10.
- USC00238880 years failing 90% coverage (excluded from its trend tests): 1997, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2019, 2020, 2021. The 2011–2021 hole removes most of the recent wet decade from the station test, so its null result is low power, not evidence against the basin trend.
- PRISM basin values are a 4 km grid mean over a ~60 × 60 km box around West Plains; station gaps enter PRISM only indirectly through its interpolation. Treat the basin trends as the Q3 headline and the station tests as a consistency check.

## Coupling: monthly basin precip → Mammoth Spring flow (anomaly correlation by lag)

Monthly anomalies (climatology removed; log flow), lags 0–12 months, 1000 12-month block-bootstrap resamples for the CI (0 s).

|   lag |      r |   r_lo |   r_hi |   n |
|------:|-------:|-------:|-------:|----:|
|     0 |  0.3   |  0.252 |  0.358 | 545 |
|     1 |  0.463 |  0.422 |  0.526 | 545 |
|     2 |  0.357 |  0.29  |  0.409 | 545 |
|     3 |  0.278 |  0.186 |  0.347 | 544 |
|     4 |  0.22  |  0.134 |  0.272 | 543 |
|     5 |  0.161 |  0.064 |  0.217 | 542 |
|     6 |  0.128 |  0.035 |  0.203 | 541 |
|     7 |  0.096 |  0.007 |  0.169 | 540 |
|     8 |  0.06  | -0.036 |  0.151 | 539 |
|     9 |  0.002 | -0.107 |  0.088 | 538 |
|    10 | -0.001 | -0.083 |  0.085 | 537 |
|    11 |  0.049 | -0.029 |  0.14  | 536 |
|    12 |  0.02  | -0.062 |  0.125 | 535 |

- response lag (max r): 1 months, r=0.46 (95% CI 0.42 to 0.53), n=545 months

![indices](../reports/figures/phase6_indices.png)

Figure: annual total, days ≥ 1 in, and max 1-day precip at USC00238880; source RCC-ACIS StnData, 1981-01-01–2026-08-24; years failing 90% coverage omitted.

![lag](../reports/figures/phase6_lag_correlation.png)

Figure: source: USGS DV 07069190 + PRISM 30 km basin mean; period 1981-02-25–2026-08-23; approved 99%, provisional from 2026-04-09.

## Limitations

- Station indices are point measurements; basin indices are a 4 km grid mean (smoother extremes by construction).
- COOP series 1981+ in this build (cache keyed on station id); the 1948–1980 record is not yet pulled, so the USC00238880 trend window matches KUNO/basin rather than extending it.
- USC00238880 has 32 gaps > 7 days (qa_report); years failing 90% coverage are NaN, not low. KUNO years before 1998 are NaN by coverage.
- Precip series carry no approval flag; the all/approved-only rule does not apply here. Mammoth flow used in coupling: source: USGS DV 07069190; period 1981-02-25–2026-08-23; approved 99%, provisional from 2026-04-09.
- Lag-correlation CI is a 12-month block bootstrap of the lagged pairs; it preserves within-year serial correlation but not dependence across block boundaries, so it is mildly optimistic.
