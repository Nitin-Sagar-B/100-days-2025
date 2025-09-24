from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from typing import Optional, List, Dict, Any

import pandas as pd

try:
    import streamlit as st  # for secrets, optional at runtime
except Exception:  # pragma: no cover
    st = None  # type: ignore

import os
import json
import gspread
from google.oauth2.service_account import Credentials

# Columns contract aligned with SQL model
HEADERS = [
    "date",
    "sugar_intake_g",
    "water_ml",
    "fap_count",
    "productive_hours",
    "weight_kg",
    "notes",
    "created_at",
    "updated_at",
]


@dataclass
class SheetsConfig:
    spreadsheet_id: str
    worksheet_name: str = "DailyMetrics"


def _load_service_account_dict() -> Optional[dict]:
    # 1) Streamlit secrets: gcp_service_account
    if st is not None:
        try:
            sa = st.secrets.get("gcp_service_account")  # type: ignore[attr-defined]
            if sa:
                return dict(sa)
        except Exception:
            pass
    # 2) Env var GOOGLE_SERVICE_ACCOUNT_JSON (full JSON string)
    raw = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON")
    if raw:
        try:
            return json.loads(raw)
        except Exception:
            pass
    # 3) Env var GOOGLE_SERVICE_ACCOUNT_FILE (path to JSON file)
    path = os.getenv("GOOGLE_SERVICE_ACCOUNT_FILE")
    if path and os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return None


def _get_client() -> gspread.Client:
    sa_dict = _load_service_account_dict()
    if not sa_dict:
        raise RuntimeError(
            "Google Sheets credentials not configured. Add a service account JSON in Streamlit secrets as 'gcp_service_account' or set GOOGLE_SERVICE_ACCOUNT_JSON/FILE."
        )
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]
    creds = Credentials.from_service_account_info(sa_dict, scopes=scopes)
    return gspread.authorize(creds)


class GoogleSheetRepo:
    def __init__(self, cfg: SheetsConfig):
        self.cfg = cfg
        self.gc = _get_client()
        self.sh = self.gc.open_by_key(cfg.spreadsheet_id)
        try:
            self.ws = self.sh.worksheet(cfg.worksheet_name)
        except gspread.WorksheetNotFound:
            self.ws = self.sh.add_worksheet(title=cfg.worksheet_name, rows=2000, cols=len(HEADERS))
        self._ensure_headers()

    def _ensure_headers(self) -> None:
        values = self.ws.get_all_values()
        if not values:
            self.ws.update("A1", [HEADERS])
        else:
            hdr = values[0]
            if hdr != HEADERS:
                # rewrite headers to match contract
                self.ws.update("A1", [HEADERS])

    def _now(self) -> datetime:
        return datetime.utcnow()

    def _to_row(self, payload: Dict[str, Any], created_at: Optional[str] = None) -> List[Any]:
        return [
            (payload["date"].isoformat() if isinstance(payload.get("date"), date) else str(payload.get("date", ""))),
            int(payload.get("sugar_intake_g", 0)),
            int(payload.get("water_ml", 0)),
            int(payload.get("fap_count", 0)),
            float(payload.get("productive_hours", 0.0)),
            (float(payload["weight_kg"]) if payload.get("weight_kg") not in (None, "") else ""),
            payload.get("notes") or "",
            created_at or self._now().isoformat(timespec="seconds") + "Z",
            self._now().isoformat(timespec="seconds") + "Z",
        ]

    def _get_all_records_df(self) -> pd.DataFrame:
        records = self.ws.get_all_records()
        df = pd.DataFrame(records)
        if not df.empty:
            if "date" in df.columns:
                df["date"] = pd.to_datetime(df["date"]).dt.date
        return df

    def to_dataframe(self) -> pd.DataFrame:
        df = self._get_all_records_df()
        if not df.empty:
            df = df.sort_values("date")
            df["date"] = pd.to_datetime(df["date"])  # back to datetime64 for charts
        return df

    def _find_row_index_by_date(self, d: date) -> Optional[int]:
        # Row index in Sheets is 1-based; headers occupy row 1
        # We'll scan the first column quickly
        col = self.ws.col_values(1)  # includes header in [0]
        target = d.isoformat()
        for idx, val in enumerate(col[1:], start=2):  # start at row 2
            if val == target:
                return idx
        return None

    def upsert_day(self, payload: Dict[str, Any]) -> None:
        d = payload["date"]
        if isinstance(d, str):
            d = date.fromisoformat(d)
            payload["date"] = d
        row_idx = self._find_row_index_by_date(d)
        if row_idx:
            # preserve original created_at
            existing = self.ws.row_values(row_idx)
            created_at = existing[HEADERS.index("created_at")] if len(existing) >= len(HEADERS) else None
            row = self._to_row(payload, created_at=created_at)
            rng = f"A{row_idx}:{chr(ord('A') + len(HEADERS) - 1)}{row_idx}"
            self.ws.update(rng, [row])
        else:
            row = self._to_row(payload)
            self.ws.append_row(row, value_input_option="USER_ENTERED")

    def get_day(self, d: date) -> Optional[Dict[str, Any]]:
        row_idx = self._find_row_index_by_date(d)
        if not row_idx:
            return None
        vals = self.ws.row_values(row_idx)
        data = dict(zip(HEADERS, vals))
        # normalize types
        out: Dict[str, Any] = {
            "date": d,
            "sugar_intake_g": int(data.get("sugar_intake_g") or 0),
            "water_ml": int(data.get("water_ml") or 0),
            "fap_count": int(data.get("fap_count") or 0),
            "productive_hours": float(data.get("productive_hours") or 0.0),
            "weight_kg": (float(data["weight_kg"]) if data.get("weight_kg") not in (None, "") else None),
            "notes": data.get("notes") or "",
        }
        return out

    def delete_day(self, d: date) -> bool:
        row_idx = self._find_row_index_by_date(d)
        if not row_idx:
            return False
        self.ws.delete_rows(row_idx)
        return True
