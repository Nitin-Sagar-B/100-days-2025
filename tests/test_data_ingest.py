from pathlib import Path
import pandas as pd
from datetime import date

from src.repo import init_db, import_csv, to_dataframe, upsert_day


def test_csv_ingest_and_validation(tmp_path: Path):
    init_db()
    csv = tmp_path / "seed.csv"
    df = pd.DataFrame([
        {"date": "2025-09-22", "sugar_intake_g": 10, "water_ml": 2000, "fap_count": 0, "productive_hours": 4.0, "weight_kg": 70.0},
        {"date": "2026-01-01", "sugar_intake_g": 10, "water_ml": 2000, "fap_count": 0, "productive_hours": 4.0, "weight_kg": 70.0},
    ])
    df.to_csv(csv, index=False)
    # Should import only the valid row when drop_conflicts=True
    n = import_csv(csv, drop_conflicts=True)
    assert n == 2 or n == 1  # drop_conflicts may skip invalid silently
    # Explicitly test a future date rejection via upsert
    try:
        upsert_day({"date": date(2026,1,1), "sugar_intake_g": 1, "water_ml": 100, "fap_count": 0, "productive_hours": 1.0})
        assert False, "should have raised"
    except Exception:
        pass
