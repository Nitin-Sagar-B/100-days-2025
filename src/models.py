from __future__ import annotations

from datetime import date, datetime
from typing import Optional

from sqlalchemy import Column, Date, DateTime, Float, Integer, MetaData, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


metadata_obj = MetaData()


class Base(DeclarativeBase):
    metadata = metadata_obj


class DailyMetrics(Base):
    __tablename__ = "daily_metrics"

    date: Mapped[date] = mapped_column(Date, primary_key=True)
    sugar_intake_g: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    water_ml: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    fap_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    productive_hours: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    weight_kg: Mapped[float] = mapped_column(Float, nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)


def create_all(engine):
    Base.metadata.create_all(engine)
