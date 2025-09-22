from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Dict, Tuple


LAST_DAY = date(2025, 12, 31)


@dataclass
class ValidationResult:
    ok: bool
    message: str = ""


RANGES = {
    "sugar_intake_g": (0, 1000),
    "water_ml": (0, 5000),  # ml
    "fap_count": (0, 10),
    "productive_hours": (0.0, 24.0),
    "weight_kg": (50.0, 100.0),
}


def validate_date(d: date) -> ValidationResult:
    if d > LAST_DAY:
        return ValidationResult(False, "No future dates beyond 2025-12-31 allowed.")
    return ValidationResult(True)


def validate_ranges(payload: Dict) -> ValidationResult:
    for key, (low, high) in RANGES.items():
        if payload.get(key) is None:
            # allow None for weight, notes, etc.
            if key == "weight_kg":
                continue
        val = payload.get(key)
        if val is None:
            continue
        if not (low <= float(val) <= high):
            return ValidationResult(False, f"{key} out of bounds [{low}, {high}]: {val}")
    return ValidationResult(True)
