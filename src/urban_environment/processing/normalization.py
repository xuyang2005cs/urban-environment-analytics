"""Minimal Phase 1 normalization for Open-Meteo hourly payloads."""

from __future__ import annotations

from typing import Any

import pandas as pd


WEATHER_COLUMN_MAP = {
    "time": "timestamp",
    "temperature_2m": "temperature",
    "relative_humidity_2m": "relative_humidity",
    "precipitation": "precipitation",
    "wind_speed_10m": "wind_speed",
    "surface_pressure": "surface_pressure",
}
AIR_COLUMN_MAP = {
    "time": "timestamp",
    "pm2_5": "pm2_5",
    "pm10": "pm10",
    "nitrogen_dioxide": "nitrogen_dioxide",
    "ozone": "ozone",
    "european_aqi": "air_quality_index",
}


def weather_to_dataframe(payload: dict[str, Any], city_id: str) -> pd.DataFrame:
    """Normalize an hourly weather response into a typed DataFrame."""

    return _hourly_to_dataframe(payload, city_id, WEATHER_COLUMN_MAP)


def air_quality_to_dataframe(payload: dict[str, Any], city_id: str) -> pd.DataFrame:
    """Normalize an hourly air-quality response into a typed DataFrame."""

    return _hourly_to_dataframe(payload, city_id, AIR_COLUMN_MAP)


def merge_environment_data(
    weather: pd.DataFrame, air_quality: pd.DataFrame, *, how: str = "inner"
) -> pd.DataFrame:
    """Probe timestamp alignment without interpolation or imputation."""

    if how not in {"inner", "left"}:
        raise ValueError("how must be 'inner' or 'left'")
    return weather.merge(air_quality, on=["city", "timestamp"], how=how)


def _hourly_to_dataframe(
    payload: dict[str, Any], city_id: str, column_map: dict[str, str]
) -> pd.DataFrame:
    hourly = payload.get("hourly")
    if not isinstance(hourly, dict):
        raise ValueError("payload is missing hourly data")
    missing = set(column_map).difference(hourly)
    if missing:
        raise ValueError(f"hourly data is missing: {', '.join(sorted(missing))}")

    frame = pd.DataFrame({target: hourly[source] for source, target in column_map.items()})
    frame.insert(0, "city", city_id)
    frame["timestamp"] = pd.to_datetime(frame["timestamp"], errors="coerce")
    for column in frame.columns.difference(["city", "timestamp"]):
        frame[column] = pd.to_numeric(frame[column], errors="coerce")
    return frame

