"""Reusable API response fixtures."""

from __future__ import annotations

import pytest
import pandas as pd

from urban_environment.models.city import City


@pytest.fixture
def weather_payload() -> dict[str, object]:
    return {
        "timezone": "Asia/Shanghai",
        "hourly": {
            "time": ["2026-09-23T00:00", "2026-09-23T01:00"],
            "temperature_2m": [20.0, 21.0],
            "relative_humidity_2m": [60, 58],
            "precipitation": [0.0, 0.1],
            "wind_speed_10m": [7.0, 8.0],
            "surface_pressure": [1010.0, 1009.5],
        },
    }


@pytest.fixture
def air_payload() -> dict[str, object]:
    return {
        "timezone": "Asia/Shanghai",
        "hourly": {
            "time": ["2026-09-23T00:00", "2026-09-23T01:00"],
            "pm2_5": [10.0, 11.0],
            "pm10": [18.0, 20.0],
            "nitrogen_dioxide": [12.0, 13.0],
            "ozone": [50.0, 51.0],
            "european_aqi": [25.0, 26.0],
        },
    }


@pytest.fixture
def beijing() -> City:
    return City(
        id="beijing",
        name="北京",
        query_name="Beijing",
        country="中国",
        country_code="CN",
        latitude=39.9075,
        longitude=116.39723,
        timezone="Asia/Shanghai",
    )


@pytest.fixture
def environment_frame() -> pd.DataFrame:
    timestamps = pd.date_range("2026-09-20", periods=192, freq="h", tz="UTC")
    rows = []
    for city, offset in (("beijing", 0.0), ("tokyo", 2.0)):
        for index, timestamp in enumerate(timestamps):
            rows.append(
                {
                    "city": city,
                    "timestamp": timestamp,
                    "temperature": 20 + offset + (index % 24) / 4,
                    "relative_humidity": 55 + (index % 10),
                    "precipitation": 0.2 if index % 30 == 0 else 0.0,
                    "wind_speed": 5 + (index % 7),
                    "pm2_5": 15 + offset + (index % 8),
                    "pm10": 25 + offset + (index % 9),
                    "air_quality_index": 30 + offset + (index % 11),
                    "ozone": 50 + index % 12,
                }
            )
    return pd.DataFrame(rows)

