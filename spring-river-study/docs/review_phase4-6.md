# Adversarial review — Phases 4–6 (2026-08-25)

Reviewer: independent Codex pass (`codex:codex-rescue`) over f5b2ac2..7cd7d02, reading the repo directly.
Reviewer could not run the suite (uv cache permission in its sandbox); direct-run fallback gave 101 passed / 5 tempdir errors. Suite here: 110 passed.

**Verdict: NEEDS-CHANGES** (9 blocking, 4 non-blocking). Dispositions below; all blocking items were addressed or explicitly overruled before merge. Fixes: commit 6288d49 (libraries) + the runner commit following it. Effects on headline numbers are recorded in `spring_river_research.md` ("Phase 4–6 decisions"). A second Codex pass over the fixed tree is recorded at the bottom of this file.

## Blocking

| # | Finding | Disposition |
|---|---|---|
| 1 | Q1 temporal leakage: `p_recharge_in` is the full Sep–Feb total even when min7 ended before Feb (32/43 Mammoth, 13/24 Hardy years). `lowflow.py` | **Fixed.** Predictors are now strictly antecedent: trailing-365-day basin precip ending the day before the min7 window, the 365 days before that, and 6-month trailing ONI (`min7_dated` in `wateryear.py`). |
| 2 | Sen-slope CI rank off-by-one (`trends.py`). Hardy min7 lower bound 0.00798 → 0.00736. | **Fixed.** CI now from `scipy.stats.theilslopes`; test pins equality. |
| 3 | Grubbs-Beck drop without B17B conditional-probability adjustment; "parametric bootstrap" mislabel (`freq_lp3.py`). | **Fixed.** Default fit keeps all peaks and reports the count *flagged* below the GB threshold; dropping is opt-in and documented as unadjusted. Wording → nonparametric bootstrap. |
| 4 | Q7 CI bootstrap iid-resamples years and treats non-consecutive rows as adjacent; permutation can move a flag into the unusable last year (`permutation.py`). | **Fixed.** CI is now Clopper-Pearson on the conditional rate; permutation shuffles `major[:-1]` only so n_major is fixed. |
| 5 | Q5 "stage at fixed flow" is a ±5% band median; event-shift table labels the whole WY as "before" (`rating.py`). | **Fixed.** Local log-linear fit within ±20% evaluated at 400/1000 cfs; shifts compare ±365-day windows around each event. |
| 6 | Q3 recharge coverage gate accepts truncated boundary seasons (Jan–Feb 1981 passes as complete); basin `recharge_in` slope sign flips when corrected (`intensity.py`). | **Fixed.** Coverage is against the calendar length of Sep–Feb. |
| 7 | POT counts include partial WY 2026 as a full year in dispersion/trend (`phase5.py`). | **Fixed.** Dispersion/trend use complete water years only; partial WY reported separately. |
| 8 | All/approved-only sensitivity incomplete (Q1 HC3/Pettitt, POT trend/dispersion, Q6, lag correlation). | **Fixed.** Each runner now reports the approved-only variant for those items with a CHANGED flag rule. |
| 9 | Q4 CI ignores matching uncertainty / control-year reuse; matching uses post-window precip only; 7-day skip lets recession contaminate "base flow". | **Partly fixed, partly overruled.** Skip → 30 days; matching now on precip *and* pre-event base flow; `n_unique_controls` reported; report text states the CI reflects event-to-event variation only. Propagating matching uncertainty with n=6 events is not attempted — the result is presented as descriptive, not causal. |

## Non-blocking

| # | Finding | Disposition |
|---|---|---|
| 1 | `max3_in` rolling sum bleeds across Dec 31/Jan 1. | **Fixed** (rolled within calendar year). |
| 2 | Spec gaps: fixed rather than fitted BFImax; no linear-reservoir attribution; no spectral check for Q6. | **Deferred** to Phase 7/8 with the §2.5 items; recorded in `spring_river_research.md`. Spectral check on n=7 events is not informative. |
| 3 | Caption gaps (combined Phase 4 captions derive approval from Mammoth only; Phase 6 indices figure lacks period/approval; BH headline claims omit n). | **Fixed** in runners. |
| 4 | Q4 7-day post-flood skip. | **Fixed** (see blocking 9). |
