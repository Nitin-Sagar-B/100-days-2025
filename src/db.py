from __future__ import annotations

import os
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path

from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker

DB_PATH = Path("data/habits.db")


def get_engine(echo: bool = False) -> Engine:
    os.makedirs(DB_PATH.parent, exist_ok=True)
    engine = create_engine(f"sqlite:///{DB_PATH}", echo=echo, future=True)

    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):  # type: ignore[no-redef]
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.close()

    return engine


SessionLocal = sessionmaker(
    bind=get_engine(), autoflush=False, autocommit=False, future=True, expire_on_commit=False
)


@contextmanager
def session_scope():
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def utcnow_str() -> str:
    return datetime.utcnow().isoformat(timespec="seconds")
