from __future__ import annotations

import argparse
from datetime import date, datetime, timedelta
from pathlib import Path
import random
import sys

import numpy as np
import pandas as pd

# Ensure project root on path when running from scripts/
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.repo import upsert_day, init_db


def daterange(start: date, end: date):
    cur = start
    while cur <= end:
        yield cur
        cur += timedelta(days=1)


def generate(start: date, end: date, seed: int = 42) -> pd.DataFrame:
    random.seed(seed)
    np.random.seed(seed)
    rows = []
    base_weight = 75.0
    for d in daterange(start, end):
        # occasional missing day
        if random.random() < 0.05:
            continue
        sugar = max(0, int(np.random.normal(60, 25)))
        water = int(np.random.normal(2200, 400))
        fap = int(np.clip(np.random.poisson(0.3), 0, 5))
        prod = float(np.clip(np.random.normal(5.0, 2.0), 0, 12))
        # weight with gentle drift and noise
        base_weight += np.random.normal(0, 0.03)
        weight = round(base_weight + np.random.normal(0, 0.4), 1)
        # occasional outliers
        if random.random() < 0.03:
            sugar += 120
        if random.random() < 0.03:
            prod = max(0.0, prod - 3.0)
        notes = ""
        rows.append(
            {
                "date": d,
                "sugar_intake_g": sugar,
                "water_ml": water,
                "fap_count": fap,
                "productive_hours": prod,
                "weight_kg": weight,
                "notes": notes,
            }
        )
    df = pd.DataFrame(rows)
    return df


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--out", type=Path, default=Path("data/sample_seed.csv"))
    p.add_argument("--range", type=str, default="2025-09-22:2025-12-31")
    p.add_argument("--seed-db", action="store_true")
    args = p.parse_args()

    start_s, end_s = args.range.split(":")
    start = date.fromisoformat(start_s)
    end = date.fromisoformat(end_s)

    df = generate(start, end)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    df_out = df.copy()
    df_out["date"] = df_out["date"].astype(str)
    df_out.to_csv(args.out, index=False)
    print(f"Wrote {args.out} with {len(df)} rows")

    if args.seed_db:
        init_db()
        for _, row in df.iterrows():
            upsert_day({**row, "date": row["date"]})
        print("Seeded DB at data/habits.db")


if __name__ == "__main__":
    main()
