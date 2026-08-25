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
    p = float((perm >= diff).mean())
    k = int(quiet[np.flatnonzero(prior) + 1].sum())
    lo, hi = _clopper_pearson(k, n_major)
    return ConditionalRateResult(
        n, n_major, observed, base, float(diff), lo - base, hi - base, p
    )
