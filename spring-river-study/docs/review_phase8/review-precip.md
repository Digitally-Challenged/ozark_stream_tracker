# Phase 8 adversarial review — precipitation (Q3), coupling, and the 2026 statements

Reviewer scope: Q3 basin intensity indices, the basin-source comparison, the West Plains 1948– record and its
disagreement with the grids, the coupling lag, and the 2026 claims. All checks run read-only from
`spring-river-study/`; scratch scripts in `/tmp/p8*.py`, outputs reproduced inline. No repo file modified.

Headline: **two of the study's Q3 conclusions do not survive.** The AORC intensification signal is
substantially a 2002 discontinuity in the product, not a trend; and the one "significant" West Plains index is
an artefact of the 1.068 catch ratio. A third — the buffer-vs-polygon attribution — is asserted on evidence
that does not support it.

---

## Claim 1 — "AORC over the polygon shows intensification: 6/10 indices BH-significant (max1 +0.26, SDII +0.032, days ≥1 in +1.38, days ≥2 in, top-5 share, growing-season total)"

Source: `docs/phase6_precip.md` "basin: index trends"; `spring_river_research.md:72`.

**Strongest attack.** AORC v1.1 has no radar input before 2002 (the study's own
`src/spring_river/ingest/aorc.py:12-14` says so). A gauge+reanalysis blend is *smooth*; a radar-informed
analysis resolves convective cells. Every index the study flags as significant is an index that measures
sharpness — SDII, max 1-day, days ≥1 in, days ≥2 in, top-5 share. If the 2002 input change alone raises
these, a monotone-trend test on the pooled 1981–2025 record will read the step as a trend. The study lists
"AORC pre-2002 has no radar" as a limitation but never tests whether it *is* the signal.

**What would falsify it.** If the AORC intensity indices trend within each era, or if the co-located gauge
record shows a comparable jump across 2002, the step is climate, not instrumentation.

**Checks run.** Rebuilt AORC daily from the 45 per-year hourly caches (394,464 h, 1981-01-01→2025-12-31,
24 h ending 12 UTC) and reproduced the published trends exactly (SDII +0.036/dec, max1 +0.275, days≥1
+1.25 — matches `phase6_precip.md` to rounding). Then pre/post-2002 means, AORC vs the West Plains gauge
over the identical years (`/tmp/p8b.py`):

| index | AORC 1981–01 | AORC 2002–25 | AORC Δ | WP Δ (same years) |
|---|---|---|---|---|
| sdii_in | 0.286 | 0.399 | **+39.7 %** | **+1.4 %** |
| days_ge_2 | 0.95 | 2.42 | **+153.8 %** | +23.0 % |
| days_ge_1 | 8.33 | 13.00 | **+56.0 %** | +18.2 % |
| max1_in | 2.40 | 3.21 | +33.8 % | +16.1 % |
| top5_frac | 0.190 | 0.221 | +16.6 % | −1.7 % |
| total_in | 45.09 | 49.67 | +10.1 % | +10.6 % |

Annual *total* moves identically in both (+10 % vs +11 %) — the two products agree on how much rain fell.
Only the *sharpness* indices diverge, and they diverge exactly at the radar onset.

OLS with a 2002 step term (`/tmp/p8c.py`):

```
sdii_in    year only  b=+0.0377/dec p=0.0000 | +step: b=+0.0000/dec p=0.9983, step=+0.1133 p=0.0012
days_ge_1  year only  b=+1.3307/dec p=0.0025 | +step: b=-0.8646/dec p=0.2475, step=+6.6120 p=0.0013
days_ge_2  year only  b=+0.3491/dec p=0.0634 | +step: b=-0.5417/dec p=0.1108, step=+2.6830 p=0.0035
max1_in    year only  b=+0.2645/dec p=0.0256 | +step: b=-0.0191/dec p=0.9327, step=+0.8542 p=0.1513
top5_frac  year only  b=+0.0115/dec p=0.0018 | +step: b=+0.0040/dec p=0.5642, step=+0.0227 p=0.2074
```

The SDII trend — the study's strongest result at z=4.55 — becomes **exactly zero** (b=+0.00000/dec, p=0.998)
once a 2002 level shift is allowed, and the step is significant at p=0.001. Within-era Sen slopes confirm it:
SDII is +0.013/dec in 1981–2001 and **−0.009/dec** in 2002–2025, against +0.036 pooled. Same pattern for
max1 (+0.142 then −0.066, pooled +0.275) and days≥1 (0.000 then −1.277, pooled +1.250). Every flagged index
trends flat or negative *inside* both eras and only rises when the eras are pooled.

