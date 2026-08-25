# Basin precipitation source comparison — generated 2026-08-25

Default source for this edition: `aorc`. Sources:

- `aorc`: NOAA AORC v1.1 1 km hourly basin mean over the MoDNR Mammoth Spring recharge polygon (~349 mi²), daily totals 24 h ending 12 UTC (1981-01-01–2026-01-01)
- `prism_polygon`: PRISM 4 km daily basin mean over the MoDNR Mammoth Spring recharge polygon (~349 mi²) (1981-01-01–2026-08-25)
- `prism_buffer`: PRISM 4 km daily mean over the legacy 30 km West Plains buffer bbox (first edition) (1981-01-01–2026-08-24)

Same code paths as Phases 4 and 6 (all-data variant). Q1 = OLS p_trailing coefficient, R², residual Sen trend; Q4 = mean 6-month post-flood base-flow difference vs matched controls; Q3 = Sen slope per decade with BH flag; coupling = monthly anomaly lag correlation with block-bootstrap CI.

| block      | metric                          | aorc                                 | prism_polygon                        | prism_buffer                          |
|:-----------|:--------------------------------|:-------------------------------------|:-------------------------------------|:--------------------------------------|
| q1_mammoth | p_trailing_in coef (log-cfs/in) | 0.0156 (0.0111 to 0.0201; n=42)      | 0.0139 (0.00912 to 0.0186; n=42)     | 0.013 (0.00893 to 0.0171; n=42)       |
| q1_mammoth | OLS R²                          | 0.577 (n=42)                         | 0.519 (n=42)                         | 0.446 (n=42)                          |
| q1_mammoth | residual trend (log-cfs/yr)     | -0.00126 (-0.00326 to 0.00122; n=42) | -0.00225 (-0.0048 to 0.000148; n=42) | -0.00222 (-0.00497 to 0.000453; n=42) |
| q4_mammoth | post-flood base-flow diff (%)   | 26 (15.7 to 41; n=6)                 | 24.7 (16.5 to 35.4; n=6)             | 27.5 (19.8 to 42; n=6)                |
| q1_hardy   | p_trailing_in coef (log-cfs/in) | 0.0231 (0.00876 to 0.0375; n=24)     | 0.0246 (0.00567 to 0.0435; n=24)     | 0.023 (0.00967 to 0.0363; n=24)       |
| q1_hardy   | OLS R²                          | 0.408 (n=24)                         | 0.553 (n=24)                         | 0.47 (n=24)                           |
| q1_hardy   | residual trend (log-cfs/yr)     | 0.0203 (0.00915 to 0.0291; n=24)     | 0.0103 (-0.00061 to 0.0191; n=24)    | 0.00676 (-0.00135 to 0.0195; n=24)    |
| q4_hardy   | post-flood base-flow diff (%)   | 30.7 (19.6 to 38.7; n=6)             | 32.9 (24 to 41.5; n=6)               | 22.9 (12.6 to 35.1; n=6)              |
| q3         | total_in slope/decade           | 0.96 (-1.25 to 3.12; n=45)           | 2.01 (-0.0612 to 4.2; n=45)          | 2.41 (0.355 to 4.46; n=45)            |
| q3         | total_in BH-significant         | no                                   | no                                   | yes                                   |
| q3         | recharge_in slope/decade        | -0.806 (-1.99 to 0.602; n=44)        | -0.282 (-1.51 to 1.04; n=44)         | -0.0177 (-1.27 to 1.19; n=44)         |
| q3         | recharge_in BH-significant      | no                                   | no                                   | no                                    |
| q3         | max1_in slope/decade            | 0.264 (0.0517 to 0.495; n=45)        | 0.28 (0.082 to 0.481; n=45)          | 0.28 (0.0967 to 0.528; n=45)          |
| q3         | max1_in BH-significant          | yes                                  | yes                                  | yes                                   |
| q3         | sdii_in slope/decade            | 0.0324 (0.0204 to 0.0461; n=45)      | 0.0217 (0.00838 to 0.0358; n=45)     | 0.0347 (0.0222 to 0.0486; n=45)       |
| q3         | sdii_in BH-significant          | yes                                  | yes                                  | yes                                   |
| coupling   | response lag (months)           | 1 (n=539)                            | 1 (n=545)                            | 1 (n=545)                             |
| coupling   | r at response lag               | 0.454 (0.412 to 0.519; n=539)        | 0.476 (0.437 to 0.54; n=545)         | 0.463 (0.422 to 0.526; n=545)         |

## Agreement between sources

| block     | metric                         | aorc vs prism_polygon   | prism_polygon vs prism_buffer   |
|:----------|:-------------------------------|:------------------------|:--------------------------------|
| agreement | daily_r                        | 0.955 (n=16433)         | 0.975 (n=16671)                 |
| agreement | annual_total_r                 | 0.966 (n=45)            | 0.984 (n=45)                    |
| agreement | annual_total_ratio             | 1.01 (n=45)             | 0.997 (n=45)                    |
| agreement | aorc mean annual (in)          | 47.5 (n=45)             | nan                             |
| agreement | prism_polygon mean annual (in) | 47.8 (n=45)             | 47.8 (n=45)                     |
| agreement | prism_buffer mean annual (in)  | nan                     | 47.7 (n=45)                     |

![sources](../reports/figures/precip_sources_annual.png)
