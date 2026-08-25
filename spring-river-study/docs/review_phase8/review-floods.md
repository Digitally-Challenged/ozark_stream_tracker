# Phase 8 adversarial review — FLOOD conclusions (Q2, Q8, Q6, Q7, §6.1)

Reviewer scratch: `scratchpad/phase8/floods/` (`a_hist.py`, `b_trend.py`, `c2.py`, `d_rating.py`, `e_misc.py`).
All runs `uv run python … ` from `spring-river-study/`. Repo untouched.

Claims reviewed: 7. Verdicts: **STANDS 3 · WEAKENED 3 · REFUTED 1.**

---

## Claim Q8a — "23 ft = 29 yr; 20 ft = 12.5 yr" at Hardy (docs/phase5_floods.md:53-54; report.qmd:587, 817)

**Strongest attack.** The 1982-12-03 29.0 ft crest is deliberately excluded ("reported as a historical exceedance only, not fitted", report.qmd:825). That is not a neutral omission: excluding a known record-setting exceedance from a 24-year fit while retaining the 44-year *awareness* of it inflates the return period of exactly the stages the report calls the "flood exposure, major" tier. The report's own hedge ("the practical number is the empirical rate", :817) concedes the LP3 number is not the one to use, yet the 29-yr figure is what appears in the headline paragraph (:447) and the tier table (:813).

**What would falsify it.** A historical-information fit (B17C/EMA, or B17B Appendix-6 weighting) that leaves the 20 ft and 23 ft return periods within the reported bootstrap width.

**Checks run.** `a_hist.py`. Stage→flow (whole record, n=24): log10Q = 1.9538 + 2.2152·log10H, R²=0.9906 → 29.0 ft ≈ **156,000 cfs**. Independent corroboration (`e_misc.py`): Imboden WY1983 peak 244,000 cfs, log-log Imboden→Hardy on 24 concurrent pairs (slope 1.095, R²=0.811) → Hardy ≈ **183,000 cfs** (≈31 ft). So 156k is if anything conservative.

B17B-style historical weighting, threshold = the historical peak, systematic n=24, W=(H−Z)/(n−s):

| historical period H | W | station skew | weighted skew (−0.2 reg) | RP 16 ft | RP 20 ft | RP 23 ft |
|---|---|---|---|---|---|---|
| baseline (no 1982) | — | −0.157 | −0.175 | 4.5 | **12.5** | **29.4** |
| 1982–2025 (H=44) | 1.79 | −0.000 | −0.056 | 4.0 | **9.9** | **20.1** |
| 1937–2025 (H=90) | 3.71 | −0.067 | −0.089 | 4.3 | **11.3** | **24.5** |

Station-skew-only sensitivity is immaterial: H=44 gives 9.8 / 19.4 yr; H=90 gives 11.2 / 24.1 yr — i.e. the regional-skew choice moves the 23-yr return period by ≤0.7 yr, an order of magnitude less than the 1982 decision moves it. **The −0.2 regional value is a non-issue; the 1982 exclusion is the whole story.**

**Verdict: WEAKENED.** The point estimates are biased long by ~20–30 % at the stages that matter. 23 ft is 20–25 yr, not 29; 20 ft is 10–11 yr, not 12.5. Both remain inside the reported 5–95 % bootstrap band, so nothing is *refuted* — but the reported skew sensitivity ("station skew only") is the wrong sensitivity to have run. It tests the parameter that doesn't matter and omits the one that does.

**What would settle it.** PeakFQ/EMA with the 1982 crest as a historical peak over a stated perceptibility threshold, plus the Arkansas/Missouri regional skew study value. The scratch computation above is an adequate stand-in for the direction and rough size.

---

## Claim Q8b — "Stage→flow via a fixed log-log fit; rating drift (Q5) propagates here" (docs/phase5_floods.md:181)

