"""West Plains daily precipitation record: COOP 1948→Mar 1998, then KUNO ASOS.

Two instruments, one at a time. USC00238880 (West Plains COOP, volunteer-read,
1948→, −91.874/36.727, 1105 ft) supplies every day through 1998-03-31. KUNO
(West Plains Municipal Airport ASOS, 1998-04-01→, −91.905/36.879, 1226 ft —
10.7 mi north of and 120 ft above the town gauge) supplies every day from
1998-04-01.

The two gauges differ systematically: on calendar months complete at both, the
COOP/KUNO catch ratio is ~1.07. KUNO is raised by that measured ratio so the
whole record sits on the town gauge's level. Nothing else is adjusted: no day
is borrowed between gauges (a day the period's instrument missed stays NaN)
and nothing is interpolated. The `source` column records the instrument.
"""
import numpy as np
import pandas as pd

KUNO_START = "1998-04-01"
MIN_MONTH_DAYS = 25


def catch_ratio(
    coop: pd.DataFrame, kuno: pd.DataFrame, min_month_days: int = MIN_MONTH_DAYS
) -> float:
    """sum(COOP)/sum(KUNO) over calendar months complete at both stations.

    Same definition as `phase6._monthly_agreement`'s ratio: only months with
    at least `min_month_days` non-NaN days at *both* stations contribute.
    """
    mc = coop.set_index("date")["pcpn_in"].resample("MS").agg(["sum", "count"])
    mk = kuno.set_index("date")["pcpn_in"].resample("MS").agg(["sum", "count"])
    j = mc.join(mk, lsuffix="_c", rsuffix="_k", how="inner")
    j = j[(j["count_c"] >= min_month_days) & (j["count_k"] >= min_month_days)]
    return float(j["sum_c"].sum() / j["sum_k"].sum())


def splice(
    coop: pd.DataFrame,
    kuno: pd.DataFrame,
    ratio: float,
    kuno_start: str = KUNO_START,
) -> pd.DataFrame:
    """Daily record on a complete index from COOP's first day onward.

    Before `kuno_start`: COOP as measured (`source="coop"`).
    From `kuno_start`: KUNO × `ratio`, putting the airport gauge on the town
    gauge's level (`source="kuno"`).
    Where the period's instrument reported nothing: NaN (`source="none"`).
    No day is ever borrowed from the other gauge, and none is interpolated.
    """
    c = coop.set_index("date")["pcpn_in"].sort_index().astype("float64")
    k = kuno.set_index("date")["pcpn_in"].sort_index().astype("float64")
    last = max(c.index.max(), k.index.max())
    index = pd.date_range(c.index.min(), last, freq="D")
    c = c.reindex(index)
    k = k.reindex(index)

    after = index >= pd.Timestamp(kuno_start)
    use_kuno = after & k.notna().to_numpy()
    use_coop = ~after & c.notna().to_numpy()

    value = np.where(use_kuno, k.to_numpy() * ratio, np.where(use_coop, c.to_numpy(), np.nan))
    source = np.where(use_kuno, "kuno", np.where(use_coop, "coop", "none"))
    return pd.DataFrame({"date": index, "pcpn_in": value, "source": source})


def west_plains_record(
    start: str = "1948-01-01", end: str | None = None
) -> pd.DataFrame:
    """Fetch both gauges, measure the catch ratio, and return the record."""
    # Imported here, not at module scope: `catch_ratio` and `splice` are pure
    # and must stay importable (and unit-testable) without pulling in the
    # ingest/config layer. Only this convenience fetcher needs them.
    from datetime import date

    from spring_river.config import START_DATE
    from spring_river.ingest import acis

    end = end or date.today().isoformat()
    coop = acis.get_station_pcpn("USC00238880", start, end, cache_suffix="_1948")
    kuno = acis.get_station_pcpn("KUNO", START_DATE, end)
    return splice(coop, kuno, catch_ratio(coop, kuno))
