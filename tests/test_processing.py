"""Normalization, merge and quality tests."""

from __future__ import annotations

import pandas as pd

from urban_environment.processing.normalization import (
    air_quality_to_dataframe,
    merge_environment_data,
    weather_to_dataframe,
)
from urban_environment.quality.checks import check_dataframe


def test_weather_normalization(weather_payload):
    frame = weather_to_dataframe(weather_payload, "beijing")
    assert frame.columns.tolist() == [
        "city",
        "country",
        "timestamp",
        "temperature",
        "relative_humidity",
        "precipitation",
        "wind_speed",
        "surface_pressure",
        "weather_code",
        "timezone",
        "source",
        "ingested_at",
    ]
    assert str(frame["timestamp"].dtype) == "datetime64[ns, UTC]"
    assert frame["temperature"].dtype.kind in "fi"


def test_air_quality_normalization(air_payload):
    frame = air_quality_to_dataframe(air_payload, "beijing")
    assert "air_quality_index" in frame
    assert frame["city"].unique().tolist() == ["beijing"]


def test_normalization_coerces_bad_values_to_null(weather_payload):
    weather_payload["hourly"]["temperature_2m"][0] = "invalid"
    frame = weather_to_dataframe(weather_payload, "beijing")
    assert pd.isna(frame.loc[0, "temperature"])


def test_quality_check_counts_failed_numeric_conversion(weather_payload):
    weather_payload["hourly"]["temperature_2m"][0] = "invalid"
    frame = weather_to_dataframe(weather_payload, "beijing")
    report = check_dataframe(
        frame,
        required_columns={"city", "timestamp", "temperature"},
        numeric_columns={"temperature"},
    )
    assert report.invalid_numeric == 1
    assert report.result == "WARN"


def test_inner_merge_aligns_city_and_timestamp(weather_payload, air_payload):
    weather = weather_to_dataframe(weather_payload, "beijing")
    air = air_quality_to_dataframe(air_payload, "beijing")
    merged = merge_environment_data(weather, air)
    assert len(merged) == 2
    assert {"temperature", "pm2_5"}.issubset(merged.columns)


def test_quality_check_passes_clean_frame(weather_payload):
    frame = weather_to_dataframe(weather_payload, "beijing")
    report = check_dataframe(
        frame,
        required_columns={"city", "timestamp", "temperature"},
        numeric_columns={"temperature", "relative_humidity"},
    )
    assert report.result == "PASS"
    assert report.rows == 2


def test_quality_check_warns_on_duplicate_timestamp(weather_payload):
    frame = weather_to_dataframe(weather_payload, "beijing")
    frame = pd.concat([frame, frame.iloc[[0]]], ignore_index=True)
    report = check_dataframe(
        frame,
        required_columns={"city", "timestamp"},
        numeric_columns={"temperature"},
    )
    assert report.result == "WARN"
    assert report.duplicate_timestamps == 1


def test_quality_check_fails_missing_column(weather_payload):
    frame = weather_to_dataframe(weather_payload, "beijing").drop(columns="timestamp")
    report = check_dataframe(
        frame,
        required_columns={"city", "timestamp", "temperature"},
        numeric_columns={"temperature"},
    )
    assert report.result == "FAIL"
    assert report.missing_columns == ("timestamp",)