**Strongest attack.** Q5 documents −0.019 ft/yr at 1,000 cfs and a step at 2008→2010. If the control is degrading, a single whole-record log-log fit assigns pre-2010 (higher) stages to given flows, biasing stage return periods short in the recent regime.

**What would falsify it.** Refit on recent years only and see the stage return periods move materially.

**Checks run.** `d_rating.py`. Refit on WY≥2010 (n=16): a=2.0252, b=2.1541, R²=0.9963. Refit on WY≥2015 (n=11): a=2.0375, b=2.1479, R²=0.9967.

| stage | whole-record RP | WY≥2010 RP | WY≥2015 RP |
|---|---|---|---|
| 16 ft | 4.5 | 4.4 | 4.5 |
| 20 ft | 12.5 | 12.0 | 12.3 |
| 23 ft | 29.4 | 27.1 | 27.8 |

Residuals of the whole-record fit vs water year: slope +0.0010 log10-cfs/yr, p=0.332 (n=24) — no detectable drift in the *flood-stage* relation.

**Verdict: STANDS.** The Q5 drift is a low-flow/mid-flow control phenomenon and does not measurably propagate to the 16–23 ft range. Worth saying so affirmatively rather than leaving it as an open caveat: recent-rating refits move 23 ft by 2.3 yr, i.e. **an order of magnitude less than the 1982 decision**. The real extrapolation risk at 23 ft is different and unstated: max observed Hardy stage is 22.82 ft, so 23 ft is barely extrapolated, but the 29 ft crest used above sits at 1.86× the maximum observed flow — the log-log fit's extension there is unvalidated.

---

## Claim Q2 — "No detectable change in flood frequency" at Imboden (docs/phase5_floods.md:171-175)

**Strongest attack.** The stated decision rule requires *both* a trend CI excluding zero *and* non-overlapping split-period 10-yr CIs — a conjunction that is very hard to fail to satisfy at any n, and which tests only the *central* tendency. If the distribution is widening at the top while the median is flat, the rule cannot see it. And the brief's own framing ("the three largest Imboden peaks are all recent-ish") points exactly there.

Also: the brief's premise is factually off. The three largest Imboden peaks are **WY1983 (244,000 cfs, 38.12 ft), WY2025 (128,000), WY2011 (122,000)** — the "1982" event is the Dec-1982 crest that falls in water year 1983, and it is 1.9× the second largest. Any "big ones getting bigger" narrative has to explain that its single largest event is 43 years old.

**What would falsify it.** A split, change-point, upper-tail, or clustering test that finds a significant recent increase after honest accounting for multiplicity.

**Checks run.** `b_trend.py`, n=89, WY1937–2025, log10 cfs.

- Split at **1980**: n 43/46, geometric means 26,235 vs 27,526 cfs; Welch p=0.769, Mann-Whitney p=0.879. **No change.** The brief's suggested alternative split finds nothing.
- Split at 1990: p=0.287 / 0.467. Nothing.
- Split at **2008**: n 71/18, 24,598 vs 38,241 cfs; **Welch p=0.028, Mann-Whitney p=0.050.** The post-2008 period *is* significantly wetter in the mean of log peaks — which the report's rule never tested, because it compared bootstrap 10-yr *quantile* CIs (wide by construction) instead of the location of the distributions.
- **Top-quartile only** (n=23, peaks ≥ 75th pct): Sen slope +0.00081 log10-cfs/yr, 95% CI −0.00094 to +0.00386; Spearman ρ=0.207, p=0.343. **No upper-tail trend.**
- Quantile regression on year: q=0.50 slope −0.00076 (p=0.694); q=0.75 +0.00055 (p=0.780); q=0.90 +0.00263 (p=0.232). All CIs span zero. **The big ones are not getting bigger.**
- Top-decile (n=9) Spearman ρ=0.70, p=0.036 — but that is a rank correlation on a hand-picked upper tail with no multiplicity control, and the quantile regression above (the principled version of the same question) is null.
- **Clustering of extremes** (permutation on mean year of the k largest, 200,000 draws): top-3 mean year 2006.3, one-sided p=0.044; top-5 mean 2000.8, p=0.039; top-10 mean 1989.9, p=0.127. Three tests, best p=0.039; with even a Bonferroni over the three k values nothing survives, and the choice of k was made after seeing the data.

