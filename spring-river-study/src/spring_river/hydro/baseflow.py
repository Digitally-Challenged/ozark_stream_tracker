"""Eckhardt recursive base-flow filter (spec §2.2). Lyne-Hollick check lands
with the Phase 4 analysis plan; the ledger only needs Eckhardt BFI."""
import numpy as np


def eckhardt(q: np.ndarray, alpha: float = 0.98, bfi_max: float = 0.8) -> np.ndarray:
    q = np.asarray(q, dtype="float64")
    b = np.empty_like(q)
    b[0] = q[0] * bfi_max
    denom = 1.0 - alpha * bfi_max
    for t in range(1, len(q)):
        b[t] = ((1 - bfi_max) * alpha * b[t - 1] + (1 - alpha) * bfi_max * q[t]) / denom
        b[t] = min(b[t], q[t])
    return b


def bfi(q: np.ndarray, **kw) -> float:
    q = np.asarray(q, dtype="float64")
    return float(eckhardt(q, **kw).sum() / q.sum())
