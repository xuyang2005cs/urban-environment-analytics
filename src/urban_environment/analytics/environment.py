"""Explainable environmental analytics built with Pandas and DuckDB SQL."""

from __future__ import annotations

import math

import pandas as pd


DAILY_METRICS = (
    "temperature",
    "relative_humidity",
    "wind_speed",
    "pm2_5",
    "pm10",
    "air_quality_index",
)


def daily_aggregation(frame: pd.DataFrame) -> pd.DataFrame:
    """Return per-city daily mean/min/max plus precipitation sum."""

    if frame.empty:
        return pd.DataFrame()
    data = frame.copy()
    data["timestamp"] = pd.to_datetime(data["timestamp"], utc=True)
    data["date"] = data["timestamp"].dt.date
    available = [metric for metric in DAILY_METRICS if metric in data]
    aggregations = {metric: ["mean", "min", "max"] for metric in available}
    if "precipitation" in data:
        aggregations["precipitation"] = ["sum", "mean", "max"]
    result = data.groupby(["city", "date"], as_index=False).agg(aggregations)
    result.columns = [
        "_".join(part for part in column if part).rstrip("_")
        if isinstance(column, tuple)
        else column
        for column in result.columns
    ]
    return result


def rolling_analytics(frame: pd.DataFrame) -> pd.DataFrame:
    """Add 24-hour and 7-day time-based rolling means per city."""

    if frame.empty:
        return frame.copy()
    data = frame.copy()
    data["timestamp"] = pd.to_datetime(data["timestamp"], utc=True)
    data = data.sort_values(["city", "timestamp"])
    metrics = [metric for metric in DAILY_METRICS if metric in data]
    pieces: list[pd.DataFrame] = []
    for _, group in data.groupby("city", sort=False):
        indexed = group.set_index("timestamp")
        for metric in metrics:
            indexed[f"{metric}_rolling_24h"] = indexed[metric].rolling("24h", min_periods=1).mean()
            indexed[f"{metric}_rolling_7d"] = indexed[metric].rolling("7d", min_periods=1).mean()
        pieces.append(indexed.reset_index())
    return pd.concat(pieces, ignore_index=True)


def city_comparison(frame: pd.DataFrame) -> pd.DataFrame:
    """Compare metrics without producing an unsupported composite ranking."""

    if frame.empty:
        return pd.DataFrame()
    metrics = [
        metric
        for metric in (
            "temperature", "pm2_5", "air_quality_index", "precipitation", "wind_speed"
        )
        if metric in frame
    ]
    comparison = frame.groupby("city", as_index=False)[metrics].mean()
    return comparison.rename(columns={metric: f"{metric}_mean" for metric in metrics})


def correlation_exploration(frame: pd.DataFrame, *, minimum_rows: int = 3) -> pd.DataFrame:
    """Calculate selected Pearson correlations; never imply causality."""

    pairs = (
        ("pm2_5", "wind_speed"),
        ("pm2_5", "relative_humidity"),
        ("pm2_5", "precipitation"),
        ("ozone", "temperature"),
    )
    rows: list[dict[str, object]] = []
    for left, right in pairs:
        if left not in frame or right not in frame:
            rows.append({"metric_x": left, "metric_y": right, "correlation": None, "status": "insufficient data"})
            continue
        values = frame[[left, right]].dropna()
        correlation = values[left].corr(values[right]) if len(values) >= minimum_rows else math.nan
        status = "ok" if pd.notna(correlation) else "insufficient data"
        rows.append(
            {
                "metric_x": left,
                "metric_y": right,
                "correlation": round(float(correlation), 4) if pd.notna(correlation) else None,
                "status": status,
            }
        )
    return pd.DataFrame(rows)


def detect_anomalies(
    frame: pd.DataFrame,
    *,
    metrics: tuple[str, ...] = ("temperature", "pm2_5", "air_quality_index"),
    multiplier: float = 1.5,
) -> pd.DataFrame:
    """Flag IQR outliers without modifying or deleting source records."""

    rows: list[dict[str, object]] = []
    for city, group in frame.groupby("city"):
        for metric in metrics:
            if metric not in group:
                continue
            values = pd.to_numeric(group[metric], errors="coerce")
            valid = values.dropna()
            if len(valid) < 4:
                continue
            q1, q3 = valid.quantile([0.25, 0.75])
            iqr = q3 - q1
            if iqr == 0:
                continue
            lower, upper = q1 - multiplier * iqr, q3 + multiplier * iqr
            mask = (values < lower) | (values > upper)
            for index in group.index[mask]:
                value = float(values.loc[index])
                score = (lower - value) / iqr if value < lower else (value - upper) / iqr
                rows.append(
                    {
                        "city": city,
                        "timestamp": group.loc[index, "timestamp"],
                        "metric": metric,
                        "value": value,
                        "score": round(float(score), 3),
                    }
                )
    return pd.DataFrame(rows, columns=["city", "timestamp", "metric", "value", "score"])