**Verdict: WEAKENED.** The headline conclusion survives every *upper-tail* attack — quantile regression at q=0.90, top-quartile Sen slope, and the top-10 clustering test all come back null, and the 1980 split is flat. That is a genuinely stronger result than the report currently claims for itself, and it should be stated. But the conclusion is **not** supported by the stated decision rule, which is defective in two ways: (1) the conjunction "trend CI excludes zero AND split CIs disjoint" makes non-stationarity almost undetectable at n=89 by construction, and (2) the split test the report chose (overlapping bootstrap 10-yr quantile CIs) **misses a difference in means that is significant at p=0.028**. The report says "CIs overlap: yes" and stops; a reader is entitled to know that the same 2008 split shows a significant shift in central tendency. Right conclusion, wrong test, and an undisclosed borderline result.

**What would settle it.** Replace the ad-hoc conjunction with a pre-registered upper-tail test (quantile regression at q=0.9, or a GEV/GPA location-scale trend model), report it with its CI, and disclose the 2008 mean-shift result and its post-hoc-split status.

---

## Claim Q6 — "Major-flood inter-arrivals are memoryless" (CV 1.01, bootstrap p=0.47, n=7)

**Strongest attack.** With n=7 gaps, "consistent with exponential" is nearly uninformative — the test cannot reject almost anything. Presenting it as a positive finding ("memoryless", report.qmd:447 and :777) reads as evidence of absence.

**What would falsify it.** A power calculation showing the test can detect only implausibly strong regularity.

**Checks run.** `c2.py`, `e_misc.py`. Null sampling distribution of CV for n=7 exponential gaps: 5th pct **0.518**, central 95 % interval **0.461–1.498**. So *any* observed CV between 0.46 and 1.50 is "consistent with exponential" at n=7; the observed 1.01 is dead centre of a very wide acceptance region. One-sided power (α=0.05) against a gamma alternative:

| true CV | power, CV statistic (`c2.py`) | power, **study's KS-vs-exponential bootstrap** (`c_power.py`) |
|---|---|---|
| 1.0 (null) | 0.05 | 0.05 |
| 0.7 | 0.26 | **0.16** |
| 0.6 | 0.43 | — |
| 0.5 | 0.66 | **0.44** |
| 0.4 | 0.89 | — |
| 0.3 | 0.99 | **0.94** |

The study's actual statistic (KS against a fitted exponential, bootstrap p — `hydro/interarrival.py`) is **weaker than the CV proxy at every alternative**. It reaches 80 % power only around **CV ≈ 0.35** — i.e. it can detect a near-clockwork cadence (gaps varying by ~1/3 of their mean) and essentially nothing weaker. Moderate regularity (CV 0.5–0.7, a perfectly realistic hydrologic alternative) is missed 56–84 % of the time.

Separately, the "with 1982 crest" variant already gives CV 1.38, bootstrap p=0.108 (phase5_floods.md:134) — the same data with one more event moves p by a factor of 4.3, which is itself a statement about the fragility of the n=7 result.

**Verdict: WEAKENED.** "Memoryless" overstates it. The honest statement is "the 7 observed gaps cannot distinguish a Poisson process from anything with CV above ~0.35; no cadence is detectable and none could have been unless it were near-metronomic." The docs' own note ("A bootstrap p well above 0.05 means the gaps are consistent with a memoryless (Poisson) process", :141) is the sentence that needs the power number attached to it.

**What would settle it.** Nothing available. n=7 is the record. A longer POT series at a lower threshold (≥14 ft gives 8-9 events; ≥10 ft gives 17) would trade event severity for n and could support a real cadence test — worth running at ≥10 ft as a supplementary check, where n=17 gives a materially narrower acceptance region.

