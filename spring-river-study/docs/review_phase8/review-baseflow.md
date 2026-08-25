# Phase 8 adversarial review — base-flow and gauge conclusions

Reviewer scope: Q1 (Mammoth + Hardy attribution, residual trends, BFI, Pettitt), the Hardy
low-flow gain and its rating-artefact test, Q5 rating drift, Q4 post-flood base flow.
All checks run read-only from `/Users/COLEMAN/orca/workspaces/ozark_stream_tracker/goatfish/spring-river-study`
with `uv run`; scratch scripts in `scratchpad/phase8/baseflow/`. Nothing in the repo was modified.

Every baseline number in the brief that I re-ran reproduced exactly. The attacks below are
about model form, alternative specifications, and independent evidence — not arithmetic.

---

## Claim 1 — Mammoth residual trend is ≈0 on all three basin precip series

**Claim.** `docs/phase4_baseflow.md:20` — residual Sen slope −0.00126 log-cfs/yr
(95% CI −0.00326 to +0.00122), n=42, OLS R²=0.58; brief states "≈0 on all three basin series",
i.e. no non-climatic decline at the vent.

**Strongest attack.** The 365-d/prior-365-d window pair is one choice among many, and the
"≈0 on all three sources" framing hides that the two PRISM series already sit at the edge of
significance in the *negative* direction. If the null result is a window artefact, a longer
memory window — appropriate for a karst spring whose recharge memory is plausibly multi-year
(the study's own Mammoth recession k = 188 days implies long storage) — should expose a decline.

**What would falsify it.** A residual trend whose CI excludes zero on the negative side under a
defensible alternative predictor window or an added PET term.

**Checks run.** `scratchpad/phase8/baseflow/q1_alt.py` (windows 180/545/730 d, precip-only,
single-window; all three basin sources) and `pet2.py` (West Plains COOP maxt as a PET surrogate,
365-d and 120-d antecedent means, ACIS StnData, coverage 0.895).

Mammoth residual Sen slope (log-cfs/yr) by window and source:

| window | AORC | PRISM-polygon | PRISM-buffer |
|---|---|---|---|
| 365 (reported) | −0.0013 [−0.0033, +0.0012] p=0.36 | −0.0022 [−0.0048, +0.0001] p=0.062 | −0.0022 [−0.0050, +0.0005] p=0.087 |
| 180 | +0.0005 [−0.0018, +0.0028] p=0.71 | −0.0010 [−0.0040, +0.0011] p=0.49 | −0.0012 [−0.0039, +0.0012] p=0.31 |
| 545 | −0.0013 [−0.0043, +0.0015] p=0.37 | −0.0032 [−0.0060, +0.0002] p=0.058 | −0.0027 [−0.0058, +0.0006] p=0.11 |
| 730 | −0.0021 [−0.0052, +0.0011] p=0.16 | **−0.0035 [−0.0066, −2.7e-7] p=0.049** | −0.0030 [−0.0065, +0.0003] p=0.067 |

PET/temperature (AORC, 365-d): base −0.0013 p=0.363 → +maxt365 −0.0003 p=0.880 →
+both temp terms +0.0001 p=0.942. Adding evapotranspiration pushes the residual *toward* zero,
never negative.

**Verdict: WEAKENED.** The conclusion is right on the primary series and is not manufactured by
the window choice or by an omitted PET term — but "≈0 on all three basin series" overstates the
agreement. On PRISM-polygon the 730-d specification yields a *significant* negative residual
(p=0.049), and the reported 365-d PRISM results (p=0.062, p=0.087) are marginal with CIs almost
entirely below zero. The honest statement is: no significant non-climatic decline on the primary
AORC series at any window; PRISM-based fits are consistently, marginally negative, and one
specification crosses p<0.05. This is a source-sensitivity finding of the same kind the study
already flags for Hardy, and it should be reported symmetrically.

**What would settle it.** A basin precip series independent of PRISM's gauge network over the
polygon (e.g. Stage IV / MRMS for the post-2002 half, or a Livneh/gridMET cross-check), plus
pre-registering the window length on physical grounds (spring recession k, tracer transit time)
rather than by convention.

---

## Claim 2 — Hardy residual +0.0203/yr is source-dependent, "not a finding"

**Claim.** `docs/phase4_baseflow.md:42` — Hardy residual +0.0203 [+0.0092, +0.0291] on AORC,
but +0.0103 [−0.0006, +0.0191] on PRISM-polygon, so the study declines to call it a finding.

**Strongest attack (in the study's own favour).** This is the one place where the study is too
conservative rather than too aggressive. The precip-only model — the correct comparison, since
ONI is never significant at either gauge — is significant on *all three* sources. More
importantly, the study never used the single best available climate control: Mammoth Spring's own
min7. Mammoth and Hardy share the same recharge climate; Mammoth min7 absorbs precipitation,
ONI, PET, and any gridded-precip bias simultaneously. If the Hardy rise is climate, it disappears
against Mammoth.

**What would falsify it.** log(Hardy min7 / Mammoth min7) showing no trend.

**Checks run.** `scratchpad/phase8/baseflow/q1_hardy.py`, `q1_alt.py`.

- Hardy residual, precip-only (drop ONI): AORC +0.0213 [+0.0108, +0.0293] p=1.4e-5;
  PRISM-polygon +0.0116 [+0.0017, +0.0208] p=0.021; PRISM-buffer +0.0110 [+0.0027, +0.0227] p=0.016.
  **All three sources significant** once the never-significant ONI term is removed.
- Hardy residual with Mammoth min7 added as a predictor: +0.0121 [+0.0016, +0.0209] p=0.016, R² 0.61.
- **log(Hardy min7 / Mammoth min7) Sen trend: +0.0124/yr [+0.0028, +0.0219], p=0.0023, n=24.**
  This is a pure ratio — no precipitation model at all, so no window, source, or model-form
  choice can manufacture it. Pettitt on the log ratio: change after WY 2014 (K=101, p=0.029).
- Windows 180/545/730 on AORC: +0.0199, +0.0179, +0.0150, all CIs excluding zero.
- Adding PET terms: +0.0186 to +0.0205, unchanged.

**Verdict: WEAKENED (the disclaimer is wrong, not the number).** The "source-dependent, not a
finding" hedge is not supported. The Hardy rise relative to Mammoth is robust to the precip
source, the predictor window, the ONI term, PET, and to abandoning the precipitation model
entirely. The source-dependence of the reported figure is an artefact of one weak, insignificant
regressor (ONI, CI −0.080 to +0.176) eating degrees of freedom in an n=24 fit. Report the ratio
trend as the primary evidence and demote the regression.

**What would settle it.** Already settled by the ratio; nothing further needed for the trend's
existence. Its *cause* is Claim 3.

---

## Claim 3 — the Hardy low-flow gain is real water, not a rating artefact

**Claim (brief, controller analysis).** Hardy min7 − Mammoth min7: 2002–07 mean ~39 cfs,
2009–25 ~128 cfs, step at WY2008; 66 field measurements agree with rating-computed flow within
~1% in every era, so the gain is real water.

**Strongest attacks.** (a) The step could be a datum change or gauge relocation. (b) The field-vs-
rating agreement is potentially *circular*: USGS shifts the rating to match the measurements, so
of course they agree — agreement demonstrates the rating tracks the measurements, not that either
tracks reality.

**What would falsify it.** A datum revision or site move dated 2007–2009; or evidence that the
apparent gain follows only from a re-rating with no independent physical signal.

**Checks run.**

1. Reproduced the gain: `gain.py` — 2002–07 mean 39.3 cfs, 2009–25 mean 127.8 cfs. Exact match.
2. **Monitoring-location metadata** (`api.waterdata.usgs.gov/ogcapi/v0/collections/monitoring-locations/items?monitoring_location_number=07069305`):
   the site carries an explicit `revision_note`:
   *"From Dec 2022 to Dec 2024, datum value of 342.49 was revised to 342.73 ft above NAVD of 1988.
   Prior to Dec 2022, datum value of 340.91 ft was revised to 342.49 ft above NAVD of 1988."*
   Two datum revisions exist — **but both are dated Dec 2022 and later, not 2007–2009**, and both
   are gauge-datum bookkeeping (revisions to the reported elevation of the datum plane), not a
   site move. Coordinates, drainage area (845 mi²), and station name are unchanged across the
   record. `time-series-revisions` returns 0 records for this site.
3. **The circularity test.** Field measurements carry *measured stage* alongside *measured
   discharge* — both independent of the rating. If the gain were a re-rating, measured stage at a
   given measured discharge would be constant while the rating moved. It is not
   (`fm.py`, n=360 stage + 142 discharge field readings, joined on `field_visit_id`):
   measured stage in the 330–520 cfs band falls 3.44 ft (2004) → 3.21 (2007) → 3.04 (2011) →
   2.98 (2018) → 2.97 (2026). Normalizing each measurement to 400 cfs and taking the Sen trend:
   **−0.0150 ft/yr [−0.0214, −0.0100], p<0.0001, n=20 WY** (`q5b.py`). The channel really
   degraded; the rating followed physical measurements, it did not create them.
4. Independent of any rating or datum, the ratio test in Claim 2 (+0.0124/yr, p=0.002) uses only
   two discharge series and reproduces the rise.

**Verdict: STANDS**, with two corrections to the supporting text.

- The datum-artefact hypothesis is **refuted for the WY2008 step**, but the study must stop saying
  "no USGS datum records reviewed" (`docs/phase4_baseflow.md:203`, brief limitations): two datum
  revisions **do** exist and are now documented above. They post-date 2022 and cannot explain a
  2008 step, but a reader who finds them independently will assume the study missed them.
- The "~1% in every era" figure is **not reproducible as stated**. Joining field discharge to the
  same-day DV value (`circ.py`, n=157 low-flow visits): 2001–07 mean +1.3% (median +1.8%,
  sd 5.0), 2008–14 **−2.6%** (median −2.1%, sd 4.7), 2015–25 −0.4% (sd 3.5), 2026 +4.3%.
  The 2008–14 era is off by −2.6%, not 0.0%, and the scatter (sd ~4–5%) is far larger than the
  quoted means. The direction of the error is harmless (it does not create the gain) but the
  number as written is wrong and the era means should carry their standard deviations.
- Note also that the ~1% agreement is, on its own, a **weak** argument for the reason the attack
  states — it is close to circular. The load-bearing evidence is the independent measured-stage
  decline (item 3) and the Mammoth ratio (item 4). Lead with those.

**What would settle the cause.** Synoptic seepage runs (a same-day discharge traverse Mammoth →
South Fork → Hardy at low flow) would partition the ~90 cfs among the South Fork (~34 cfs per the
brief), unmeasured tributaries, and diffuse groundwater. Absent that, the attribution of the
gain's *source* remains open even though its *existence* is now solid.

---

## Claim 4 — Q5 rating drift: stage at fixed discharge is falling; the change is at the downstream control

**Claim.** Stage at 1,000 cfs −0.019 ft/yr [−0.021, −0.016], n=19 WY; at 400 cfs −0.008
[−0.013, −0.005]; bridge cross-section stable.

**Strongest attack.** Both numbers derive from the same IV stage/discharge pairs, and the
discharge in those pairs is *itself produced by the rating*. A drifting rating trivially produces
a drifting "stage at fixed discharge" with no channel change whatsoever. The whole result could be
an internal property of USGS's rating maintenance.

**What would falsify it.** Independently measured stage at independently measured discharge
showing no decline.

**Checks run.** `q5.py` reproduces `reports/tables/phase4_rating_drift.parquet` exactly (3.943 ft
at 1000 cfs in WY2008 → 3.522 in WY2025). `q5b.py` repeats the analysis on field measurements
only — measured stage regressed on log10(measured discharge), normalized to 400 cfs, annual means,
Sen trend: **−0.0150 ft/yr [−0.0214, −0.0100], p<0.0001, n=20 water years, 2003–2026**.

**Verdict: STANDS, and is understated.** The independent field-measurement check confirms the
drift, and it is *nearly twice as steep* as the IV-derived 400 cfs figure (−0.0150 vs −0.0079
ft/yr). It also extends the record four years earlier than the IV series (2003 vs IV_START
2007-10-01), covering the 2006-09-23 event the study had to omit from the shift table
(`docs/phase4_baseflow.md:115`): measured stage@400 was 3.36 (2003), 3.41 (2004), 3.48 (2005),
3.25 (2007) — a ~0.2 ft drop bracketing that event, consistent with the study's "largest step
2008→2010" narrative starting earlier than the IV data can see.

**Recommendation.** Add the field-measurement trend to Q5. It converts the section from
"IV-derived stage-at-flow only" (its stated limitation, line 203) into a result with independent
corroboration, and it retires the "events before IV_START have no pairs" gap.

---

## Claim 5 — Q4 post-flood base flow is elevated ~26% (Mammoth) / ~31% (Hardy)

**Claim.** 6-month post-flood base flow vs 3 matched non-flood years: Mammoth +26.0%
[15.7, 41.0], Hardy +30.7% [19.6, 38.7], n=6, descriptive not causal.

**Strongest attack.** The matching selects the 3 nearest control years on standardized distance
from a pool of ~15–40 candidates. With n=6 events and heavy control reuse (Hardy: only 10 unique
control years across 18 selections), the procedure has substantial freedom to pick dry controls,
and the flood years are by construction wet years. The bootstrap CI explicitly excludes matching
uncertainty (`postflood.py:207-215`), so the stated band cannot detect this. The right test is a
placebo: run the identical pipeline on random *non-flood* pseudo-events. If a placebo reproduces
+30%, the procedure — not the floods — is producing the effect.

**What would falsify it.** A placebo distribution centred near the reported effect, or collapse
under alternative k / skip days.

**Checks run.** `q4b.py` — identical `matched_comparison`/`paired_summary` pipeline, varying
k ∈ {1,3,5,8} and `RECESSION_SKIP_DAYS` ∈ {15,30,60,90}, plus 200 placebo trials per gauge in
which the six event dates are moved to six randomly chosen non-flood years (same calendar
day-of-year, so seasonality is preserved).

| | Mammoth | Hardy |
|---|---|---|
| k=1 | +25.5 [12.2, 39.8] | +36.8 [14.3, 60.8] |
| k=3 (reported) | +26.0 [15.7, 41.0] | +30.7 [19.6, 38.7] |
| k=5 | +20.4 [10.6, 35.3] | +24.7 [15.3, 33.7] |
| k=8 | +18.9 [12.0, 28.6] | +22.3 [12.3, 32.0] |
| skip 15 d | +25.4 | +30.6 |
| skip 60 d | +19.1 | +23.9 |
| skip 90 d | +21.9 [11.7, 31.3] | **+8.0 [−8.1, +22.8]** |
| **placebo (n=200)** | **mean +0.0%, sd 7.5, p95 +12.1, P(≥26.0) = 0.000** | **mean +10.7%, sd 16.6, p95 +39.0, P(≥30.7) = 0.115** |

**Verdict: split.**

- **Mammoth: STANDS.** The placebo distribution is centred on zero (mean +0.0%, sd 7.5) and no
  trial in 200 reached +26%. The matching procedure has no intrinsic bias at this gauge, and the
  effect is stable from +18.9% to +26.0% across every k and skip variant. This is stronger
  evidence than the study currently claims for it.
- **Hardy: WEAKENED, materially.** The placebo mean is **+10.7%**, i.e. roughly a third of the
  reported +30.7% is reproduced by randomly chosen non-flood "events" — the matching procedure
  *is* biased at Hardy, presumably because its 24-year record gives a thin, wet-skewed candidate
  pool and heavy reuse (10 unique controls for 18 slots). 11.5% of random placebos beat the real
  effect, which is not a p-value but is far from negligible. And at a 90-day recession skip the
  Hardy effect collapses to +8.0% with a CI spanning zero, meaning much of the "post-flood base
  flow" at Hardy is still recession water at 30 days — exactly the contamination
  `RECESSION_SKIP_DAYS` was raised from 7 to 30 to remove (`postflood.py:20-22`). Hardy's flashier
  response (median recession k 13.9 d vs Mammoth's 188 d) does not explain this away: a short k
  should make 30 days *more* than sufficient, so the persistence to 90 days is either a genuine
  slow limb or the wet-year selection the placebo detects.

**Recommendation.** Report the placebo result alongside both effects, and report Hardy as
placebo-corrected (~+20%) or drop it. State the skip-day sensitivity: Mammoth is flat across
15–90 d, Hardy is not.

**What would settle it.** More events (the binding constraint — n=6 with 24 years at Hardy), or a
continuous dose-response framing (post-flood base-flow anomaly regressed on event peak magnitude
across all peaks, not just ≥16 ft) which would use the whole record instead of six binary
comparisons and would not need matched controls at all.

---

## Claim 6 — BFI shows no trend at either gauge; Pettitt change-points as documented

**Claim.** `docs/phase4_baseflow.md:57-68` — Eckhardt and Lyne-Hollick BFI Sen slopes all with
CIs spanning zero at both gauges; Mammoth Pettitt after WY2008 (p=0.260), Hardy after WY2013
(p=0.013).

**Strongest attack.** BFI is a *ratio* (base flow / total flow). At a spring-fed river where BFI
is already near 1, it is nearly insensitive to a change in the absolute base-flow rate — the
denominator moves with the numerator. A no-trend BFI is therefore near-uninformative about
whether base flow changed, yet it is presented as corroborating evidence.

**What would falsify it.** Nothing — the claim as stated is a true statement about BFI.

**Checks run.** Read `docs/phase4_baseflow.md:57-68` and `hydro/baseflow.py`. I did not re-run
the filters; the reported slopes (Mammoth Eckhardt 2.31e-05 [−4.6e-05, +1.17e-04]; Hardy
Lyne-Hollick 0.0039 [−0.0012, +0.0088], the largest) are all far from significance. Note the
Hardy Lyne-Hollick MK p=0.097 is the closest, and it is positive — directionally consistent with
the Claim 2/3 gain rather than contradicting it.

**Verdict: STANDS as stated, but its evidentiary weight is overstated.** BFI's null result should
not be cited as evidence against a base-flow change; it is a low-power test at these gauges. The
Pettitt result deserves a note the study omits: Mammoth's WY2008 change-point is **not
significant** (p=0.260) and should not be described in the same breath as Hardy's WY2013
(p=0.013). Separately, my Pettitt on the Hardy/Mammoth log ratio finds the change after
**WY2014** (K=101, p=0.029), close to Hardy's own WY2013 — the two are consistent, but note that
neither lands on the WY2008 step the low-flow-gain analysis emphasizes. The gain series
(difference of min7) steps at 2008; the ratio and the raw Hardy min7 change around 2013–14.
That discrepancy is unexplained in the current text and a reader will notice it.

---

## Ranked findings the study owner most needs to hear

1. **Q4 Hardy fails a placebo test; Mammoth passes decisively.** Random non-flood pseudo-events
   reproduce +10.7% at Hardy (11.5% of 200 trials beat the real +30.7%), and the effect falls to
   +8.0% with a CI spanning zero at a 90-day recession skip. Mammoth's placebo is +0.0% with
   0/200 trials reaching +26%. Report the placebo for both; Hardy's headline number is roughly a
   third procedural.

2. **The Hardy gain is more defensible than the study says, and by better evidence than the
   ~1% field-measurement agreement.** `log(Hardy min7 / Mammoth min7)` rises +0.0124/yr
   (p=0.0023, n=24) with no precipitation model at all, and independently measured stage at
   ~400 cfs falls −0.0150 ft/yr (p<0.0001, n=20 WY, 2003–2026) — a physical channel change no
   re-rating could fabricate. Drop the "source-dependent, not a finding" hedge (its source
   sensitivity comes from the never-significant ONI term: precip-only fits are significant on all
   three sources). Also fix two supporting details: two USGS datum revisions **do** exist for
   07069305 (dated Dec 2022 and later — they cannot explain a 2008 step, but the limitation
   "no datum records reviewed" is now wrong), and the "~1% in every era" agreement is actually
   +1.3% / **−2.6%** / −0.4% / +4.3% with sd ~4–5%.

3. **"Mammoth residual ≈0 on all three basin series" is too strong.** On PRISM-polygon with a
   730-day predictor window the residual is significantly negative (−0.0035/yr, CI upper bound
   −2.7e-7, p=0.049), and the reported 365-day PRISM fits are marginal (p=0.062, p=0.087) with
   CIs almost wholly below zero. The AORC primary result is robust to windows 180–730 d and to
   adding a PET term, so the conclusion survives — but the cross-source agreement should be
   reported with the same candour the study applies to Hardy, not asserted as unanimous.

---

Report path: `/private/tmp/claude-501/-Users-COLEMAN-orca-workspaces-ozark-stream-tracker-goatfish/c3f6ce55-ea99-41db-b63e-c5b903b8fa85/scratchpad/phase8/review-baseflow.md`
Scratch scripts: `scratchpad/phase8/baseflow/{load,q1_alt,q1_hardy,gain,fm,circ,q4b,q5,q5b,pet2}.py`
