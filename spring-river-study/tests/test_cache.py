import json

import pandas as pd
import pytest

from spring_river.ingest import cache


@pytest.fixture
def raw_dir(tmp_path, monkeypatch):
    monkeypatch.setattr(cache, "RAW_DIR", tmp_path)
    return tmp_path


def test_fetch_writes_parquet_and_meta(raw_dir):
    df = cache.fetch_cached(
        "demo", lambda: pd.DataFrame({"x": [1, 2]}), meta={"source": "test"}
    )
    assert len(df) == 2
    assert (raw_dir / "demo.parquet").exists()
    meta = json.loads((raw_dir / "demo.meta.json").read_text())
    assert meta["source"] == "test"
    assert meta["rows"] == 2
    assert "fetched_at" in meta


def test_second_call_uses_cache_not_fetch_fn(raw_dir):
    cache.fetch_cached("demo", lambda: pd.DataFrame({"x": [1]}), meta={})

    def boom():
        raise AssertionError("fetch_fn called despite cache hit")

    df = cache.fetch_cached("demo", boom, meta={})
    assert len(df) == 1


def test_refresh_true_refetches(raw_dir):
    cache.fetch_cached("demo", lambda: pd.DataFrame({"x": [1]}), meta={})
    df = cache.fetch_cached(
        "demo", lambda: pd.DataFrame({"x": [1, 2, 3]}), meta={}, refresh=True
    )
    assert len(df) == 3
