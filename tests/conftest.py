"""Reusable API response fixtures."""

from __future__ import annotations

import pytest


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