**Verdict: REFUTED as stated.** The AORC intensity trends are not distinguishable from a single
discontinuity at the documented change in the product's inputs. The correct statement is: AORC's
storm-sharpness indices step up at 2002 and trend flat-to-negative within each era.

**What would settle it.** (a) AORC v1.1 documentation or NOAA validation quantifying the pre/post-2002
homogeneity of sub-daily/daily extremes over the mid-South. (b) A radar-era-only test (2002–2025, n=24) —
already run above, it is flat. (c) Livneh or nClimGrid-Daily over the same polygon 1981–2025 as an
independent gridded product without a 2002 input change.

---

## Claim 2 — "The West Plains 1948– gauge does not corroborate intensification over 1949–2025; the difference is point-vs-areal and 1949-vs-1981"

Source: `docs/phase6_precip.md` "Reading the West Plains 1948–"; `spring_river_research.md:72`.

**Strongest attack.** The study names two candidate explanations (geometry, window) and adopts them without
testing either. There is a third it does not name — the product. If the gauge is flat on AORC's *own*
1981–2025 window, the window explanation is dead, and given Claim 1 the residual explanation is that AORC's
signal is a product artefact, not that the gauge is a poorer instrument.

**What would falsify it.** The gauge showing intensification once restricted to 1981–2025.

**Checks run** (`/tmp/p8a.py`). West Plains 1948– indices restricted to 1981–2025 (same window as AORC,
n=44 index years):

| index | WP 1981–2025 | AORC 1981–2025 |
|---|---|---|
| sdii_in | +0.0082 (−0.0107, +0.0241) p_bh 0.52 | +0.032 (0.020, 0.046) p_bh 0.000 |
| max1_in | +0.100 (−0.161, +0.340) p_bh 0.52 | +0.264 (0.052, 0.495) p_bh 0.046 |
| days_ge_1 | +0.745 (−0.000, +1.818) p_bh 0.37 | +1.379 (0.488, 2.222) p_bh 0.016 |
| top5_frac | −0.0017 p_bh 0.74 | +0.010 (0.003, 0.018) p_bh 0.040 |
| total_in | +1.445 p_bh 0.37 | +0.960 p_bh 0.395 |

**Zero of ten** indices are BH-significant at the gauge on AORC's own window. The disagreement is therefore
**not period**. Nor is it purely areal smoothing: PRISM 4 km over the *same* MoDNR polygon, 1981–2025, gives
SDII +0.0217 (0.0084, 0.0358) and max1 +0.280 (0.082, 0.481) — but PRISM shares Stage IV/MRMS and gauge
inputs with AORC (`aorc.py:14-15`), so it is not an independent witness to the same radar-era change.

**Verdict: WEAKENED — the stated explanation is wrong, and the conclusion is stronger than written.** The
gauge does not merely "fail to corroborate over a different window"; it fails to corroborate over the
*identical* window. Combined with Claim 1's step test, the parsimonious reading is that the intensification
is in the gridded product, not in the atmosphere over this basin. The report's framing ("a point-vs-areal
and record-length difference, not a coverage artifact") should be replaced.

**What would settle it.** Per-cell AORC at the West Plains gauge coordinate (−91.874, 36.727) vs the gauge
daily record, 1981–2025, split at 2002. Not feasible offline: the cache
(`data/raw/aorc_basin_hourly_*.parquet`) stores only the polygon mean (`time_utc`, `pcpn_mm`) — the per-cell
grid is discarded at ingest (`aorc._basin_hourly_mean`). Re-pulling one cell from
`s3://noaa-nws-aorc-v1-1-1km` would settle this decisively and cheaply.

---

## Claim 3 — "The first edition's significant annual-total rise (+2.41, 0.36–4.46) was a property of the oversized 30 km buffer geometry"

Source: `spring_river_research.md:72`; `docs/precip_comparison.md`.

**Strongest attack.** Two nested areas over the same 45 years are near-perfectly correlated. Attributing a
difference in *significance* to geometry requires showing the geometries actually differ in trend — not that
one p-value landed on each side of 0.05.

**What would falsify it.** The buffer-minus-polygon difference series showing its own significant trend.

