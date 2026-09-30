"""Small, explainable Phase 1 data-quality checks."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import timedelta

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
    null_ratio: float = 0.0
    duplicate_ratio: float = 0.0
    timestamp_monotonic: bool = True
    timestamp_gaps: int = 0
    range_violations: int = 0

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


def check_dataframe(
    frame: pd.DataFrame,
    *,
    required_columns: set[str],
    numeric_columns: set[str],
    ranges: dict[str, tuple[float | None, float | None]] | None = None,
    expected_interval: timedelta = timedelta(hours=1),
) -> QualityReport:
    """Check row presence, columns, timestamps, numeric values, nulls and duplicates."""

    missing = tuple(sorted(required_columns.difference(frame.columns)))
    nulls = int(frame.isna().sum().sum())
    duplicate_timestamps = (
        int(frame.duplicated(subset=["city", "timestamp"]).sum())
        if {"city", "timestamp"}.issubset(frame.columns)
        else 0
    )
    observed_invalid_numeric = sum(
        int(frame[column].notna().sum() - pd.to_numeric(frame[column], errors="coerce").notna().sum())
        for column in numeric_columns.intersection(frame.columns)
    )
    invalid_numeric = max(
        observed_invalid_numeric,
        int(frame.attrs.get("invalid_numeric", 0)),
    )

    row_count = len(frame)
    cell_count = max(row_count * max(len(frame.columns), 1), 1)
    null_ratio = nulls / cell_count
    duplicate_ratio = duplicate_timestamps / max(row_count, 1)
    timestamp_monotonic = True
    timestamp_gaps = 0
    if "timestamp" in frame and not frame.empty:
        ordered = frame.sort_values([column for column in ("city", "timestamp") if column in frame])
        timestamp_monotonic = bool(frame["timestamp"].is_monotonic_increasing)
        group_key = "city" if "city" in ordered else lambda _: "all"
        timestamp_gaps = int(
            sum(
                (group["timestamp"].diff().dropna() > expected_interval).sum()
                for _, group in ordered.groupby(group_key, dropna=False)
            )
        )

    range_violations = 0
    for column, (minimum, maximum) in (ranges or {}).items():
        if column not in frame:
            continue
        values = pd.to_numeric(frame[column], errors="coerce")
        if minimum is not None:
            range_violations += int((values < minimum).sum())
        if maximum is not None:
            range_violations += int((values > maximum).sum())

    if frame.empty or missing or "timestamp" not in frame or frame["timestamp"].isna().any():
        result = "FAIL"
    elif (
        nulls
        or duplicate_timestamps
        or invalid_numeric
        or not timestamp_monotonic
        or timestamp_gaps
        or range_violations
    ):
        result = "WARN"
    else:
        result = "PASS"
    return QualityReport(
        rows=len(frame),
        missing_columns=missing,
        nulls=nulls,
        duplicate_timestamps=duplicate_timestamps,
        invalid_numeric=invalid_numeric,
        null_ratio=round(null_ratio, 6),
        duplicate_ratio=round(duplicate_ratio, 6),
        timestamp_monotonic=timestamp_monotonic,
        timestamp_gaps=timestamp_gaps,
        range_violations=range_violations,
        result=result,
    )
