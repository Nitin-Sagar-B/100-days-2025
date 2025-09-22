import pandas as pd
from datetime import date, timedelta

from src.analytics import add_rolling, compute_streak


def test_rolling_avg():
    d0 = pd.date_range("2025-09-22", periods=10, freq="D")
    df = pd.DataFrame({"date": d0, "productive_hours": list(range(10))})
    out = add_rolling(df)
    assert "prod_7" in out.columns and "prod_30" in out.columns
    assert out["prod_7"].iloc[-1] > out["prod_7"].iloc[0]


def test_streaks():
    d0 = pd.date_range("2025-09-22", periods=7, freq="D")
    df = pd.DataFrame({
        "date": d0,
        "productive_hours": [1,1,5,5,5,5,5],
        "water_ml": [2000,2000,2000,2000,2000,2000,2000],
        "sugar_intake_g": [50]*7,
        "fap_count": [0]*7,
        "weight_kg": [70]*7,
    })
    assert compute_streak(df) == 5