**Checks run** (`/tmp/p8i.py`, PRISM buffer vs PRISM polygon, 1981–2025, n=45):

```
annual total r = 0.9836
poly: +2.009 in/dec (CI -0.061, +4.198) p=0.0645
buf : +2.409 in/dec (CI +0.355, +4.463) p=0.0227
trend of DIFFERENCE (buf - poly): +0.272 in/dec (CI -0.091, +0.678) p=0.129
```

The two geometries' trends differ by +0.27 in/decade with a CI comfortably spanning zero. The CIs of the two
trends overlap over ~95 % of their length. What changed between editions is that a p-value crossed 0.05.

**Verdict: REFUTED as an attribution.** The buffer and polygon do not differ detectably in annual-total
trend; the edition-to-edition change in the *verdict* is a threshold crossing, not a geometric finding.
Rewrite as: "the annual-total trend is +2.0 to +2.4 in/decade across geometries, and is not separable from
zero at n=45 on either — the first edition's 'significant' label reflected the significance threshold, not a
different climate over a different area."

---

## Claim 4 — "West Plains 1948–: days ≥1 in +0.70/decade (0.26–1.15) is BH-significant; total +1.26 (0.28–2.34) is not (p_BH 0.067)"

Source: `docs/phase6_precip.md`; `westplains.py`.

**Strongest attack.** The whole record hinges on one number applied as a constant: KUNO × 1.068 for
1998–2026, i.e. a +6.8 % inflation applied to exactly the back half of a 76-year trend test. Any error in
that ratio maps one-for-one into the trend. The ratio is also measured over the very period it is applied
to, which is circular for trend purposes.

**What would falsify it.** The verdicts on days_ge_1 or total_in flipping under plausible alternative ratios.

**Checks run** (`/tmp/p8d.py`), full 1949–2025 record, BH across 10 indices:

| ratio | BH-significant | total_in slope (p_bh) | days_ge_1 slope (p_bh) |
|---|---|---|---|
| 1.000 (no adjustment) | **none** | +0.662 (0.517) | +0.400 (**0.517**) |
| 1.034 (half) | none | +0.989 (0.250) | +0.541 (0.133) |
| **1.068 (study)** | days_ge_1 | +1.262 (0.067) | +0.703 (**0.017**) |
| 1.100 | total_in, days_ge_1 | +1.541 (**0.016**) | +0.833 (0.002) |

The study's **only** significant West Plains index is created by the ratio. Drop the adjustment and nothing
is significant; raise it 3 % and the annual total becomes significant too. The published verdict sits at a
knife-edge in a nuisance parameter.

Two further problems with treating 1.068 as constant:
- **Strongly seasonal.** Monthly COOP/KUNO ratios: Jan 1.239, May 1.212, Sep 1.175, Aug 1.122, Jul **0.929**,
  Jun 0.978, Mar 0.994, Apr 0.998. Range 0.93–1.24. A flat 1.068 under-inflates winter and over-inflates
  summer — and days ≥1 in is a summer-weighted index.
- **Time-varying.** Overlap split at 2012: early 1.0933 (n=158 months), late 1.0390 (n=124). The ratio
  drifts ~5 % across the application window, which itself injects a spurious downward tilt into the KUNO era.

Applying the 12 monthly ratios instead of one constant (`/tmp/p8d.py`): days_ge_1 remains significant
(+0.682, p_bh 0.025) and no other verdict changes — so the *seasonal* refinement is benign. The
**existence** of the adjustment, not its seasonality, is what carries the result.

**Verdict: WEAKENED, materially.** The days≥1 finding is not robust to a nuisance parameter the study
treats as measured-and-settled. It must be reported with the ratio sensitivity attached, or downgraded.

**What would settle it.** Restrict the West Plains trend test to the homogeneous COOP-only era, or run a
formal homogenisation (e.g. quantile-matching rather than a mean ratio) with the adjustment uncertainty
propagated into the trend CI.

---

## Claim 5 — "The 1998 splice does not create a trend" (implicit; the study argues the ratio removes the step)

**Strongest attack.** The study checks only that the *mean level* matches. A splice can equally well *hide*
a trend by imposing a step of the wrong sign.

**Checks run** (`/tmp/p8c.py`), West Plains 1949–2025, OLS index ~ year + step(≥1998):

