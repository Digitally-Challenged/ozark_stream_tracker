import numpy as np

from spring_river.stats.multiple import benjamini_hochberg


def test_bh_matches_known_example():
    p = np.array([0.01, 0.04, 0.03, 0.20, 0.50])
    rejected, adj = benjamini_hochberg(p, q=0.05)
    # sorted: .01,.03,.04,.20,.50 -> adj: .05,.0667,.0667,.25,.50
    assert rejected.tolist() == [True, False, False, False, False]
    assert abs(adj[0] - 0.05) < 1e-9
    assert abs(adj[1] - 0.0667) < 1e-3


def test_bh_all_null():
    rejected, _ = benjamini_hochberg(np.array([0.3, 0.6, 0.9]))
    assert not rejected.any()
