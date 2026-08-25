"""Hardy vs Imboden discharge cross-check and precip homogeneity (spec §2.1)."""
import numpy as np
import pandas as pd
from scipy import stats


def hardy_vs_imboden(hardy: pd.DataFrame, imboden: pd.DataFrame) -> pd.DataFrame:
    merged = hardy.merge(imboden, on="date", suffixes=("_h", "_i"))
    merged = merged[(merged["value_h"] > 0) & (merged["value_i"] > 0)].copy()
    lh, li = np.log10(merged["value_h"]), np.log10(merged["value_i"])
    fit = stats.linregress(li, lh)
    merged["residual"] = lh - (fit.intercept + fit.slope * li)
    return merged.rename(columns={"value_h": "hardy", "value_i": "imboden"})[
        ["date", "hardy", "imboden", "residual"]
    ].reset_index(drop=True)


def precip_overlap(a: pd.DataFrame, b: pd.DataFrame) -> dict:
    merged = a.merge(b, on="date", suffixes=("_a", "_b")).dropna(
        subset=["pcpn_in_a", "pcpn_in_b"]
    )
    mean_a = merged["pcpn_in_a"].mean()
    return {
        "n_days": int(len(merged)),
        "corr": float(merged["pcpn_in_a"].corr(merged["pcpn_in_b"])),
        "mean_ratio": float(merged["pcpn_in_b"].mean() / mean_a)
        if mean_a > 0
        else float("nan"),
    }