```
total_in     year only b=+1.2310/dec p=0.0084 | +step: b=+1.7203/dec p=0.0456, step=-2.6911 p=0.4943
days_ge_1    year only b=+0.7425/dec p=0.0004 | +step: b=+0.8484/dec p=0.0266, step=-0.5824 p=0.7382
sdii_in      year only b=+0.0035/dec p=0.2835 | +step: b=+0.0137/dec p=0.0247, step=-0.0557 p=0.0474
recharge_in  year only b=+0.4368/dec p=0.1248 | +step: b=+1.3744/dec p=0.0110, step=-5.1562 p=0.0404
```

Two indices carry a **significant negative residual step at 1998** after the ratio adjustment: SDII
(−0.056, p=0.047) and recharge_in (−5.16 in, p=0.040). For both, allowing the step *reveals* a trend that
the pooled fit suppresses: SDII goes from +0.0035/dec (p=0.28, "flat") to **+0.0137/dec (p=0.025)**, and
recharge_in from +0.44 (p=0.12) to **+1.37 (p=0.011)**.

This cuts against the study in a specific and interesting way: the report's claim that "the gauge shows more
wet days, not harder rain" rests on a flat SDII that may be a splice artefact. The residual step means the
1.068 mean-ratio adjustment does not homogenise the *distribution* — it matches totals while leaving KUNO's
wet-day counting (an ASOS tipping bucket resolving more small events than a volunteer observer) unmatched,
which deflates KUNO-era SDII (total/wet-days) exactly as observed.

**Verdict: WEAKENED — the splice is distorting, in both directions.** It manufactures the days≥1 result
(Claim 4) and suppresses an SDII and recharge-season trend. The report's two flagship West Plains sentences
("more wet days, not harder rain"; "does not corroborate intensification") both depend on which of these
artefacts you look at.

**What would settle it.** Wet-day-frequency matching (quantile mapping) between COOP and KUNO over the
282-month overlap instead of a single mean ratio, or a COOP-era-only (1949–1997, n≈48) trend test as the
homogeneous baseline.

---

## Claim 6 — "6/10 indices BH-significant" (the multiplicity control)

**Strongest attack.** BH controls the false-discovery rate assuming independence or positive regression
dependence. Ten precipitation indices from one daily series are heavily co-determined — days≥1, days≥2,
SDII, top-5 share and max1 are near-restatements of one another. Under strong positive dependence BH is
conservative for FDR but says nothing useful about "how many of these are real"; and the *count* of
significant indices is the number the report leads with, which is not an FDR-controlled quantity at all.

**What would falsify it.** A dependence-aware resampling null returning the same count.

**Checks run** (`/tmp/p8e.py`). Mean |r| among the 10 indices: **0.482** (AORC), 0.439 (WP) — the indices
are about half-redundant. Ran a max-T permutation null: permute the *year labels jointly* across all ten
indices (preserving their cross-correlation exactly), 5,000 draws, compare each observed |z| to the null
distribution of max|z|. This controls FWER under the true dependence.

| index | \|z\| | max-T p | BH verdict | max-T verdict |
|---|---|---|---|---|
| sdii_in | 4.55 | 0.0000 | sig | **sig** |
| days_ge_1 | 2.85 | 0.0264 | sig | **sig** |
| top5_frac | 2.77 | 0.0384 | sig | **sig** |
| max1_in | 2.42 | 0.0988 | sig | *not sig* |
| growing_in | 2.18 | 0.1694 | sig | **not sig** |
| days_ge_2 | 2.15 | 0.1814 | sig | **not sig** |
| days_ge_0p5 | 1.68 | 0.4486 | ns | ns |

Under max-T the count drops from **6/10 to 3/10** (4/10 if max1 at p=0.099 is called borderline).
growing_in and days_ge_2 do not survive. West Plains under max-T: days_ge_1 p=0.0100 survives; total_in
p=0.085 does not — so BH and max-T agree there.

**Verdict: WEAKENED.** BH is a defensible choice, but the headline "6/10" is inflated relative to a
dependence-aware FWER null. Report 3/10 (max-T) alongside 6/10 (BH), and stop using the *count* as a
summary statistic — with r̄=0.48 among indices it is closer to "3 effectively independent tests" than ten.
Note this attack is *subordinate* to Claim 1: under the 2002 step model none of these are trends at all.

---

