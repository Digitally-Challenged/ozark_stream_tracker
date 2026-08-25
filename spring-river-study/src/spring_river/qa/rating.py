"""Q5: is the stage-floor decline a rating artifact? Stage at fixed discharge
per water year from IV pairs (spec §2.2, risk #4). This is the IV-derived
substitute for USGS shift records, which have not been obtained."""
import pandas as pd

from spring_river.config import RATING_FLOWS_CFS, RATING_TOLERANCE
from spring_river.hydro.wateryear import water_year


def pair_iv(iv_q: pd.DataFrame, iv_h: pd.DataFrame) -> pd.DataFrame:
    m = iv_q.merge(iv_h, on="datetime", suffixes=("_q", "_h"))
    return pd.DataFrame(
        {
            "datetime": m["datetime"],
            "q_cfs": m["value_q"].astype("float64"),
            "stage_ft": m["value_h"].astype("float64"),
            "approved": m["approved_q"] & m["approved_h"],
        }
    ).dropna(subset=["q_cfs", "stage_ft"]).reset_index(drop=True)


def stage_at_flow(
    pairs: pd.DataFrame,
    flows: tuple[float, ...] = RATING_FLOWS_CFS,
    tol: float = RATING_TOLERANCE,
    min_pairs: int = 20,
) -> pd.DataFrame:
    p = pairs.assign(wy=water_year(pairs["datetime"]))
    rows = []
    for wy, grp in p.groupby("wy"):
        for f in flows:
            win = grp[(grp["q_cfs"] >= f * (1 - tol)) & (grp["q_cfs"] <= f * (1 + tol))]["stage_ft"]
            n = len(win)
            rows.append(
                {
                    "wy": int(wy),
                    "flow_cfs": float(f),
                    "stage_median_ft": float(win.median()) if n >= min_pairs else float("nan"),
                    "stage_iqr_ft": float(win.quantile(0.75) - win.quantile(0.25)) if n >= min_pairs else float("nan"),
                    "n_pairs": n,
                }
            )
    return pd.DataFrame(rows)


def rating_shift_at_events(sf: pd.DataFrame, event_dates: pd.Series) -> pd.DataFrame:
    idx = sf.set_index(["wy", "flow_cfs"])["stage_median_ft"]
    rows = []
    for d in pd.to_datetime(event_dates):
        wy = int(water_year(pd.Series([d])).iloc[0])
        for f in sorted(sf["flow_cfs"].unique()):
            before = idx.get((wy, f), float("nan"))
            after = idx.get((wy + 1, f), float("nan"))
            rows.append(
                {
                    "event_date": d,
                    "flow_cfs": f,
                    "stage_before_ft": before,
                    "stage_after_ft": after,
                    "shift_ft": after - before,
                }
            )
    return pd.DataFrame(rows)
