"""West Plains composite daily precipitation: COOP 1948→ spliced with KUNO ASOS.

USC00238880 (West Plains COOP, volunteer-read, 1948→) has ~675 missing days
scattered through 2011–2021, so twelve calendar years fail the 90 % coverage
gate and drop out of the Q3 station trend test. KUNO (West Plains Municipal
Airport ASOS, ~2 mi away, 1998-04→) is essentially complete.

The composite **substitutes a co-located measurement** for the missing
volunteer readings — it does not interpolate. A day missing at both stations
stays NaN. KUNO is multiplied by the COOP/KUNO catch ratio so the spliced
series keeps the COOP gauge's level (the ASOS undercatches slightly), and the
`source` column records which gauge supplied every day.
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
    """Daily composite on a complete index from COOP's first day onward.

    Before `kuno_start`: COOP as measured (`source="coop"`).
    From `kuno_start`: KUNO × `ratio` where KUNO reported (`source="kuno"`),
    else unscaled COOP where COOP reported (`source="coop"`), else NaN
    (`source="none"`). No value is ever interpolated.
    """
    c = coop.set_index("date")["pcpn_in"].sort_index().astype("float64")
    k = kuno.set_index("date")["pcpn_in"].sort_index().astype("float64")
    last = max(c.index.max(), k.index.max())
    index = pd.date_range(c.index.min(), last, freq="D")
    c = c.reindex(index)
    k = k.reindex(index)

    cutoff = pd.Timestamp(kuno_start)
    use_kuno = (index >= cutoff) & k.notna().to_numpy()
    use_coop = ~use_kuno & c.notna().to_numpy()

    value = np.where(use_kuno, k.to_numpy() * ratio, np.where(use_coop, c.to_numpy(), np.nan))
    source = np.where(use_kuno, "kuno", np.where(use_coop, "coop", "none"))
    return pd.DataFrame({"date": index, "pcpn_in": value, "source": source})


def west_plains_composite(
    start: str = "1948-01-01", end: str | None = None
) -> pd.DataFrame:
    """Fetch both gauges, compute the catch ratio, and return the composite."""
    from datetime import date

    from spring_river.config import START_DATE
    from spring_river.ingest import acis

    end = end or date.today().isoformat()
    coop = acis.get_station_pcpn("USC00238880", start, end, cache_suffix="_1948")
    kuno = acis.get_station_pcpn("KUNO", START_DATE, end)
    return splice(coop, kuno, catch_ratio(coop, kuno))