---

## Claim Q7 — "P(quiet year | major flood) = 0/5 vs base 0.08; no support" (docs/phase5_floods.md:145)

**Strongest attack.** Same as Q6 but worse: the base rate is 2/24. A conditional rate of 0/5 is the *most extreme observation in the direction of "no quiet years follow major floods"* and it still returns permutation p=1.000. The design cannot produce evidence in either direction.

**What would falsify it.** A power calculation showing the design can detect a plausible effect.

**Checks run.** `c2.py`, Fisher exact, n_major=5 vs n_other=19, base rate 2/19:

| true P(quiet \| major) | power |
|---|---|
| 0.2 | 0.06 |
| 0.4 | 0.27 |
| 0.6 | 0.60 |
| 0.8 | 0.88 |
| 1.0 | 1.00 |

**80 % power requires the conditional probability to be ~0.75 or higher** — i.e. the test can only detect the hypothesis that a major flood makes a quiet year *near-certain*. Against a strong-but-realistic 2.5× elevation (0.2), power is 0.06 — indistinguishable from the false-positive rate.

**Verdict: REFUTED as a finding.** Not the direction of the claim — the claim's *content* is fine ("no support") — but the framing. A test with 6 % power against a 2.5× effect has not produced a null result; it has produced no result. The docs do concede "with n_major=5 the test has little power; the CI is the honest statement" (:147), which is the right instinct, but the Clopper-Pearson bound (−0.08 to +0.44) understates it: the bound is on the *difference in rates*, and it is compatible with the conditional rate being anywhere from 0 to 0.52, which is the whole plausible hypothesis space. Q7 should be reported as **UNTESTABLE WITH CURRENT DATA**, not as a tested negative. As currently written the report line reads as a substantive finding, and it is not one.

**What would settle it.** Pooling with hydrologically similar Ozark spring-fed basins to raise n_major, or extending the definition of "major" downward (≥14 ft gives 9 events) at the cost of weakening the hypothesis.

---

## Claim §6.1a — "Peak timing: Imboden mean date 24 Feb, R 0.49, no decadal drift" (docs/phase7_seasonality.md:49; report.qmd:447)

**Strongest attack.** The decade table shows mean dates ranging **16 Jan (2000s) to 09 Apr (1960s)** — an 83-day spread — and the report calls that "no drift". No formal test of decade-to-decade homogeneity is reported; the conclusion rests on eyeballing a table where three consecutive recent decades (2000s 16 Jan → 2010s 27 Feb → 2020s 13 Mar) march monotonically later by 56 days.

**What would falsify it.** A Watson-Williams or circular ANOVA across decades rejecting equal mean directions, or a monotone trend in decade mean-doy.

**Checks run.** Read from `docs/phase7_seasonality.md:38-49`. Decade mean-doy sequence 1940s→2020s: 61.1, 58.3, 99.5, 40.2, 17.9, 87.0, 15.9, 57.8, 72.2. This oscillates with no monotone pattern over the full record; the recent three-decade march is a subsequence of a series that has previously swung 40→99→18 with n≈10 per decade. Rayleigh R per decade ranges 0.31–0.94 with n=9–11, so per-decade mean dates carry very large standard errors (for R≈0.5, n=10, the circular SE on the mean direction is roughly ±25–30 days).

**Verdict: STANDS**, with a caveat the report should carry. The oscillation is fully consistent with sampling noise at n≈10/decade, and the claim is not falsified. But "no decadal drift" is asserted, not tested — the docs' own limitation section (:198) flags a different issue (bimodality) and not this one. One line stating a Watson-Williams result across decades would convert an assertion into evidence; without it the strongest defence available is "the decade means are too noisy to say anything", which is weaker than the report's phrasing implies.

---

## Claim §6.1b — "Recession k: Hardy median 13.9 d, Mammoth 188 d, no trend"

