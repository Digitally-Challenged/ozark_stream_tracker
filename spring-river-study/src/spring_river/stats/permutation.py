"""Q7: is a quiet year more likely after a major-flood year? (spec §2.3)"""
from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class ConditionalRateResult:
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


def conditional_rate_test(
    major: np.ndarray, quiet: np.ndarray, n_perm: int = 10000, seed: int = 0
) -> ConditionalRateResult:
    major = np.asarray(major, dtype=bool)
    quiet = np.asarray(quiet, dtype=bool)
    n = len(major)
    base = float(quiet.mean())
    observed = _rate_after(major, quiet)
    diff = observed - base
    rng = np.random.default_rng(seed)
    n_major = int(major[:-1].sum())
    if n_major == 0:
        return ConditionalRateResult(
            n, 0, observed, base, float("nan"), float("nan"), float("nan"), float("nan")
        )
    perm = np.array([_rate_after(rng.permutation(major), quiet) - base for _ in range(n_perm)])
    p = float((perm >= diff).mean())
    boot = np.array(
        [
            _rate_after(major[idx := np.sort(rng.integers(0, n, n))], quiet[idx]) - quiet[idx].mean()
            for _ in range(n_perm)
        ]
    )
    boot = boot[~np.isnan(boot)]
    lo, hi = np.percentile(boot, [2.5, 97.5]) if len(boot) else (float("nan"), float("nan"))
    return ConditionalRateResult(n, n_major, observed, base, float(diff), float(lo), float(hi), p)
