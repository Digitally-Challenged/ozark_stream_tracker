"""Q7: is a quiet year more likely after a major-flood year? (spec §2.3)"""
from dataclasses import dataclass

import numpy as np
from scipy import stats


@dataclass(frozen=True)
class ConditionalRateResult:
    """Conditional quiet-year rate after a major-flood year vs the base rate.

    diff = rate_after_major - base_rate. diff_lo/diff_hi are the Clopper-Pearson
    exact 95% interval on rate_after_major (k quiet-after-major of n_major
    prior-major years), shifted by base_rate; they bracket diff. p is a
    permutation p-value with n_major held fixed.
    """

    n_years: int
    n_major: int
    rate_after_major: float
    base_rate: float
    diff: float
    diff_lo: float
    diff_hi: float
    p: float


def _rate_after(major: np.ndarray, quiet: np.ndarray) -> float:
    idx = np.flatnonzero(major[:-1])
    if len(idx) == 0:
        return float("nan")
    return float(quiet[idx + 1].mean())


def _clopper_pearson(k: int, n: int, level: float = 0.95) -> tuple[float, float]:
    a = (1 - level) / 2
    lo = 0.0 if k == 0 else float(stats.beta.ppf(a, k, n - k + 1))
    hi = 1.0 if k == n else float(stats.beta.ppf(1 - a, k + 1, n - k))
    return lo, hi


def conditional_rate_test(
    major: np.ndarray, quiet: np.ndarray, n_perm: int = 10000, seed: int = 0
) -> ConditionalRateResult:
    major = np.asarray(major, dtype=bool)
    quiet = np.asarray(quiet, dtype=bool)
    n = len(major)
    base = float(quiet.mean())
    observed = _rate_after(major, quiet)
    diff = observed - base
    n_major = int(major[:-1].sum())
    if n_major == 0:
        return ConditionalRateResult(
            n, 0, observed, base, float("nan"), float("nan"), float("nan"), float("nan")
        )
    rng = np.random.default_rng(seed)
    prior, last = major[:-1], major[-1:]
    perm = np.array(
        [
            _rate_after(np.concatenate([rng.permutation(prior), last]), quiet) - base
            for _ in range(n_perm)
        ]
    )
    p = float(((perm >= diff).sum() + 1) / (n_perm + 1))  # plus-one Monte Carlo correction
    k = int(quiet[np.flatnonzero(prior) + 1].sum())
    lo, hi = _clopper_pearson(k, n_major)
    return ConditionalRateResult(
        n, n_major, observed, base, float(diff), lo - base, hi - base, p
    )


def conditional_rate_power(n_major: int, n_other: int, base_rate: float,
                           alt_rates: tuple[float, ...] = (0.2, 0.4, 0.6, 0.8),
                           n_sim: int = 4000, alpha: float = 0.05, seed: int = 1):
    """Power of the Q7 conditional-rate test (Fisher exact) by true rate.

    Phase 8 (review.md item 2). With a handful of major-flood years the design
    cannot detect any plausible effect, so a null result is not evidence of no
    effect — it is no result. This reports what the test could have found.
    """
    import pandas as pd

    rng = np.random.default_rng(seed)
    rows = []
    for p_alt in alt_rates:
        a = rng.binomial(n_major, p_alt, n_sim)
        b = rng.binomial(n_other, base_rate, n_sim)
        rej = sum(stats.fisher_exact([[int(x), n_major - int(x)],
                                      [int(y), n_other - int(y)]])[1] < alpha
                  for x, y in zip(a, b))
        rows.append({"true_rate_given_major": p_alt, "power": rej / n_sim})
    return pd.DataFrame(rows).assign(n_major=n_major, n_other=n_other,
                                     base_rate=base_rate, alpha=alpha)
