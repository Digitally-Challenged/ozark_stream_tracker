import numpy as np

from spring_river.hydro.baseflow import bfi, eckhardt


def test_eckhardt_never_exceeds_streamflow():
    rng = np.random.default_rng(7)
    q = np.exp(rng.normal(5, 1, size=500))
    b = eckhardt(q)
    assert np.all(b <= q + 1e-9)
    assert np.all(b >= 0)


def test_constant_flow_converges_to_bfi_max():
    q = np.full(400, 250.0)
    b = eckhardt(q, bfi_max=0.8)
    # fixed point of the recursion under constant flow is bfi_max * q
    assert abs(b[-1] - 0.8 * 250.0) < 1e-6


def test_bfi_between_0_and_1():
    rng = np.random.default_rng(7)
    q = np.exp(rng.normal(5, 1, size=500))
    assert 0 < bfi(q) < 1
