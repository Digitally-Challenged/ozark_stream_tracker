"""Non-parametric trend tests (spec §2.2, §2.6).

Mann-Kendall S with tie-corrected variance; Sen's slope with the Gilbert
(1987) rank-based confidence interval; Pettitt (1979) single change-point.
Every public function returns effect size + CI + n so callers can satisfy
the "no bare p-values" rule.
"""
from dataclasses import dataclass

import numpy as np
from scipy import stats

MIN_N = 8


@dataclass(frozen=True)
class TrendResult:
    n: int
    s: float
    z: float
    p: float
    slope: float
    slope_lo: float
    slope_hi: float
    intercept: float


@dataclass(frozen=True)
class PettittResult:
    n: int
    k: float
    change_index: int
    p: float


def _mk_variance(x: np.ndarray) -> float:
    n = len(x)
    var = n * (n - 1) * (2 * n + 5)
    _, counts = np.unique(x, return_counts=True)
    ties = counts[counts > 1]
    var -= np.sum(ties * (ties - 1) * (2 * ties + 5))
    return var / 18.0


def mann_kendall(x: np.ndarray) -> tuple[float, float, float]:
    x = np.asarray(x, dtype="float64")
    n = len(x)
    s = 0.0
    for i in range(n - 1):
        s += np.sign(x[i + 1 :] - x[i]).sum()
    var = _mk_variance(x)
    if var == 0 or s == 0:
        return float(s), 0.0, 1.0
    z = (s - 1) / np.sqrt(var) if s > 0 else (s + 1) / np.sqrt(var)
    p = 2 * (1 - stats.norm.cdf(abs(z)))
    return float(s), float(z), float(p)


def sen_slope(
    x: np.ndarray, t: np.ndarray | None = None, alpha: float = 0.05
) -> tuple[float, float, float, float]:
    x = np.asarray(x, dtype="float64")
    n = len(x)
    t = np.arange(n, dtype="float64") if t is None else np.asarray(t, dtype="float64")
    i, j = np.triu_indices(n, k=1)
    dt = t[j] - t[i]
    keep = dt != 0
    slopes = np.sort((x[j] - x[i])[keep] / dt[keep])
    slope = float(np.median(slopes))
    n_pairs = len(slopes)
    c = stats.norm.ppf(1 - alpha / 2) * np.sqrt(_mk_variance(x))
    m1 = int(np.floor((n_pairs - c) / 2))
    m2 = int(np.ceil((n_pairs + c) / 2))
    lo = float(slopes[max(m1, 0)])
    hi = float(slopes[min(m2, n_pairs - 1)])
    intercept = float(np.median(x - slope * t))
    return slope, lo, hi, intercept


def trend_test(
    x: np.ndarray, t: np.ndarray | None = None, alpha: float = 0.05
) -> TrendResult:
    x = np.asarray(x, dtype="float64")
    t = np.arange(len(x), dtype="float64") if t is None else np.asarray(t, dtype="float64")
    ok = ~np.isnan(x) & ~np.isnan(t)
    x, t = x[ok], t[ok]
    if len(x) < MIN_N:
        raise ValueError(f"n < {MIN_N}: got {len(x)}")
    s, z, p = mann_kendall(x)
    slope, lo, hi, intercept = sen_slope(x, t, alpha)
    return TrendResult(len(x), s, z, p, slope, lo, hi, intercept)


def pettitt(x: np.ndarray) -> PettittResult:
    x = np.asarray(x, dtype="float64")
    n = len(x)
    sign = np.sign(x[None, :] - x[:, None])  # sign[i, j] = sign(x_j - x_i)
    u = np.array([sign[: t + 1, t + 1 :].sum() for t in range(n - 1)])
    k_idx = int(np.argmax(np.abs(u)))
    k = float(abs(u[k_idx]))
    p = float(min(1.0, 2 * np.exp(-6 * k**2 / (n**3 + n**2))))
    return PettittResult(n, k, k_idx, p)