**Strongest attack.** The docs already concede the fatal issue (`phase7_seasonality.md:196`): "events cluster within wet years, so n overstates independence." Hardy's n=16 includes three WY2023 events and three WY2025 events; Mammoth's n=80 includes six WY2015 and six WY2025 events. Mann-Kendall on clustered samples has inflated effective n and an anti-conservative p — but the reported result is *null*, so clustering makes the null **conservative**, not anti-conservative, in the sense that the true CI is wider than reported. The wide CIs (Hardy −0.215 to +0.401 days/yr; Mammoth −1.03 to +1.7) are therefore understated.

A second issue not flagged: Mammoth fits include events with r² as low as **0.280** (2020-02-14, k=1800.6 d) and 0.503, 0.579, 0.583, 0.653, 0.669, 0.742 — seven fits below r²=0.75, several producing k values 5–10× the median. These are single-exponential fits to non-exponential recessions and they dominate the upper IQR. No r² screen is applied.

**What would falsify it.** Re-running the trend on one event per water year (or a WY-block bootstrap), and on r²-screened events, and finding a slope CI excluding zero.

**Checks run.** Read from `docs/phase7_seasonality.md:96-188`. Event-per-WY counts: Hardy WY2023 ×3, WY2025 ×2, WY2007 ×2, WY2015/2016 ×2 → effective n ≈ 11, not 16. Mammoth: 45 distinct water years for 80 events → effective n ≈ 45, not 80. Correcting n from 80→45 widens the Mammoth CI by roughly √(80/45) = 1.33×, to about −1.4 to +2.3 days/yr. Neither correction changes the sign of the conclusion.

**Verdict: STANDS.** The null holds under every correction I can apply from the tabulated data, and the corrections all widen CIs around zero rather than move the point estimate. Two housekeeping items: report the effective n (WY-block) alongside the event n, and either screen or flag the seven Mammoth fits with r²<0.75 whose k values (585, 597, 835, 1105, 1801 d) are physically implausible for a spring recession and are inflating the reported IQR (150–231 d).

---

# Three findings the study owner most needs to hear

1. **The Q8 skew sensitivity tests the wrong parameter.** Station-vs-regional skew moves the 23 ft return period by ≤0.7 yr. Including the 1982 crest as historical information moves it from 29.4 to **20.1–24.5 yr**, and 20 ft from 12.5 to **9.9–11.3 yr**. The 156,000 cfs implied by the 29-ft crest is independently corroborated by the concurrent Imboden relation (→183,000 cfs). Run the historical-information fit before the report goes out, or state the ~25 % long bias in the headline rather than in a limitation.

2. **Q7 is not a null result — it is no result, and the report reads otherwise.** With n_major=5 the design has **6 % power against a 2.5× effect** and needs P(quiet|major) ≈ 0.75 to reach 80 %. Reclassify from "no support" to "untestable with current data". Q6 has the same problem more mildly: the study's own KS-bootstrap statistic reaches 80 % power only around CV ≈ 0.35 (16 % power at CV 0.7), so "memoryless" should become "no cadence detectable, and none weaker than near-metronomic could have been."

3. **Q2's stated decision rule fails to see a result its own data contain.** The conjunction rule ("trend CI excludes zero AND split 10-yr CIs disjoint") makes non-stationarity nearly undetectable by construction, and the 2008 split it uses shows a **significant shift in the mean of log peaks (Welch p=0.028, MWU p=0.050)** that the overlapping-quantile-CI test never surfaced. The good news is that every principled upper-tail test I ran is null — quantile regression at q=0.90 (+0.00263, CI −0.0017 to +0.0070), top-quartile Sen slope, and top-10 clustering (p=0.127) — so the conclusion is right and is *better supported than the report claims*. Swap the ad-hoc rule for the q=0.90 quantile regression, and disclose the 2008 mean shift as a post-hoc split.