## Claim 7 — "Coupling: monthly basin-precip anomalies → Mammoth flow, lag 1 month, r 0.45 (0.41–0.52, n=539)"

**Strongest attack.** The AORC daily total is a 24 h window ending 12 UTC. A storm arriving on the last
days of a month is largely assigned to that month while its flow response falls in the next — so a lag of
"1 month" could be a binning boundary effect rather than an aquifer transit time. And monthly binning cannot
resolve anything shorter than a month.

**What would falsify it.** The argmax lag moving with the day-end hour, or a daily-resolution
cross-correlation peaking near 30 days.

**Checks run** (`/tmp/p8g.py`):

```
AORC day-end hour sensitivity (argmax over lags 0-4):
  end  0 UTC: L0=0.305 L1=0.456 L2=0.346 L3=0.258  -> 1
  end  6 UTC: L0=0.297 L1=0.457 L2=0.344 L3=0.261  -> 1
  end 12 UTC: L0=0.290 L1=0.455 L2=0.341 L3=0.267  -> 1   (study's choice)
  end 18 UTC: L0=0.286 L1=0.454 L2=0.340 L3=0.268  -> 1
hourly -> calendar month directly (NO daily binning at all):
             L0=0.283 L1=0.450 L2=0.333 L3=0.261         -> 1
COOP gauge precip instead of AORC:
             L0=0.252 L1=0.411 L2=0.323 L3=0.263         -> 1
```

Lag 1 is invariant to the day-end hour (r at L1 moves 0.454→0.457), survives bypassing daily binning
entirely, and holds on COOP as well as AORC. The obs-day / 12-UTC artefact hypothesis is dead.

But the daily-resolution cross-correlation (day-of-year anomalies, AORC daily vs log Mammoth DV) tells a
different story about *interpretation*:

```
lag(days):   0     1     2     3     5     7    10    14    20    30    45    60    90
r:        0.102 0.136 0.141 0.140 0.137 0.132 0.124 0.120 0.110 0.098 0.081 0.069 0.053
```

The response peaks at **2–3 days** and decays monotonically — there is no local maximum near 30 days. The
"1 month" lag is the coarsest bin that captures a fast response plus a long tail; it is a resolution label,
not a transit time.

**Verdict: STANDS as a statistic, WEAKENED as a physical statement.** The number is robust. But if the
report reads "1 month" as the aquifer response time, that is wrong by an order of magnitude at the leading
edge: the spring begins responding within 2–3 days. Recommend reporting both — "onset within days
(daily-resolution peak at 2–3 d), monthly-anomaly correlation maximised at lag 1 month (r 0.45)".

**What would settle it.** A daily-resolution distributed-lag or transfer-function fit (already half-done
above), or event-scale analysis of individual storms.

---

## Claim 8 — "Sep 2025–Feb 2026 rain at West Plains 13.6 in = 10th driest of 75 (COOP-only 12.4 = 4th of 66; KUNO raw 12.8 = 8th)"

**Checks run** (`/tmp/p8h.py`, ≥90 % window coverage gate):

```
Sep-Feb (spliced):  2026 = 13.63 in, rank 10 driest of 75    <- matches report exactly
Sep-Feb COOP-only:  2026 = 12.40 in, rank  4 driest of 66    <- matches
Sep-Feb KUNO raw:   2026 = 12.76 in, rank  3 driest of 28
```

The spliced and COOP-only figures reproduce exactly. **The "KUNO raw 12.8 = 8th" does not**: I get 12.76 in
at rank **3 of 28** (KUNO starts 1998, so only 28 Sep–Feb seasons exist — an "8th of N" for KUNO is not
reachable under any N I can construct). Either the report's KUNO figure uses a different denominator (an
unstated pooling with COOP years) or it is a transcription error.

**Window sensitivity** — the recharge-season rank is not stable:

```
Sep-Feb: 13.63 in, rank 10 of 75
Oct-Mar: 12.82 in, rank  6 of 76
Nov-Apr: 16.81 in, rank 15 of 76
Aug-Jan: 13.50 in, rank 12 of 74
```

Rank spans 6th to 15th across four defensible six-month recharge windows — a factor of 2.5 in "how dry".
"10th driest" carries more precision than the window definition supports.

**Verdict: STANDS with two corrections.** (a) Fix or source the "KUNO raw 12.8 = 8th" figure — it does not
reproduce. (b) Report the rank as a range across window definitions (6th–15th driest) or state Sep–Feb as a
pre-registered choice.

