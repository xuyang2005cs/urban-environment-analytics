import pandas as pd

from urban_environment.quality.checks import check_dataframe


def report(frame):
    return check_dataframe(
        frame,
        required_columns={"city", "timestamp", "relative_humidity", "wind_speed"},
        numeric_columns={"relative_humidity", "wind_speed"},
        ranges={"relative_humidity": (0, 100), "wind_speed": (0, None)},
    )


def test_quality_reports_null_ratio():
    frame = pd.DataFrame({"city": ["a"], "timestamp": [pd.Timestamp("2026-01-01", tz="UTC")], "relative_humidity": [None], "wind_speed": [1]})
    result = report(frame)
    assert result.null_ratio == 0.25
    assert result.result == "WARN"


def test_quality_reports_range_violation():
    frame = pd.DataFrame({"city": ["a"], "timestamp": [pd.Timestamp("2026-01-01", tz="UTC")], "relative_humidity": [101], "wind_speed": [-1]})
    result = report(frame)
    assert result.range_violations == 2
    assert result.result == "WARN"


def test_quality_reports_hourly_gap():
    frame = pd.DataFrame({"city": ["a", "a"], "timestamp": pd.to_datetime(["2026-01-01T00:00Z", "2026-01-01T03:00Z"]), "relative_humidity": [50, 51], "wind_speed": [1, 2]})
    assert report(frame).timestamp_gaps == 1


def test_quality_reports_non_monotonic_timestamp():
    frame = pd.DataFrame({"city": ["a", "a"], "timestamp": pd.to_datetime(["2026-01-01T01:00Z", "2026-01-01T00:00Z"]), "relative_humidity": [50, 51], "wind_speed": [1, 2]})
    result = report(frame)
    assert result.timestamp_monotonic is False
    assert result.result == "WARN"
