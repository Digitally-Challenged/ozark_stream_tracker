# Phase 8 — adversarial review of the conclusions

Written 2026-08-25 against the second edition (main 53297cd). Method: four independent reviewers who did not produce the results — three domain attackers (base flow and gauge; floods; precipitation and 2026) on Claude Opus and one Codex generalist — each given `docs/phase8-brief` (every conclusion with its numbers, the data map, read-only rules), told to refute, to say what would falsify each claim, and to run their own checks. Their full reports are summarised here per claim; the controller independently re-ran the two findings that overturn conclusions (AORC 2002 step; Q4 Hardy placebo). Verdict scale: **STANDS** · **WEAKENED** (how) · **REFUTED** (why) · **UNTESTABLE** (what data would test it).

Tally: 24 claims reviewed — 11 stand, 9 weakened, 3 refuted, 1 untestable. Two headline conclusions of the second edition change as a result (Q3 intensity; Q7 framing); three become stronger than the report currently states (Hardy low-flow rise; Q2 stationarity; Q5 rating drift); the rest survive with stated corrections.

---

## Base flow and the gauge

### Q1a — Mammoth Spring: no non-climatic decline (residual −0.0013 log-cfs/yr, CI −0.0033 to +0.0012, n=42)
- **Attack.** The 365-d/prior-365-d predictor windows are a convention; a karst spring with a 188-day recession constant may remember rain for longer, and a longer window could expose a decline the null hides. Also "≈0 on all three basin series" claims unanimity.
- **Falsifier.** A residual CI excluding zero on the negative side under a defensible window or with an evapotranspiration term.
- **Checks (reviewer).** Windows 180/365/545/730 d × three sources; West Plains max-temperature as a PET surrogate. AORC: −0.0013 … −0.0021, all CIs span zero; PET terms move the residual toward zero. PRISM-polygon at 730 d: **−0.0035/yr, CI upper bound −3×10⁻⁷, p=0.049**; PRISM 365-d fits p=0.062 / 0.087 with CIs almost wholly below zero.
- **Verdict: WEAKENED — conclusion survives on the primary series; "all three sources agree" does not.** State the PRISM fits as consistently, marginally negative, with the same candour applied to Hardy.
- **Would settle it.** A basin series independent of PRISM's gauge network (Stage IV/MRMS 2002→; Livneh or nClimGrid-Daily), and a window pre-registered from spring recession/tracer transit rather than convention.