---

## Claim 9 — "Mar–Jun 2026 mean flow lowest of 24 yr at Hardy (560 vs median 1,255 cfs) and 4th-lowest of 46 at Mammoth (291)"

**Checks run** (`/tmp/p8h.py`, ≥90 % coverage of Mar 1 – Jun 30):

```
Hardy   Mar-Jun 2026 = 560 cfs, rank 1 lowest of 25; median 1450
Mammoth Mar-Jun 2026 = 291 cfs, rank 4 lowest of 46; median  418
```

The substance holds: Hardy 2026 **is** the lowest Mar–Jun on its record, and Mammoth **is** 4th-lowest of
46. Two numeric discrepancies: the Hardy record has **25** qualifying years, not 24; and the Hardy Mar–Jun
median is **1,450 cfs**, not 1,255. The 1,255 figure may come from a different coverage gate or a
mean-of-years rather than median — either way it understates the 2026 deficit (2026 is 39 % of the median,
not 45 %), so correcting it strengthens the claim.

**Verdict: STANDS; two numbers need correcting** (n=25 not 24; median 1,450 not 1,255).

---

## Claim 10 — "Annual total not significant (+0.96, CI −1.25 to 3.12) and recharge-season flat-to-negative (−0.81, CI −1.99 to 0.60)"

Reproduced exactly from the rebuilt AORC caches: total +0.951 (−1.250, +3.124) n=45; recharge −0.793
(−1.993, +0.602) n=44 (`/tmp/p8b.py`). Unaffected by the 2002 step attack — total_in's step term is
p=0.060 and the year coefficient was never significant either way.

**Verdict: STANDS.** This is the most robust Q3 result in the set, and — given Claims 1 and 2 — arguably the
only Q3 result that should be stated without qualification.

---

## Claims reviewed: 10 — STANDS 3 (Claims 7 statistic, 9, 10) · WEAKENED 4 (2, 4, 5, 6) · REFUTED 2 (1, 3) · plus Claim 8 STANDS-with-corrections

(Claim 7 is counted under STANDS for the statistic with a documented weakening of the physical reading;
Claim 8 counted with the STANDS group.)

---

## The three findings the study owner most needs to hear

**1. The Q3 intensification headline is a 2002 discontinuity in AORC, not a trend.** Allow a step at the
documented radar-onset year and the SDII trend goes to exactly zero (+0.00000/dec, p=0.998) while the step is
p=0.001; every flagged index trends flat-or-negative within both eras. The co-located gauge shows +1.4 %
in SDII across 2002 where AORC shows +40 %, while the two agree to within 1 point on annual *total*. The
report's own limitations list names the radar onset but never tests it — and it is the whole result. This
should be reframed before publication, not footnoted.

**2. The West Plains "days ≥1 in" finding is manufactured by the 1.068 catch ratio, and the splice is
simultaneously hiding an SDII and recharge-season trend.** With no ratio: nothing significant (p_bh 0.52).
At 1.100: the annual total becomes significant too. And a residual 1998 step term is significant for SDII
(−0.056, p=0.047) and recharge_in (−5.16 in, p=0.040), revealing trends of +0.0137/dec (p=0.025) and
+1.37/dec (p=0.011) that the pooled fit suppresses. Both of the report's West Plains sentences — "more wet
days, not harder rain" and "does not corroborate intensification" — rest on splice artefacts pointing in
opposite directions. Needs quantile-based homogenisation or a COOP-era-only baseline.

**3. Two attributions are asserted without the test that would support them, and both fail it.** (a) The
buffer-vs-polygon difference is called "the buffer's geometry", but the two series are r=0.984 and the trend
of their difference is +0.27 in/dec (CI −0.09 to +0.68, p=0.13) — the edition-to-edition change is a p-value
crossing 0.05, nothing more. (b) The gauge-vs-grid disagreement is called "point-vs-areal and
1949-vs-1981", but on AORC's own 1981–2025 window the gauge shows **0/10** significant indices — the window
explanation is falsified and the geometry one is not the parsimonious remainder once Claim 1 is in hand.
Separately, "6/10 BH-significant" becomes 3/10 under a max-T null that respects the r̄=0.48 correlation
among the indices; and the coupling "lag 1 month" is a binning label — the daily cross-correlation peaks at
2–3 days with no local maximum near 30.
