"""Minimal Phase 1 normalization for Open-Meteo hourly payloads."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

import pandas as pd


WEATHER_COLUMN_MAP = {
    "time": "timestamp",
    "temperature_2m": "temperature",
    "relative_humidity_2m": "relative_humidity",
    "precipitation": "precipitation",
    "wind_speed_10m": "wind_speed",
    "surface_pressure": "surface_pressure",
    "weather_code": "weather_code",
}
AIR_COLUMN_MAP = {
    "time": "timestamp",
    "pm2_5": "pm2_5",
    "pm10": "pm10",
    "nitrogen_dioxide": "nitrogen_dioxide",
    "ozone": "ozone",
    "european_aqi": "air_quality_index",
}


def weather_to_dataframe(
    payload: dict[str, Any],
    city_id: str,
    *,
    country: str = "",
    timezone_name: str | None = None,
    ingested_at: datetime | None = None,
) -> pd.DataFrame:
    """Normalize an hourly weather response into a typed DataFrame."""

    return _hourly_to_dataframe(
        payload,
        city_id,
        WEATHER_COLUMN_MAP,
        country=country,
        timezone_name=timezone_name,
        source="open-meteo-weather",
        ingested_at=ingested_at,
    )


def air_quality_to_dataframe(
    payload: dict[str, Any],
    city_id: str,
    *,
    country: str = "",
    timezone_name: str | None = None,
    ingested_at: datetime | None = None,
) -> pd.DataFrame:
    """Normalize an hourly air-quality response into a typed DataFrame."""

    return _hourly_to_dataframe(
        payload,
        city_id,
        AIR_COLUMN_MAP,
        country=country,
        timezone_name=timezone_name,
        source="open-meteo-air-quality",
        ingested_at=ingested_at,
    )


def merge_environment_data(
    weather: pd.DataFrame, air_quality: pd.DataFrame, *, how: str = "inner"
) -> pd.DataFrame:
    """Probe timestamp alignment without interpolation or imputation."""

    if how not in {"inner", "left"}:
        raise ValueError("how must be 'inner' or 'left'")
    return weather.merge(air_quality, on=["city", "timestamp"], how=how)


def _hourly_to_dataframe(
    payload: dict[str, Any],
    city_id: str,
    column_map: dict[str, str],
    *,
    country: str,
    timezone_name: str | None,
    source: str,
    ingested_at: datetime | None,
) -> pd.DataFrame:
    hourly = payload.get("hourly")
    if not isinstance(hourly, dict):
        raise ValueError("payload is missing hourly data")
    missing = set(column_map).difference(hourly)
    if missing:
        raise ValueError(f"hourly data is missing: {', '.join(sorted(missing))}")

    frame = pd.DataFrame({target: hourly[source] for source, target in column_map.items()})
    effective_timezone = timezone_name or str(payload.get("timezone") or "UTC")
    frame.insert(0, "country", [country] * len(frame))
    frame.insert(0, "city", city_id)
    local_time = pd.to_datetime(frame["timestamp"], errors="coerce")
    frame["timestamp"] = local_time.dt.tz_localize(
        effective_timezone, ambiguous="NaT", nonexistent="shift_forward"
    ).dt.tz_convert("UTC")
    invalid_numeric = 0
    for column in frame.columns.difference(["city", "country", "timestamp"]):
        original = frame[column]
        converted = pd.to_numeric(original, errors="coerce")
        invalid_numeric += int((original.notna() & converted.isna()).sum())
        frame[column] = converted
    frame.attrs["invalid_numeric"] = invalid_numeric
    frame["timezone"] = effective_timezone
    frame["source"] = source
    frame["ingested_at"] = pd.Timestamp(ingested_at or datetime.now(timezone.utc))
    return frame

