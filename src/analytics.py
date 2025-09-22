from __future__ import annotations

import numpy as np
import pandas as pd


def add_rolling(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df
    df = df.sort_values("date").copy()
    df["prod_7"] = df["productive_hours"].rolling(7, min_periods=1).mean()
    df["prod_30"] = df["productive_hours"].rolling(30, min_periods=1).mean()
    return df


def weekly_breakdown(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df
    df = df.copy()
    df["week"] = df["date"].dt.to_period("W-MON").apply(lambda r: r.start_time)
    agg = (
        df.groupby("week")[
            ["sugar_intake_g", "water_ml", "productive_hours", "fap_count"]
        ]
        .sum()
        .reset_index()
    )
    return agg


def weekday_avg_productivity(df: pd.DataFrame) -> pd.Series:
    if df.empty:
        return pd.Series(dtype=float)
    df = df.copy()
    df["weekday"] = df["date"].dt.day_name()
    return df.groupby("weekday")["productive_hours"].mean()


def correlation_matrix(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame()
    cols = ["sugar_intake_g", "water_ml", "fap_count", "productive_hours", "weight_kg"]
    numeric = df[cols].copy()
    return numeric.corr(method="pearson")


def compute_streak(df: pd.DataFrame, goal_hours: float = 4.0, water_goal_ml: int = 2000) -> int:
    if df.empty:
        return 0
    x = df.sort_values("date").copy()
    met = (x["productive_hours"] >= goal_hours) & (x["water_ml"] >= water_goal_ml)
    # Count from the last day backwards until first failure
    streak = 0
    for ok in reversed(met.to_list()):
        if ok:
            streak += 1
        else:
            break
    return streak


def composite_score(df: pd.DataFrame) -> pd.Series:
    if df.empty:
        return pd.Series(dtype=float)
    x = df.copy()
    # Normalize each metric to 0-1, invert sugar (less is better)
    def norm(s, low, high):
        s = s.clip(lower=low, upper=high)
        return (s - low) / (high - low)

    water = norm(x["water_ml"], 0, 4000)
    prod = norm(x["productive_hours"], 0, 12)
    sugar = 1 - norm(x["sugar_intake_g"], 0, 150)
    score = (0.5 * prod) + (0.35 * water) + (0.15 * sugar)
    return score.clip(0, 1)
