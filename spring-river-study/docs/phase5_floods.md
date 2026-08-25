# Phase 5 — floods (Q2, Q6, Q7, Q8) — generated 2026-08-25

## Q8 LP3 flood frequency (nonparametric bootstrap, 5–95%)

Regional skew -0.2 (approximate, see config); the 'station skew only' block is the sensitivity case. LP3 by method of moments with B17-weighted skew; the Grubbs-Beck low-outlier screen flags but does not drop (all peaks retained in the fit); nonparametric bootstrap (resampled peaks), 5–95%, 2000 resamples. Not EMA.

### Hardy (n=24, WY 2002–2025, station skew -0.16, weighted skew -0.18; low outliers flagged below 2969 cfs: 0 (retained; no B17B conditional-probability adjustment applied))

|   return_period |   q_cfs |   q_lo |   q_hi |
|----------------:|--------:|-------:|-------:|
|            1.25 |   11288 |   8480 |  15771 |
|            2    |   22807 |  17174 |  30208 |
|            5    |   44552 |  32553 |  57205 |
|           10    |   62391 |  44282 |  79486 |
|           25    |   88469 |  60333 | 114284 |
|           50    |  110266 |  73308 | 144373 |
|          100    |  133946 |  87021 | 179736 |

### Hardy — station skew only (n=24, WY 2002–2025, station skew -0.16, weighted skew -0.16; low outliers flagged below 2969 cfs: 0 (retained; no B17B conditional-probability adjustment applied))

|   return_period |   q_cfs |   q_lo |   q_hi |
|----------------:|--------:|-------:|-------:|
|            1.25 |   11278 |   8442 |  15858 |
|            2    |   22752 |  16878 |  30763 |
|            5    |   44528 |  32251 |  57227 |
|           10    |   62503 |  44495 |  78684 |
|           25    |   88936 |  60880 | 113279 |
|           50    |  111155 |  74237 | 145558 |
|          100    |  135408 |  87296 | 184185 |

### Imboden (n=89, WY 1937–2025, station skew -0.18, weighted skew -0.18; low outliers flagged below 2724 cfs: 1 (retained; no B17B conditional-probability adjustment applied))

|   return_period |   q_cfs |   q_lo |   q_hi |
|----------------:|--------:|-------:|-------:|
|            1.25 |   14186 |  12133 |  16903 |
|            2    |   27522 |  23910 |  31286 |
|            5    |   51677 |  43616 |  59601 |
|           10    |   70918 |  58308 |  84761 |
|           25    |   98446 |  76431 | 124449 |
|           50    |  121050 |  89488 | 161724 |
|          100    |  145282 | 101403 | 205995 |

### Stage thresholds at Hardy

Stage→flow from the 24 annual-peak (stage, flow) pairs: log10 Q = 1.954 + 2.215·log10 H (R²=0.991). NWS categories: action 8, minor 10, moderate 14, major 16 ft.

|   stage_ft |   flow_cfs |   lp3_return_period_yr |   empirical_exceedances_2002_2025 | empirical_return_period_yr   |   nws_crests_ge_stage_1982_2025 |
|-----------:|-----------:|-----------------------:|----------------------------------:|:-----------------------------|--------------------------------:|
|          8 |       9001 |                    1.2 |                                22 | 1.1                          |                              21 |
|         10 |      14756 |                    1.4 |                                16 | 1.5                          |                              20 |
|         14 |      31093 |                    2.9 |                                 9 | 2.7                          |                              11 |
|         16 |      41795 |                    4.5 |                                 6 | 4.0                          |                               8 |
|         20 |      68516 |                   12.5 |                                 3 | 8.0                          |                               5 |
|         23 |      93380 |                   29.4 |                                 0 | >1000                        |                               1 |

NWS crest count includes the 1982-12-03 29.0 ft record; the Hardy systematic record is WY 2002+. Empirical return period = n_years / exceedances of the annual-peak stage.

### Sensitivity: the 1982 crest as historical information

