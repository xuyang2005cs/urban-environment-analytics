import pandas as pd

from urban_environment.analytics.environment import (
    city_comparison,
    correlation_exploration,
    daily_aggregation,
    detect_anomalies,
    rolling_analytics,
)


def test_daily_aggregation_has_mean_min_max(environment_frame):
    result = daily_aggregation(environment_frame)
    assert {"temperature_mean", "temperature_min", "temperature_max"}.issubset(result)
    assert len(result) == 16


def test_daily_aggregation_sums_precipitation(environment_frame):
    result = daily_aggregation(environment_frame)
    assert "precipitation_sum" in result
    assert (result["precipitation_sum"] >= 0).all()


def test_rolling_analytics_adds_24h_and_7d(environment_frame):
    result = rolling_analytics(environment_frame)
    assert "temperature_rolling_24h" in result
    assert "pm2_5_rolling_7d" in result
    assert len(result) == len(environment_frame)


def test_rolling_mean_uses_available_early_data(environment_frame):
    result = rolling_analytics(environment_frame)
    first = result[result["city"] == "beijing"].iloc[0]
    assert first["temperature_rolling_24h"] == first["temperature"]


def test_city_comparison_returns_each_city(environment_frame):
    result = city_comparison(environment_frame)
    assert set(result["city"]) == {"beijing", "tokyo"}
    assert "pm2_5_mean" in result


def test_correlation_exploration_returns_declared_pairs(environment_frame):
    result = correlation_exploration(environment_frame)
    assert len(result) == 4
    assert set(result["status"]) == {"ok"}


def test_correlation_reports_insufficient_data():
    result = correlation_exploration(pd.DataFrame({"pm2_5": [1], "wind_speed": [2]}))
    assert "insufficient data" in set(result["status"])


def test_anomaly_detection_flags_extreme_value(environment_frame):
    frame = environment_frame.copy()
    frame.loc[0, "pm2_5"] = 1000
    result = detect_anomalies(frame)
    assert ((result["city"] == "beijing") & (result["metric"] == "pm2_5")).any()


def test_anomaly_detection_does_not_mutate_input(environment_frame):
    original = environment_frame.copy(deep=True)
    detect_anomalies(environment_frame)
    pd.testing.assert_frame_equal(environment_frame, original)
