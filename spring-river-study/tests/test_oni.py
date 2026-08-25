import pandas as pd

from spring_river.ingest.oni import parse_oni, recharge_season_oni

SAMPLE = """ SEAS  YR   TOTAL   ANOM
 DJF 2019   26.55   0.70
 JFM 2019   26.87   0.70
 ASO 2019   26.60   0.30
 SON 2019   26.50   0.50
 OND 2019   26.40   0.50
 NDJ 2019   26.30   0.50
 DJF 2020   26.20   0.50
 JFM 2020   26.10   0.50
 FMA 2020   26.00   0.40
"""


def test_parse_oni_center_month():
    df = parse_oni(SAMPLE)
    assert df.loc[df["date"] == pd.Timestamp("2019-01-01"), "anom"].item() == 0.70  # DJF 2019 -> Jan 2019
    assert df.loc[df["date"] == pd.Timestamp("2019-12-01"), "anom"].item() == 0.50  # NDJ 2019 -> Dec 2019


def test_recharge_season_mean():
    df = parse_oni(SAMPLE)
    s = recharge_season_oni(df)
    # WY 2020 = Sep 2019 (ASO .30), Oct (SON .50), Nov (OND .50), Dec (NDJ .50), Jan 2020 (DJF .50), Feb (JFM .50)
    assert abs(s.loc[2020] - (0.30 + 0.50 * 5) / 6) < 1e-9