The 1982-12-03 29.0 ft crest is known but sits outside the systematic record (Hardy WY 2002+). By the annual-peak log-log relation it is ≈156,047 cfs. Leaving a known extreme out biases the return periods of the major-exposure tier long, so it is added back by Bulletin 17B historical weighting (W = (H−Z)/(n−s); peaks at or above the threshold keep weight 1). Historical period H = 44 yr (1982–2025) and 90 yr (back to the long record's start).

| case                           | historical_period_yr   |   n_effective |   weighted_skew |   rp_16ft_yr |   rp_20ft_yr |   rp_23ft_yr |
|:-------------------------------|:-----------------------|--------------:|----------------:|-------------:|-------------:|-------------:|
| systematic only (headline fit) | <NA>                   |            24 |          -0.175 |          4.5 |         12.5 |         29.4 |
| with 1982 crest, H=44 yr       | 44                     |            44 |          -0.056 |          4   |          9.9 |         20.1 |
| with 1982 crest, H=90 yr       | 90                     |            90 |          -0.089 |          4.3 |         11.3 |         24.5 |

- **This is the headline sensitivity for Q8.** Across the cases, 20 ft is 10–13 yr and 23 ft is 20–29 yr; the systematic-only point estimates are biased long by roughly 20–30 % at these stages. They remain inside the bootstrap 5–95 % band, so the published figures are not refuted — but 23 ft should be quoted as **20–29 yr**, not as a single number.
- The station-vs-regional-skew case (reported above) moves 23 ft by well under a year: it tests a parameter that does not matter here, and is retained only as a completeness check.
- This is historical weighting, not EMA. PeakFQ/EMA with the 1982 crest over a stated perceptibility threshold remains the documented follow-up.

## Q2 stationarity

- Hardy annual peaks (log10 cfs): Sen slope 0.00125 log10-cfs/yr (95% CI -0.0232 to 0.03); MK z=0.17, p=0.862; n=24; Pettitt change after WY 2011 (p=1.000)
- Imboden annual peaks (log10 cfs): Sen slope 0.00112 log10-cfs/yr (95% CI -0.00123 to 0.00406); MK z=0.94, p=0.346; n=89; Pettitt change after WY 2005 (p=0.350)
### Upper-tail trend (pre-registered) and the post-hoc 2008 shift

The decision rule used for the verdict below (trend CI excludes zero AND split 10-yr quantile CIs disjoint) can barely fail at any n and only inspects the centre of the distribution. A flood-risk question is about the upper tail, so the tail is tested directly.

|   quantile |   slope_log10_per_yr |       lo |      hi |       p |
|-----------:|---------------------:|---------:|--------:|--------:|
|        0.5 |             -0.00076 | -0.0046  | 0.00308 | 0.69438 |
|        0.9 |              0.00263 | -0.00172 | 0.00698 | 0.23224 |

- top-quartile (≥45,900 cfs) Sen slope +0.00081 log10-cfs/yr (95% CI -0.00094 to +0.00386, n=23).
- **Both upper-tail tests have CIs spanning zero.** The Q2 conclusion is therefore better supported than the conjunction rule made it look: it now rests on a test that could have detected a tail change.

**Disclosed as post hoc.** A split at WY 2008 gives a mean shift (24,598 → 38,241 cfs; Welch p=0.028, Mann–Whitney p=0.050) that the decision rule never surfaced. The split year was chosen after seeing the data — a split at 1980 gives p=0.77 — so this is a finding to test on new data, not a result. It is reported because omitting it would be selective.

The largest peak in the record is WY1983 (244,000 cfs), 1.9× the next largest.


Imboden LP3 split at WY 2008:

### Imboden WY <2008 (n=71, WY 1937–2007, station skew -0.24, weighted skew -0.23; low outliers flagged below 2704 cfs: 1 (retained; no B17B conditional-probability adjustment applied))

|   return_period |   q_cfs |   q_lo |   q_hi |
|----------------:|--------:|-------:|-------:|
|            1.25 |   13087 |  10772 |  15865 |
|            2    |   25342 |  21816 |  29228 |
|            5    |   47044 |  39447 |  55213 |
|           10    |   63943 |  51676 |  79094 |
|           25    |   87627 |  66709 | 118102 |
|           50    |  106701 |  76906 | 154689 |
|          100    |  126824 |  86576 | 200982 |

### Imboden WY ≥2008 (n=18, WY 2008–2025, station skew 0.28, weighted skew 0.04; low outliers flagged below 7251 cfs: 0 (retained; no B17B conditional-probability adjustment applied))

|   return_period |   q_cfs |   q_lo |   q_hi |
|----------------:|--------:|-------:|-------:|
|            1.25 |   20973 |  16690 |  28393 |
|            2    |   38043 |  28932 |  51256 |
|            5    |   69516 |  49333 |  92808 |
|           10    |   95546 |  64510 | 126275 |
|           25    |  134424 |  85898 | 177533 |
|           50    |  167798 | 103119 | 224480 |
|          100    |  205010 | 120817 | 277209 |

## Partial-duration series (Hardy daily max IV stage, 7-day declustering)

- ≥8 ft (all): 45 events over complete WY 2008–2025 (n=18); mean 2.50/yr; dispersion 1.24 (p=0.453); count trend Sen slope -0 events/yr (95% CI -0.0833 to 0.25); MK z=0.59, p=0.554; n=18
- ≥10 ft (all): 17 events over complete WY 2008–2025 (n=18); mean 0.94/yr; dispersion 0.81 (p=0.624); count trend Sen slope -0 events/yr (95% CI -0 to 0.1); MK z=0.57, p=0.568; n=18
- ≥14 ft (all): 8 events over complete WY 2008–2025 (n=18); mean 0.44/yr; dispersion 0.85 (p=0.737); count trend Sen slope -0 events/yr (95% CI -0 to -0); MK z=-0.89, p=0.373; n=18
- ≥16 ft (all): 6 events over complete WY 2008–2025 (n=18); mean 0.33/yr; dispersion 1.06 (p=0.778); count trend Sen slope -0 events/yr (95% CI -0 to -0); MK z=-1.27, p=0.204; n=18

Partial WY 2026 (stage through 2026-08-24; excluded from the dispersion and trend tests above) counts: ≥8 ft 0, ≥10 ft 0, ≥14 ft 0, ≥16 ft 0

Sensitivity (approved-only days; complete WYs of the approved series):

- ≥8 ft (approved-only): 45 events over complete WY 2008–2025 (n=18); mean 2.50/yr; dispersion 1.24 (p=0.453); count trend Sen slope -0 events/yr (95% CI -0.0833 to 0.25); MK z=0.59, p=0.554; n=18
- ≥10 ft (approved-only): 17 events over complete WY 2008–2025 (n=18); mean 0.94/yr; dispersion 0.81 (p=0.624); count trend Sen slope -0 events/yr (95% CI -0 to 0.1); MK z=0.57, p=0.568; n=18
- ≥14 ft (approved-only): 8 events over complete WY 2008–2025 (n=18); mean 0.44/yr; dispersion 0.85 (p=0.737); count trend Sen slope -0 events/yr (95% CI -0 to -0); MK z=-0.89, p=0.373; n=18
- ≥16 ft (approved-only): 6 events over complete WY 2008–2025 (n=18); mean 0.33/yr; dispersion 1.06 (p=0.778); count trend Sen slope -0 events/yr (95% CI -0 to -0); MK z=-1.27, p=0.204; n=18

Dispersion index = variance/mean of annual counts (1 under Poisson; >1 clustered). A water year is complete when the daily-max stage series has a row on/after its Sep 30.

|   wy |   ge_8ft_all |   ge_10ft_all |   ge_14ft_all |   ge_16ft_all |   ge_8ft_approved |   ge_10ft_approved |   ge_14ft_approved |   ge_16ft_approved |
|-----:|-------------:|--------------:|--------------:|--------------:|------------------:|-------------------:|-------------------:|-------------------:|
| 2008 |            2 |             2 |             2 |             2 |                 2 |                  2 |                  2 |                  2 |
| 2009 |            2 |             0 |             0 |             0 |                 2 |                  0 |                  0 |                  0 |
| 2010 |            3 |             1 |             1 |             1 |                 3 |                  1 |                  1 |                  1 |
| 2011 |            1 |             1 |             1 |             1 |                 1 |                  1 |                  1 |                  1 |
| 2012 |            1 |             0 |             0 |             0 |                 1 |                  0 |                  0 |                  0 |
| 2013 |            2 |             0 |             0 |             0 |                 2 |                  0 |                  0 |                  0 |
| 2014 |            2 |             1 |             0 |             0 |                 2 |                  1 |                  0 |                  0 |
| 2015 |            5 |             1 |             0 |             0 |                 5 |                  1 |                  0 |                  0 |
| 2016 |            5 |             2 |             1 |             0 |                 5 |                  2 |                  1 |                  0 |
| 2017 |            1 |             1 |             1 |             1 |                 1 |                  1 |                  1 |                  1 |
| 2018 |            1 |             0 |             0 |             0 |                 1 |                  0 |                  0 |                  0 |
| 2019 |            2 |             1 |             0 |             0 |                 2 |                  1 |                  0 |                  0 |
| 2020 |            4 |             0 |             0 |             0 |                 4 |                  0 |                  0 |                  0 |
| 2021 |            2 |             1 |             1 |             0 |                 2 |                  1 |                  1 |                  0 |
| 2022 |            2 |             1 |             0 |             0 |                 2 |                  1 |                  0 |                  0 |
| 2023 |            3 |             3 |             0 |             0 |                 3 |                  3 |                  0 |                  0 |
| 2024 |            0 |             0 |             0 |             0 |                 0 |                  0 |                  0 |                  0 |
| 2025 |            7 |             2 |             1 |             1 |                 7 |                  2 |                  1 |                  1 |
| 2026 |            0 |             0 |             0 |             0 |                 0 |                  0 |                  0 |                  0 |

## Q6 inter-arrival of ≥16 ft events

Events (annual-peak file for WY <2008, 7-day-declustered daily-max IV stage for WY ≥2008): 2006-09-23, 2008-03-19, 2008-04-10, 2009-10-30, 2011-04-26, 2017-04-30, 2025-04-05

- 2002–present: n=7, mean gap 3.09 yr, median 1.52, CV 1.01; KS vs exponential 0.27, bootstrap p=0.465
- with 1982 crest: n=8, mean gap 6.05 yr, median 1.56, CV 1.38; KS vs exponential 0.34, bootstrap p=0.108

Sensitivity (approved-only stage days for the post-2008 events):

- 2002–present (approved-only): n=7, mean gap 3.09 yr, median 1.52, CV 1.01; KS vs exponential 0.27, bootstrap p=0.465
- with 1982 crest (approved-only): n=8, mean gap 6.05 yr, median 1.56, CV 1.38; KS vs exponential 0.34, bootstrap p=0.108

A bootstrap p well above 0.05 means the gaps are consistent with a memoryless (Poisson) process — no evidence of a regular cadence; CV near 1 is the exponential signature, CV well below 1 would indicate regularity.

### What this test could have detected (power)

At n=6 gaps a memoryless process routinely produces a CV anywhere in **0.42–1.50** (central 95 %), so the observed CV 1.01 is unremarkable either way. Power of the test against a regular (gamma) cadence:

|   cv |   power |   n_gaps |   alpha |   critical_cv |
|-----:|--------:|---------:|--------:|--------------:|
| 0.7  |   0.227 |        6 |    0.05 |         0.484 |
| 0.5  |   0.578 |        6 |    0.05 |         0.484 |
| 0.35 |   0.92  |        6 |    0.05 |         0.484 |

- 80 % power is reached only at CV ≈ 0.35 — near-metronomic.
- **State the conclusion as 'no cadence is detectable, and none weaker than near-metronomic could have been' — not as 'the process is memoryless'.** A high p here is an absence of evidence.
- Adding the 1982 crest (the 'with 1982 crest' row above) is the only extra information available; a ≥10 ft POT series (see the partial-duration section) is the supplementary check with real n.

## Q7 quiet year (<8 ft peak) after a ≥16 ft year

- P(quiet | prior major) = 0.00 vs base rate 0.08; difference -0.08 (Clopper-Pearson exact 95% bounds on the conditional rate minus the base rate: -0.08 to +0.44); permutation p=1.000; n_major=5, n_years=24

Water years with a missing annual peak count as neither major nor quiet. With n_major=5 the test has little power; the CI is the honest statement.

### What this test could have detected (power)

Fisher-exact power at n_major=5, n_other=19, base rate 0.08, against a true conditional quiet-year rate of:

|   true_rate_given_major |   power |   n_major |   n_other |   base_rate |   alpha |
|------------------------:|--------:|----------:|----------:|------------:|--------:|
|                     0.2 |   0.084 |         5 |        19 |       0.083 |    0.05 |
|                     0.4 |   0.346 |         5 |        19 |       0.083 |    0.05 |
|                     0.6 |   0.654 |         5 |        19 |       0.083 |    0.05 |
|                     0.8 |   0.909 |         5 |        19 |       0.083 |    0.05 |

- 80 % power requires a true conditional rate of about 0.8 — i.e. a quiet year would have to follow a major flood most of the time before this design could see it.
- Against a 2.5× effect the power is roughly 0.08. The Clopper-Pearson bound already admits a conditional rate anywhere from 0.00 to 0.52.
- **Q7 is therefore reclassified as UNTESTABLE with the current record, not as 'no support'.** The design produced no result, which is not the same as a null result. Testing it needs many more major-flood years than this river has recorded.

## Antecedent conditions before ≥14 ft annual peaks (60-day BFI, 30-day basin precip)

| event_date          |   bfi_prior |   precip_prior_in |   baseflow_prior_cfs |
|:--------------------|------------:|------------------:|---------------------:|
| 2003-11-18 00:00:00 |        0.81 |              2.78 |               383.07 |
| 2006-09-23 00:00:00 |        0.8  |              3.19 |               242.65 |
| 2008-03-19 00:00:00 |        0.51 |              5.75 |               798.16 |
| 2009-10-30 00:00:00 |        0.55 |              9.46 |              1191.44 |
| 2011-04-26 00:00:00 |        0.43 |             12.04 |               805.81 |
| 2015-12-28 00:00:00 |        0.54 |              8.04 |               927.3  |
| 2017-04-30 00:00:00 |        0.64 |              7.59 |              1086.58 |
| 2021-04-29 00:00:00 |        0.7  |              2.78 |              1329.99 |
| 2025-04-05 00:00:00 |        0.8  |              3.59 |              1277.95 |

BFI from segmented Eckhardt on Hardy DV discharge; precip is the basin mean (NOAA AORC v1.1 1 km hourly basin mean over the MoDNR Mammoth Spring recharge polygon (~349 mi²), daily totals 24 h ending 12 UTC). Windows exclude the event day.

![freq](../reports/figures/phase5_freq_curves.png)

![pot](../reports/figures/phase5_pot_counts.png)

## Stationarity verdict

**Verdict: no detectable change in flood frequency.**

- Imboden peak trend CI excludes zero: no (Sen slope +0.0011 log10-cfs/yr, 95% CI -0.0012 to +0.0041).
- Imboden 10-yr quantile, WY <2008: 63,943 cfs (5–95% 51,676–79,094); WY ≥2008: 95,546 cfs (64,510–126,275); CIs overlap: yes.
- Rule: 'non-stationary' requires both a trend CI excluding zero and non-overlapping split-period 10-yr CIs. Magnitude-tier comparison at Hardy rests on n=24.

## Limitations

- LP3/MOM with weighted skew, not EMA. The headline fit excludes the 1982 crest; the historical-weighting sensitivity above puts it back and is the case to quote at 20–23 ft. Regional skew approximate.
- Hardy n=24; return periods beyond ~50 yr are extrapolation — the CIs say so.
- Stage↔flow mapping is a log-log fit to annual-peak pairs, not the USGS rating. **Q5's rating drift does not measurably reach these stages**: refitting stage→flow on recent water years only moves the 23 ft return period by a couple of years, and the fit's residuals show no trend against water year — the drift is a low- and mid-flow control effect. The real extrapolation risk at 29 ft is the stage→flow relation itself (see below), not the drift.
- POT and Q6 post-2008 events use daily MAX IV stage (upper bound vs a daily-mean product).
- Imboden peaks file in NWIS begins WY 1937; the split at WY 2008 leaves n=18 in the post period.
- Q6 and Q7 are power-limited, and the power sections say by how much: Q6 cannot detect any cadence weaker than near-metronomic, and Q7 cannot detect any plausible effect at all. Read their high p-values as absence of evidence, not evidence of absence.
- The 29 ft crest is 1.27× the maximum observed stage and its implied flow is 1.86× the maximum observed flow: the stage→flow relation is extrapolated well beyond its data there, which is a larger uncertainty than the frequency fit itself.