### Q1b — Hardy: residual rise "source-dependent, not a finding"
- **Attack (in the study's favour).** The best climate control for Hardy is Mammoth Spring itself: same recharge climate, absorbs precipitation, ENSO, PET and any gridded-precip bias at once. If Hardy's rise is climate it vanishes against Mammoth.
- **Falsifier.** log(Hardy min7 / Mammoth min7) with no trend.
- **Checks (reviewer).** Ratio Sen trend **+0.0124/yr, CI +0.0028 to +0.0219, p=0.0023, n=24** — no precipitation model involved. Precip-only fits (dropping the never-significant ONI term, CI −0.080 to +0.176) are significant on **all three** sources (AORC +0.0213; PRISM-polygon +0.0116, p=0.021; buffer +0.0110, p=0.016). Robust to windows 180–730 d and to PET terms. Pettitt on the ratio: after WY2014 (p=0.029).
- **Verdict: WEAKENED — the hedge, not the number.** The source-dependence of the published figure is one weak regressor eating degrees of freedom at n=24. Report the ratio trend as primary evidence and retire "not a finding".
- **Would settle it.** Its existence is settled; its cause is Q1c.

### Q1c — the Hardy low-flow gain is real water, not a rating artefact (2002–07 gain ≈39 cfs; 2009–25 ≈128 cfs)
- **Attacks.** (a) A datum change or gauge move at WY2008. (b) Circularity: USGS shifts the rating *to* the wading measurements, so ~1 % agreement proves only that the rating tracks the measurements.
- **Falsifier.** A datum revision or site move dated 2007–2009; or no independent physical signal of channel change.
- **Checks (reviewer).** USGS monitoring-location metadata for 07069305 carries **two datum revisions — 340.91→342.49 ft (pre-Dec 2022) and 342.49→342.73 ft (Dec 2022–Dec 2024)** — both bookkeeping of the datum elevation, both post-2022, no site move, no `time-series-revisions`. The circularity attack is answered by **measured stage at measured discharge** (independent of the rating): stage in the 330–520 cfs band 3.44 ft (2004) → 3.21 (2007) → 3.04 (2011) → 2.97 (2026); normalised to 400 cfs, Sen trend **−0.0150 ft/yr, CI −0.0214 to −0.0100, p<0.0001, n=20 WY (2003–2026)**. The channel really degraded; the rating followed it.
- **Verdict: STANDS, on better evidence than the controller offered.** Two corrections: (i) the "no USGS datum records reviewed" limitation is now false — two revisions exist and are dated; (ii) the "~1 % in every era" agreement, recomputed against same-day daily values (n=157), is +1.3 % / **−2.6 %** / −0.4 % / +4.3 % with sd 4–5 %; report the means with their scatter and lead with the independent stage decline and the Mammoth ratio instead.
- **Would settle the cause.** Synoptic seepage runs Mammoth → South Fork → Hardy at low flow. South Fork at Saddle (07069295) carries ~34 cfs of the ~90 cfs unexplained; 07069220 (1988–95, 2010–16) shows no gain immediately below the vent.

### Q5 — stage at fixed discharge is falling (−0.019 ft/yr at 1,000 cfs; −0.008 at 400)
- **Attack.** Both numbers come from IV pairs whose discharge is itself rating-derived; a drifting rating produces drifting stage-at-flow with no channel change.
- **Falsifier.** Independently measured stage at measured discharge showing no decline.
- **Checks (reviewer).** Field-measurement-only trend at 400 cfs: −0.0150 ft/yr (p<0.0001, n=20 WY, 2003–2026) — steeper than the IV figure and four years longer, bracketing the 2006-09-23 event the shift table had to omit (3.36→3.48→3.25 ft across 2003–2007).
- **Verdict: STANDS, understated.** Add the field-measurement trend to Q5; it retires the "IV-derived only" limitation and the "events before IV_START have no pairs" gap.

### Q4 — post-flood base flow higher, not lower (Mammoth +26 %, Hardy +31 %, n=6)
- **Attack.** Six events, three nearest controls each from a thin, wet-skewed pool with heavy reuse (Hardy: 10 unique control years for 18 slots); the bootstrap excludes matching uncertainty. A placebo — the identical pipeline on random non-flood pseudo-events — tests whether the procedure manufactures the effect.
- **Falsifier.** A placebo distribution centred near the reported effect; collapse under k or skip-day changes.
- **Checks (reviewer; 200 placebo trials, same day-of-year).** Mammoth: placebo mean **+0.0 %** (sd 7.5), 0/200 reach +26 %; effect stable +18.9 to +26.0 % across k∈{1,3,5,8} and skip 15–90 d. Hardy: placebo mean **+10.7 %** (sd 16.6), 11.5 % of trials beat +30.7 %; at a 90-day skip the effect falls to **+8.0 % (CI −8.1 to +22.8)**.
- **Verdict: Mammoth STANDS (stronger than claimed); Hardy WEAKENED, materially.** About a third of Hardy's figure is procedural and part of the rest is recession water still present at 30 days. Report the placebo for both; give Hardy as placebo-corrected (~+20 %) with the skip-day sensitivity, or drop it.
- **Would settle it.** More events (n=6 is the binding constraint), or a dose–response regression of post-event base-flow anomaly on peak magnitude across all peaks, which needs no matched controls.

### BFI no trend; Pettitt change-points
- **Attack.** BFI is a ratio near 1 at a spring-fed river — nearly blind to a change in the absolute base-flow rate — yet cited as corroboration.
- **Verdict: STANDS as stated; evidentiary weight overstated.** Do not cite BFI's null as evidence against a base-flow change. Note Mammoth's WY2008 Pettitt is not significant (p=0.26) and should not sit beside Hardy's WY2013 (p=0.013). Unexplained in the text: the Hardy−Mammoth *difference* steps at WY2008 while the *ratio* and raw Hardy min7 change at WY2013–14.

---

## Floods

### Q8 — return periods (16 ft 4.5 yr; 20 ft 12.5; 23 ft 29)
- **Attack.** The 1982-12-03 29.0-ft crest (≈156,000 cfs by the study's log-log relation; ≈183,000 cfs by the concurrent Imboden relation) is excluded from the fit while being known — that biases the return periods of exactly the "major exposure" tier long. The reported sensitivity (station vs regional skew) tests a parameter that does not matter.
- **Falsifier.** A historical-information fit leaving 20/23 ft inside the reported bootstrap band with no change of point estimate.
- **Checks (reviewer; B17B historical weighting).** Historical period 1982–2025: 20 ft **9.9 yr**, 23 ft **20.1 yr**; period 1937–2025: 11.3 / 24.5 yr. Station-only skew moves 23 ft by ≤0.7 yr.
- **Verdict: WEAKENED.** Point estimates biased long by ~20–30 % at 20–23 ft; still inside the 5–95 % band, so not refuted. Report 23 ft as 20–29 yr with the historical-information case as the headline, and replace the skew sensitivity with the 1982 sensitivity.
- **Would settle it.** PeakFQ/EMA with the 1982 crest over a stated perceptibility threshold; the Arkansas/Missouri regional-skew study value.

### Q8b — rating drift propagating into stage return periods
- **Checks (reviewer).** Refit stage→flow on WY≥2010 / ≥2015: 23 ft moves 29.4 → 27.1 / 27.8 yr; residual-vs-year p=0.33.
- **Verdict: STANDS.** Q5's drift is a low- and mid-flow control effect and does not measurably reach 16–23 ft; say so affirmatively. The real unstated extrapolation is the 29-ft crest at 1.86× the maximum observed flow.

### Q2 — no detectable change in flood magnitude or frequency (Imboden n=89)
- **Attack.** The decision rule ("trend CI excludes zero AND split 10-yr quantile CIs disjoint") can barely fail at any n and only sees the centre of the distribution.
- **Checks (reviewer).** Split 1980: p=0.77. Split 2008: **Welch p=0.028, Mann–Whitney p=0.050** — a mean shift the rule never surfaced. Top-quartile Sen slope +0.0008 (CI −0.0009 to +0.0039); quantile regression q=0.90 +0.0026 (CI −0.0017 to +0.0070); top-10 clustering p=0.13; top-3/5 clustering p≈0.04 but post hoc and not surviving Bonferroni. Largest Imboden peak is WY1983 (244,000 cfs), 1.9× the next.
- **Verdict: WEAKENED as a procedure; the conclusion is right and better supported than claimed.** Replace the conjunction rule with a pre-registered upper-tail test (q=0.90 quantile regression or GEV location-scale trend) and disclose the post-hoc 2008 mean shift.

### Q6 — major-flood inter-arrivals memoryless (n=7)
- **Checks (reviewer).** Null CV at n=7: central 95 % interval 0.46–1.50. The study's KS-bootstrap reaches 80 % power only at CV ≈ 0.35 (16 % power at CV 0.7). Adding the 1982 crest moves p from 0.47 to 0.11.
- **Verdict: WEAKENED.** "Memoryless" → "no cadence detectable; none weaker than near-metronomic could have been." A ≥10 ft POT series (n=17) is the available supplementary check.

### Q7 — quiet year after a major flood (0/5 vs base 0.08)
- **Checks (reviewer).** Fisher power at n_major=5: 0.06 against a 2.5× effect; 80 % power needs P(quiet|major) ≈ 0.75. The Clopper–Pearson bound on the rate difference is compatible with a conditional rate anywhere in 0–0.52.
- **Verdict: UNTESTABLE WITH CURRENT DATA.** Reclassify from "no support" — the design produced no result, not a null result.

### §6.1a — peak timing, no decadal drift
- **Verdict: STANDS with a caveat.** Decade means swing 16 Jan – 9 Apr with n≈10 per decade (circular SE ≈ ±25–30 d); the recent three-decade march is a subsequence of a series that has swung 40→99→18. "No drift" is asserted, not tested — add a Watson–Williams across decades.

### §6.1b — recession constants, no trend
- **Verdict: STANDS.** Report effective n by water-year block (Hardy ≈11 of 16; Mammoth ≈45 of 80) and screen or flag the seven Mammoth fits with r²<0.75 whose k (585–1,801 d) inflate the IQR.

---

## Precipitation

### Q3a — AORC intensity indices rising (6/10 BH-significant; SDII +0.032, max1 +0.26, days ≥1 in +1.38)
- **Attack.** AORC has no radar before 2002; a gauge/reanalysis blend is smooth and a radar-informed analysis is sharp. Every flagged index measures sharpness. A monotone-trend test on a series with a 2002 input change reads the step as a trend. The study lists the radar onset as a limitation and never tests it.
- **Falsifier.** Within-era trends, or a comparable jump at the co-located gauge.
- **Checks (reviewer; controller reproduced).** Pre/post-2002 means, AORC vs West Plains gauge over identical years: SDII **+37–40 %** vs **+1 %**; days ≥1 in +56–60 % vs +18 %; max1 +34 % vs +16 %; **annual total +10 % vs +11 %** (the products agree on how much rain fell). OLS with a 2002 step: SDII slope **0.000/decade (p=0.998), step p=0.001**; days ≥1 in slope −0.9 (p=0.25), step p=0.002; max1 slope −0.02 (p=0.93). Within-era Sen slopes flat or negative on every flagged index.
- **Verdict: REFUTED as stated.** AORC's storm-sharpness indices step up at the documented change in the product's inputs and trend flat-to-negative within each era. The correct statement is that no intensification is detectable over the recharge area once the product discontinuity is allowed for. PRISM over the same polygon shares Stage IV/MRMS and gauge inputs and is not an independent witness.
- **Would settle it.** NOAA's AORC v1.1 homogeneity documentation; a radar-era-only test (2002–2025: flat); per-cell AORC at the gauge coordinate vs the gauge, split at 2002 (needs a one-cell re-pull; the cache keeps only the polygon mean); an independent grid without a 2002 input change (nClimGrid-Daily, Livneh).

### Q3b — the gauge "does not corroborate intensification; the difference is point-vs-areal and 1949-vs-1981"
- **Checks (reviewer).** West Plains record on AORC's own 1981–2025 window: **0/10** indices BH-significant.
- **Verdict: WEAKENED — the explanation is wrong, the observation is stronger.** The gauge fails to corroborate over the *identical* window; with Q3a the parsimonious reading is that the intensification is in the product. Replace the framing.

### Q3c — the first edition's significant annual-total rise "was a property of the 30 km buffer"
- **Checks (reviewer).** Buffer vs polygon annual totals r=0.984; trend of the difference +0.27 in/decade (CI −0.09 to +0.68, p=0.13).
- **Verdict: REFUTED as an attribution.** The geometries do not differ detectably in trend; a p-value crossed 0.05. Rewrite: +2.0 to +2.4 in/decade across geometries, not separable from zero at n=45 on either.

### Q3d — West Plains 1948–: days ≥1 in +0.70/decade significant; total not
- **Attack.** The whole KUNO era is scaled by one constant (1.068) measured on the period it is applied to; any error maps one-for-one into the trend.
- **Checks (reviewer).** Ratio 1.000: **nothing significant**. 1.034: nothing. 1.068: days ≥1 in. 1.100: total *and* days ≥1 in. The ratio is seasonal (Jan 1.24, Jul 0.93) and drifts (1.093 before 2012, 1.039 after); monthly ratios leave days ≥1 in significant (p_BH 0.025) — the seasonal refinement is benign, the existence of the adjustment carries the result. A residual 1998 step term is significant for SDII (−0.056, p=0.047) and recharge-season total (−5.2 in, p=0.040), and allowing it reveals SDII +0.0137/decade (p=0.025) and recharge +1.37/decade (p=0.011) that the pooled fit suppresses — KUNO's tipping bucket counts more small events than a volunteer observer, deflating KUNO-era SDII.
- **Verdict: WEAKENED, materially, in both directions.** "More wet days, not harder rain" rests on a knife-edge ratio and a splice artefact. Report the ratio sensitivity (1.00–1.10) with the result, and treat the COOP-only era (1949–1997, n≈48) as the homogeneous baseline.
- **Would settle it.** Wet-day-frequency (quantile) matching between COOP and KUNO over the 282 overlapping months instead of a mean ratio, with the adjustment uncertainty propagated into the trend CI.

### Q3e — "6/10 indices BH-significant"
- **Checks (reviewer).** Mean |r| among the ten indices 0.48; max-T permutation (year labels permuted jointly, 5,000 draws): 3/10 survive (SDII, days ≥1 in, top-5 share); growing-season total, days ≥2 in, max1 do not.
- **Verdict: WEAKENED.** Stop using the count as a summary; subordinate to Q3a, under which none are trends.

### Q3f — annual total (+0.96, CI −1.25 to 3.12) and recharge-season total (−0.81, CI −1.99 to 0.60) not rising
- **Verdict: STANDS.** Reproduced exactly; unaffected by the 2002 step (total step p=0.06, slope never significant). The most robust Q3 result and, after this review, the only one to state without qualification.

### Coupling — lag 1 month, r 0.45
- **Checks (reviewer).** Invariant to the 12-UTC day-end (r at lag 1: 0.454–0.457 across 0/6/12/18 UTC), to bypassing daily binning, and to using COOP instead of AORC. Daily-resolution cross-correlation peaks at **2–3 days** and decays monotonically — no local maximum near 30 days.
- **Verdict: STANDS as a statistic; WEAKENED as a physical statement.** "1 month" is the coarsest bin that captures a fast onset plus a long tail, not a transit time. Report both: onset within days; monthly correlation maximised at lag 1.

---

## 2026 (lay report)

### Recharge season 13.6 in = 10th driest of 75; COOP-only 12.4 = 4th of 66
- **Checks (reviewer).** Both reproduce exactly. "KUNO raw 12.8 = 8th" as a *KUNO-only* rank does not reproduce (3rd of 28 — KUNO has only 28 seasons); the 8th-of-75 figure is the unadjusted spliced record and must be labelled as such. Window sensitivity: Sep–Feb 10th, Oct–Mar 6th, Nov–Apr 15th, Aug–Jan 12th.
- **Verdict: STANDS with corrections.** Label the unadjusted figure correctly; state the rank as 6th–15th across defensible windows or state Sep–Feb as the pre-registered choice.

### March–June 2026 the lowest on record at Hardy; 4th-lowest of 46 at Mammoth
- **Checks (reviewer).** Hardy 560 cfs, rank 1 of **25** (not 24), median **1,450** (not 1,255 — the earlier figure was the mean of the daily climatological medians, not the median of yearly means); Mammoth 291, rank 4 of 46, median 418.
- **Verdict: STANDS; two numbers corrected.** 2026 is 39 % of the Hardy median, not 45 % — the correction strengthens the claim.

---

## Required changes (punch list)

Conclusion-changing (do before the report is cited again):
1. **Q3 reframe.** Replace "more intense, not detectably wetter" with: annual and recharge-season totals not rising; AORC storm-sharpness indices step up at the 2002 radar onset and trend flat-to-negative within each era; no intensification detectable at the gauge over 1949–2025 or over 1981–2025. Add the step-term table and the pre/post-2002 product-vs-gauge comparison to Phase 6; remove the "6/10" count from the abstract and synthesis.
2. **Q7** → untestable with current data; **Q6** → no cadence detectable, with the power statement.
3. **Q4 Hardy** → report the placebo (+10.7 %) and the 90-day-skip result (+8 %, CI spans zero); keep Mammoth with its placebo (0 %).
4. **Q8** → 23 ft 20–29 yr and 20 ft 10–12.5 yr with the 1982 crest as historical information as the headline case; swap the skew sensitivity for the 1982 sensitivity.

Strengthen (the evidence exists, the report undersells it):
5. **Hardy low-flow rise** → lead with the Hardy/Mammoth ratio trend (+0.0124/yr, p=0.002) and the field-measurement stage decline (−0.015 ft/yr, p<0.0001); retire "source-dependent, not a finding"; correct the datum-records limitation (two revisions, 2022+) and the "~1 % in every era" figure (report era means with sd).
6. **Q5** → add the field-measurement trend; **Q2** → add the q=0.90 quantile regression and disclose the 2008 mean shift as post hoc.

Corrections of wording and numbers:
7. Mammoth "≈0 on all three sources" → PRISM fits marginally negative, one specification p=0.049.
8. Buffer-vs-polygon attribution → threshold crossing, not geometry.
9. West Plains days ≥1 in → report with ratio sensitivity 1.00–1.10; note the residual 1998 step in SDII and recharge season.
10. Coupling → "onset within 2–3 days; monthly correlation maximised at lag 1 month".
11. 2026 → Hardy Mar–Jun n=25, median 1,450; label the 12.8-in/8th figure as the unadjusted spliced record; give the window range.
12. BFI → not evidence against base-flow change; Pettitt p-values beside their years; note the 2008-vs-2013 change-point discrepancy.
13. §6.1 → effective n by water-year block; flag Mammoth recession fits with r²<0.75; add a Watson–Williams test across decades.

Data that would resolve the remaining open questions: NOAA AORC v1.1 homogeneity documentation and a one-cell AORC re-pull at the gauge; an independent gridded product without a 2002 input change; quantile-based COOP/KUNO homogenisation; PeakFQ/EMA with the 1982 crest; synoptic seepage runs Mammoth → South Fork → Hardy; the USGS shift tables (the field and channel measurements are now in hand).

Reviewer reports: `docs/review_phase8/` (brief.md, review-baseflow.md, review-floods.md, review-precip.md; review-codex.md added when it lands).

---

## Corrections applied (2026-08-25, same branch)

Punch-list items 1–10, 12 and 13 were implemented in the runners and the report (commits f20ce8e, e0ad1da, b1cffce, 0f746a6, 2754289; item 11 is the lay report, corrected separately in 53ded04). Tests 181 → 214. The corrected headline statements, as now rendered from the runners:

- **Q3.** Annual and recharge-season totals not rising. AORC storm-sharpness indices step at 2002 (SDII slope with a step term −0.002/decade, p = 0.86; step p = 0.001) and trend flat-to-negative within each era (0 of 6 rising); over identical years AORC SDII +36 % vs gauge +1 % while totals agree (+9 % vs +11 %). No intensification detectable.
- **Q4 Hardy.** +30.7 % against a placebo mean of +9.7 % that 11 % of random sets reach; +8.0 % (CI −8.1 to +22.8) at a 90-day skip; placebo-corrected ≈ +21 %. Mammoth: placebo +0.6 %, 0 of 200 sets reach +26 % — stands.
- **Q7.** Untestable with the current record (Fisher power 0.08 against a 2.5× effect).
- **Q8.** 23 ft: 20–29 yr with the 1982 crest as historical information (H = 44 → 20.1 yr; H = 90 → 24.5 yr), quoted in place of the systematic-only 29.4.

Two findings that emerged while implementing, beyond the reviewers' lists:
- The WY2008 (difference) vs WY2013–14 (ratio) change-point discrepancy noted under "BFI; Pettitt" **resolves**: on complete water years both the Hardy−Mammoth difference and the log-ratio put the change after WY2014; the WY2008 reading was an incomplete-final-year artefact.
- Watson–Williams across decades: "no drift" in peak timing holds for the 89-year Imboden series (p = 0.32) but **not** for Hardy's three-decade series (p = 0.027) — Hardy's annual-peak dates have moved later across 2000s → 2010s → 2020s. With n ≈ 6–9 per decade this is reported as a result on the short series, not as a change in the river's regime, and the §6.1 verdict is now stated separately for the two gauges.

Verification: see the Phase 8 corrections review and fresh-clone check recorded in the session ledger; the Codex generalist review is appended to `docs/review_phase8/` when it lands.
