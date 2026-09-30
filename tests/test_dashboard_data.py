from urban_environment.dashboard.data import DashboardRepository
from urban_environment.pipeline import DataPipeline
from tests.test_pipeline import FakeClient


def prepared_repository(tmp_path, beijing, weather_payload, air_payload):
    pipeline = DataPipeline(
        root=tmp_path,
        cities=[beijing],
        client_factory=lambda: FakeClient(weather_payload, air_payload),
    )
    pipeline.run(start_date="2026-09-23", end_date="2026-09-23")
    return DashboardRepository(tmp_path / "data/analytics/environment.duckdb")


def test_dashboard_query_returns_environment_data(tmp_path, beijing, weather_payload, air_payload):
    repository = prepared_repository(tmp_path, beijing, weather_payload, air_payload)
    assert len(repository.environment()) == 2


def test_dashboard_query_filters_city(tmp_path, beijing, weather_payload, air_payload):
    repository = prepared_repository(tmp_path, beijing, weather_payload, air_payload)
    assert len(repository.environment(["beijing"])) == 2
    assert repository.environment(["tokyo"]).empty


def test_dashboard_query_returns_pipeline_metadata(tmp_path, beijing, weather_payload, air_payload):
    repository = prepared_repository(tmp_path, beijing, weather_payload, air_payload)
    assert len(repository.recent_runs()) == 2
    assert len(repository.watermarks()) == 2
    assert len(repository.quality_runs()) == 2


def test_dashboard_query_handles_missing_database(tmp_path):
    repository = DashboardRepository(tmp_path / "missing.duckdb")
    assert repository.environment().empty
