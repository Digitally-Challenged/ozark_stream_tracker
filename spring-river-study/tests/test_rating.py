import numpy as np
import pandas as pd

from spring_river.qa.rating import pair_iv, rating_shift_at_events, stage_at_flow


def _iv(n_days=800, seed=0, drop_after=None, drop_ft=0.5):
    rng = np.random.default_rng(seed)
    t = pd.date_range("2018-10-01", periods=n_days * 4, freq="6h")
    q = np.exp(rng.normal(np.log(600), 0.6, len(t)))
    stage = 3.0 + 2.0 * np.log10(q / 100)          # synthetic rating
    if drop_after is not None:
        stage = np.where(t >= pd.Timestamp(drop_after), stage - drop_ft, stage)
    iv_q = pd.DataFrame({"datetime": t, "value": q, "approved": True})
    iv_h = pd.DataFrame({"datetime": t, "value": stage, "approved": True})
    return iv_q, iv_h


def test_pair_iv_inner_join():
    iv_q, iv_h = _iv()
    pairs = pair_iv(iv_q, iv_h.iloc[10:])
    assert len(pairs) == len(iv_h) - 10
    assert list(pairs.columns) == ["datetime", "q_cfs", "stage_ft", "approved"]


def test_stage_at_flow_recovers_rating():
    pairs = pair_iv(*_iv())
    sf = stage_at_flow(pairs, flows=(400.0, 1000.0), tol=0.20, min_pairs=5)
    assert list(sf.columns) == ["wy", "flow_cfs", "stage_at_flow_ft", "stage_se_ft", "n_pairs"]
    for f in (400.0, 1000.0):
        row = sf[(sf["wy"] == 2019) & (sf["flow_cfs"] == f)].iloc[0]
        assert abs(row["stage_at_flow_ft"] - (3.0 + 2.0 * np.log10(f / 100))) < 1e-6
        assert row["stage_se_ft"] < 1e-6
        assert row["n_pairs"] >= 5


def test_stage_at_flow_nan_below_min_pairs():
    pairs = pair_iv(*_iv(n_days=20))
    sf = stage_at_flow(pairs, flows=(400.0,), tol=0.20, min_pairs=10_000)
    assert sf["stage_at_flow_ft"].isna().all() and sf["stage_se_ft"].isna().all()


def test_shift_detected_after_event():
    pairs = pair_iv(*_iv(drop_after="2019-10-01", drop_ft=0.5))
    shifts = rating_shift_at_events(pairs, pd.Series([pd.Timestamp("2019-10-01")]), flows=(400.0,), min_pairs=5)
    assert list(shifts.columns) == [
        "event_date", "flow_cfs", "stage_before_ft", "stage_after_ft", "shift_ft", "n_before", "n_after",
    ]
    row = shifts.iloc[0]
    assert abs(row["shift_ft"] + 0.5) < 1e-6
    assert row["n_before"] >= 5 and row["n_after"] >= 5
