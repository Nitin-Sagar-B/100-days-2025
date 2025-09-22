from pathlib import Path
from datetime import date

from src.repo import init_db, upsert_day, export_csv, import_csv, to_dataframe


def test_export_import_roundtrip(tmp_path: Path):
    init_db()
    upsert_day({
        "date": date(2025,9,22),
        "sugar_intake_g": 20,
        "water_ml": 2100,
        "fap_count": 0,
        "productive_hours": 4.5,
        "weight_kg": 71.0,
    })
    out = tmp_path / "out.csv"
    export_csv(out)
    assert out.exists()
    # re-import
    n = import_csv(out, drop_conflicts=True)
    assert n >= 1
    df = to_dataframe()
    assert not df.empty
