import numpy as np
import pandas as pd

from spring_river.qa.rating import (
    flow_percentile_stages,
    loglog_correlation,
    pair_iv,
    rating_shift_at_events,
    rating_table,
    stage_at_flow,
)


def _q_at(stage: float) -> float:
    return 100 * 10 ** ((stage - 3.0) / 2.0)   # inverse of the synthetic rating


def test_rating_table_recovers_inverse():
    pairs = pair_iv(*_iv(n_days=2000))
    stages = (3.5, 4.0, 4.5)   # q ≈ 178, 316, 562 cfs: inside the fixture's lognormal bulk
    rt = rating_table(pairs, stages=stages, tol_ft=0.05, min_pairs=20)
    assert list(rt.columns) == ["stage_ft", "median_cfs", "q25_cfs", "q75_cfs", "n_pairs"]
    assert rt["stage_ft"].tolist() == list(stages)
    for _, row in rt.iterrows():
        assert row["n_pairs"] >= 20
        # ±0.05 ft on stage is ±6% on flow under this rating; median must sit inside that
        assert abs(row["median_cfs"] / _q_at(row["stage_ft"]) - 1) < 0.06
        assert row["q25_cfs"] <= row["median_cfs"] <= row["q75_cfs"]


def test_rating_table_nan_below_min_pairs_and_since_filter():
    pairs = pair_iv(*_iv(n_days=800))
    sparse = rating_table(pairs, stages=(20.0,), min_pairs=20)          # no pairs that high
    assert sparse["median_cfs"].isna().all() and int(sparse["n_pairs"].iloc[0]) == 0
    late = rating_table(pairs, stages=(3.0,), since="2020-06-01", min_pairs=1)
    full = rating_table(pairs, stages=(3.0,), min_pairs=1)
    assert 0 < int(late["n_pairs"].iloc[0]) < int(full["n_pairs"].iloc[0])


def test_loglog_correlation_synthetic_rating():
    pairs = pair_iv(*_iv())
    c = loglog_correlation(pairs)
    assert set(c) == {"r_loglog", "spearman", "n"}
    assert c["r_loglog"] > 0.99 and c["spearman"] > 0.99
    assert c["n"] == len(pairs)


def test_flow_percentile_stages_maps_flow_to_stage():
    pairs = pair_iv(*_iv(n_days=2000))
    dv = pd.DataFrame({"value": pairs["q_cfs"]})
    fp = flow_percentile_stages(pairs, dv["value"], percentiles=(5, 50, 95), tol=0.03)
    assert list(fp.columns) == ["percentile", "q_cfs", "stage_ft", "n_pairs"]
    for _, row in fp.iterrows():
        expected = 3.0 + 2.0 * np.log10(row["q_cfs"] / 100)
        assert abs(row["stage_ft"] - expected) < 0.03   # ±3% flow is ±0.026 ft here
        assert row["n_pairs"] > 0


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
