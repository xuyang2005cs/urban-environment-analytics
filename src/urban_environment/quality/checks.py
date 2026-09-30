"""Small, explainable Phase 1 data-quality checks."""

from __future__ import annotations

from dataclasses import asdict, dataclass

import pandas as pd


@dataclass(frozen=True)
class QualityReport:
    """Serializable quality-check result for one normalized dataset."""

    rows: int
    missing_columns: tuple[str, ...]
    nulls: int
    duplicate_timestamps: int
    invalid_numeric: int
    result: str

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


def check_dataframe(
    frame: pd.DataFrame,
    *,
    required_columns: set[str],
    numeric_columns: set[str],
) -> QualityReport:
    """Check row presence, columns, timestamps, numeric values, nulls and duplicates."""

    missing = tuple(sorted(required_columns.difference(frame.columns)))
    nulls = int(frame.isna().sum().sum())
    duplicate_timestamps = (
        int(frame.duplicated(subset=["city", "timestamp"]).sum())
        if {"city", "timestamp"}.issubset(frame.columns)
        else 0
    )
    invalid_numeric = sum(
        int(frame[column].notna().sum() - pd.to_numeric(frame[column], errors="coerce").notna().sum())
        for column in numeric_columns.intersection(frame.columns)
    )

    if frame.empty or missing or "timestamp" not in frame or frame["timestamp"].isna().any():
        result = "FAIL"
    elif nulls or duplicate_timestamps or invalid_numeric:
        result = "WARN"
    else:
        result = "PASS"
    return QualityReport(
        rows=len(frame),
        missing_columns=missing,
        nulls=nulls,
        duplicate_timestamps=duplicate_timestamps,
        invalid_numeric=invalid_numeric,
        result=result,
    )
