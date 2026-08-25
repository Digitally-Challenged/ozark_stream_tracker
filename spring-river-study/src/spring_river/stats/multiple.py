"""Benjamini-Hochberg FDR control across the Q3 index family (spec §2.6)."""
import numpy as np


def benjamini_hochberg(p: np.ndarray, q: float = 0.05) -> tuple[np.ndarray, np.ndarray]:
    p = np.asarray(p, dtype="float64")
    m = len(p)
    order = np.argsort(p)
    ranked = p[order] * m / np.arange(1, m + 1)
    adj_sorted = np.minimum.accumulate(ranked[::-1])[::-1]
    adj = np.empty(m)
    adj[order] = np.minimum(adj_sorted, 1.0)
    return adj <= q, adj
