from __future__ import annotations

import copy
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

import pytest

from urban_environment.pipeline import DataPipeline


class FakeClient:
    def __init__(self, weather, air, *, fail_air=False):
        self.weather = weather
        self.air = air
        self.fail_air = fail_air

    def __enter__(self):
        return self

    def __exit__(self, *_):
        return None

    def fetch_weather(self, **_):
        return copy.deepcopy(self.weather)

    def fetch_air_quality(self, **_):
        if self.fail_air:
            raise TimeoutError("synthetic timeout")
        return copy.deepcopy(self.air)


def make_pipeline(tmp_path, beijing, weather_payload, air_payload, *, fail_air=False):
    return DataPipeline(
        root=tmp_path,
        cities=[beijing],
        client_factory=lambda: FakeClient(weather_payload, air_payload, fail_air=fail_air),
    )


def test_pipeline_bootstrap_writes_both_datasets(tmp_path, beijing, weather_payload, air_payload):
    summary = make_pipeline(tmp_path, beijing, weather_payload, air_payload).run()
    assert summary.result == "PASS"
    assert summary.rows_fetched == 4
    assert summary.rows_inserted == 4
    assert (tmp_path / "data/analytics/environment.duckdb").exists()


def test_pipeline_explicit_rerun_skips_duplicates(tmp_path, beijing, weather_payload, air_payload):
    pipeline = make_pipeline(tmp_path, beijing, weather_payload, air_payload)
    pipeline.run(start_date="2026-09-23", end_date="2026-09-23")
    second = pipeline.run(start_date="2026-09-23", end_date="2026-09-23")
    assert second.rows_inserted == 0
    assert second.rows_skipped == 4


def test_pipeline_watermark_prevents_refetch(tmp_path, beijing, weather_payload, air_payload):
    pipeline = make_pipeline(tmp_path, beijing, weather_payload, air_payload)
    local_now = datetime.now(ZoneInfo(beijing.timezone))
    end_of_available_window = (local_now - timedelta(days=1)).replace(
        hour=23, minute=0, second=0, microsecond=0
    ).astimezone(timezone.utc)
    pipeline.database.set_watermark("beijing", "weather", end_of_available_window)
    pipeline.database.set_watermark("beijing", "air_quality", end_of_available_window)
    second = pipeline.run()
    assert second.rows_fetched == 0
    assert {run.status for run in second.runs} == {"NO_DATA"}


def test_pipeline_records_partial_failure(tmp_path, beijing, weather_payload, air_payload):
    summary = make_pipeline(
        tmp_path, beijing, weather_payload, air_payload, fail_air=True
    ).run(start_date="2026-09-23", end_date="2026-09-23")
    assert summary.result == "WARN"
    assert [run.status for run in summary.runs] == ["SUCCESS", "FAILED"]
    assert "TimeoutError" in summary.runs[1].error


def test_pipeline_rejects_unknown_city(tmp_path, beijing, weather_payload, air_payload):
    pipeline = make_pipeline(tmp_path, beijing, weather_payload, air_payload)
    with pytest.raises(ValueError, match="unknown cities"):
        pipeline.run(city_ids=["missing"])


def test_pipeline_rejects_partial_explicit_window(tmp_path, beijing, weather_payload, air_payload):
    pipeline = make_pipeline(tmp_path, beijing, weather_payload, air_payload)
    with pytest.raises(ValueError, match="provided together"):
        pipeline.run(start_date="2026-09-23")


def test_pipeline_logs_collection_runs(tmp_path, beijing, weather_payload, air_payload):
    pipeline = make_pipeline(tmp_path, beijing, weather_payload, air_payload)
    pipeline.run(start_date="2026-09-23", end_date="2026-09-23")
    runs = pipeline.database.query_dataframe("SELECT * FROM collection_runs")
    assert len(runs) == 2
    assert set(runs["status"]) == {"SUCCESS"}
    assert set(runs["quality_status"]) == {"PASS"}


def test_pipeline_does_not_update_failed_dataset_watermark(tmp_path, beijing, weather_payload, air_payload):
    pipeline = make_pipeline(
        tmp_path, beijing, weather_payload, air_payload, fail_air=True
    )
    pipeline.run(start_date="2026-09-23", end_date="2026-09-23")
    assert pipeline.database.get_watermark("beijing", "weather") is not None
    assert pipeline.database.get_watermark("beijing", "air_quality") is None

