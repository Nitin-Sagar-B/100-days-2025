from __future__ import annotations

from datetime import date, datetime
from pathlib import Path
from typing import Iterable, List, Optional

import pandas as pd
from sqlalchemy import select

from .db import get_engine, session_scope, utcnow_str
from .models import DailyMetrics, create_all
from .validation import validate_date, validate_ranges


DATA_DIR = Path("data")
BACKUP_DIR = Path("backups")


def init_db():
    engine = get_engine()
    create_all(engine)


def upsert_day(payload: dict) -> None:
    d = payload["date"]
    if isinstance(d, str):
        d = date.fromisoformat(d)
        payload["date"] = d

    vd = validate_date(d)
    if not vd.ok:
        raise ValueError(vd.message)
    vr = validate_ranges(payload)
    if not vr.ok:
        raise ValueError(vr.message)

    now = datetime.utcnow()
    with session_scope() as s:
        instance = s.get(DailyMetrics, d)
        if instance is None:
            instance = DailyMetrics(
                date=d,
                sugar_intake_g=int(payload.get("sugar_intake_g", 0)),
                water_ml=int(payload.get("water_ml", 0)),
                fap_count=int(payload.get("fap_count", 0)),
                productive_hours=float(payload.get("productive_hours", 0.0)),
                weight_kg=(
                    float(payload["weight_kg"]) if payload.get("weight_kg") is not None else None
                ),
                notes=payload.get("notes"),
                created_at=now,
                updated_at=now,
            )
            s.add(instance)
        else:
            instance.sugar_intake_g = int(payload.get("sugar_intake_g", instance.sugar_intake_g))
            instance.water_ml = int(payload.get("water_ml", instance.water_ml))
            instance.fap_count = int(payload.get("fap_count", instance.fap_count))
            instance.productive_hours = float(
                payload.get("productive_hours", instance.productive_hours)
            )
            instance.weight_kg = (
                float(payload["weight_kg"]) if payload.get("weight_kg") is not None else instance.weight_kg
            )
            instance.notes = payload.get("notes", instance.notes)
            instance.updated_at = now


def get_between(start: date, end: date) -> List[DailyMetrics]:
    with session_scope() as s:
        res = s.execute(select(DailyMetrics).where(DailyMetrics.date.between(start, end))).scalars()
        return list(res)


def to_dataframe(start: Optional[date] = None, end: Optional[date] = None) -> pd.DataFrame:
    if start and end:
        rows = get_between(start, end)
    else:
        with session_scope() as s:
            rows = list(s.execute(select(DailyMetrics)).scalars())
    df = pd.DataFrame(
        [
            {
                "date": r.date.isoformat(),
                "sugar_intake_g": r.sugar_intake_g,
                "water_ml": r.water_ml,
                "fap_count": r.fap_count,
                "productive_hours": r.productive_hours,
                "weight_kg": r.weight_kg,
                "notes": r.notes,
                "created_at": r.created_at,
                "updated_at": r.updated_at,
            }
            for r in rows
        ]
    )
    if not df.empty:
        df["date"] = pd.to_datetime(df["date"])  # type: ignore[assignment]
        df = df.sort_values("date")
    return df


def export_csv(path: Path, start: Optional[date] = None, end: Optional[date] = None) -> Path:
    df = to_dataframe(start, end)
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)
    return path


def export_json(path: Path, start: Optional[date] = None, end: Optional[date] = None) -> Path:
    df = to_dataframe(start, end)
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_json(path, orient="records", date_format="iso")
    return path


def import_csv(path: Path, drop_conflicts: bool = False) -> int:
    df = pd.read_csv(path)
    df["date"] = pd.to_datetime(df["date"]).dt.date
    count = 0
    with session_scope() as s:
        for _, row in df.iterrows():
            payload = row.to_dict()
            payload["date"] = row["date"]
            try:
                upsert_day(payload)
                count += 1
            except Exception:
                if drop_conflicts:
                    continue
                raise
    return count


def weekly_auto_backup() -> Path:
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.utcnow().strftime("%Y%m%d-%H%M%S")
    out = BACKUP_DIR / f"backup-{stamp}.csv"
    export_csv(out)
    return out
