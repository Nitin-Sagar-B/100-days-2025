from __future__ import annotations

import os
from datetime import date, datetime
from pathlib import Path
from typing import Iterable, List, Optional

import pandas as pd
from sqlalchemy import select

from .db import get_engine, session_scope, utcnow_str
from .models import DailyMetrics, create_all
from .validation import validate_date, validate_ranges

# Optional Google Sheets backend
try:  # lazy optional imports
    import streamlit as st  # type: ignore
except Exception:  # pragma: no cover
    st = None  # type: ignore

try:
    from .sheets_repo import GoogleSheetRepo, SheetsConfig, _load_service_account_dict
except Exception:  # pragma: no cover
    GoogleSheetRepo = None  # type: ignore
    SheetsConfig = None  # type: ignore
    _load_service_account_dict = None  # type: ignore


DATA_DIR = Path("data")
BACKUP_DIR = Path("backups")


_SHEETS_REPO: Optional[GoogleSheetRepo] = None  # type: ignore


def _get_spreadsheet_id() -> Optional[str]:
    # Priority: Streamlit secrets, env var, then project default from user's shared sheet
    if st is not None:
        for key in ("spreadsheet_id", "google_spreadsheet_id", "GOOGLE_SHEETS_SPREADSHEET_ID"):
            try:
                val = st.secrets.get(key)  # type: ignore[attr-defined]
                if val:
                    return str(val)
            except Exception:
                pass
    env = os.getenv("GOOGLE_SHEETS_SPREADSHEET_ID")
    if env:
        return env
    # Fallback to provided empty spreadsheet the user shared (ID is public, not a secret)
    return "1veCOGTZp75Zy4eRxIAGnYi8hYvAS1MUAQYHc9L3Pids"


def _sheets_enabled() -> bool:
    if GoogleSheetRepo is None or SheetsConfig is None:
        return False
    if _load_service_account_dict is None:
        return False
    sa = _load_service_account_dict()
    sid = _get_spreadsheet_id()
    return bool(sa and sid)


def _get_sheets_repo() -> GoogleSheetRepo:  # type: ignore[name-defined]
    global _SHEETS_REPO
    if _SHEETS_REPO is None:
        cfg = SheetsConfig(spreadsheet_id=_get_spreadsheet_id())  # type: ignore[misc]
        _SHEETS_REPO = GoogleSheetRepo(cfg)  # type: ignore[misc]
    return _SHEETS_REPO


def init_db():
    if _sheets_enabled():
        # Ensure worksheet exists and headers are present
        _get_sheets_repo()
    else:
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

    if _sheets_enabled():
        # Delegate to Sheets
        _get_sheets_repo().upsert_day(payload)
        return
    # Fallback to SQLite
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


class _ObjView:
    def __init__(self, mapping: dict):
        for k, v in mapping.items():
            setattr(self, k, v)


def get_day(d: date) -> Optional[object]:
    """Return a single day's record-like object with attributes or None."""
    if _sheets_enabled():
        rec = _get_sheets_repo().get_day(d)
        return _ObjView(rec) if rec else None
    with session_scope() as s:
        return s.get(DailyMetrics, d)


def delete_day(d: date) -> bool:
    """Delete a day's record. Returns True if deleted, False if not found."""
    if _sheets_enabled():
        return _get_sheets_repo().delete_day(d)
    with session_scope() as s:
        obj = s.get(DailyMetrics, d)
        if obj is None:
            return False
        s.delete(obj)
        return True


def get_between(start: date, end: date) -> List[DailyMetrics]:
    if _sheets_enabled():
        df = _get_sheets_repo().to_dataframe()
        if df.empty:
            return []
        mask = (df["date"].dt.date >= start) & (df["date"].dt.date <= end)
        sub = df.loc[mask]
        # Convert rows to lightweight objects akin to DailyMetrics for compatibility
        out: List[DailyMetrics] = []  # type: ignore[assignment]
        for _, r in sub.iterrows():
            out.append(_ObjView({
                "date": r["date"].date() if hasattr(r["date"], "date") else r["date"],
                "sugar_intake_g": int(r.get("sugar_intake_g", 0)),
                "water_ml": int(r.get("water_ml", 0)),
                "fap_count": int(r.get("fap_count", 0)),
                "productive_hours": float(r.get("productive_hours", 0.0)),
                "weight_kg": (float(r["weight_kg"]) if pd.notna(r.get("weight_kg")) else None),
                "notes": r.get("notes", ""),
                "created_at": r.get("created_at"),
                "updated_at": r.get("updated_at"),
            }))
        return out
    with session_scope() as s:
        res = s.execute(select(DailyMetrics).where(DailyMetrics.date.between(start, end))).scalars()
        return list(res)


def to_dataframe(start: Optional[date] = None, end: Optional[date] = None) -> pd.DataFrame:
    if _sheets_enabled():
        df = _get_sheets_repo().to_dataframe()
        if start and end and not df.empty:
            mask = (df["date"].dt.date >= start) & (df["date"].dt.date <= end)
            df = df.loc[mask]
        return df
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
