from datetime import datetime, timedelta, timezone

import pandas as pd

from urban_environment.processing.normalization import air_quality_to_dataframe, weather_to_dataframe
from urban_environment.storage.duckdb_store import DuckDBStore
from urban_environment.storage.parquet import ParquetStore


def test_parquet_write_creates_hive_style_partition(tmp_path, weather_payload):
    frame = weather_to_dataframe(weather_payload, "beijing", country="中国")
    result = ParquetStore(tmp_path).write_incremental("weather", frame)
    assert result.inserted == 2
    assert result.files[0].relative_to(tmp_path).as_posix() == "weather/city=beijing/year=2026/month=09/data.parquet"


def test_parquet_rerun_is_idempotent(tmp_path, weather_payload):
    frame = weather_to_dataframe(weather_payload, "beijing")
    store = ParquetStore(tmp_path)
    store.write_incremental("weather", frame)
    second = store.write_incremental("weather", frame)
    assert second.inserted == 0
    assert second.skipped == 2
    assert len(store.read_dataset("weather")) == 2


def test_parquet_read_empty_dataset(tmp_path):
    assert ParquetStore(tmp_path).read_dataset("weather").empty


def test_duckdb_initializes_metadata_tables(tmp_path):
    store = DuckDBStore(tmp_path / "analytics.duckdb", tmp_path / "processed")
    tables = store.query_dataframe("SHOW TABLES")["name"].tolist()
    assert {"pipeline_watermarks", "collection_runs", "quality_runs"}.issubset(tables)


def test_watermark_only_moves_forward(tmp_path):
    store = DuckDBStore(tmp_path / "analytics.duckdb", tmp_path / "processed")
    newer = datetime(2026, 9, 29, tzinfo=timezone.utc)
    store.set_watermark("beijing", "weather", newer)
    store.set_watermark("beijing", "weather", newer - timedelta(days=1))
    assert store.get_watermark("beijing", "weather") == newer


def test_duckdb_refreshes_clean_and_analytics_views(tmp_path, weather_payload, air_payload):
    processed = tmp_path / "processed"
    parquet = ParquetStore(processed)
    parquet.write_incremental("weather", weather_to_dataframe(weather_payload, "beijing"))
    parquet.write_incremental("air_quality", air_quality_to_dataframe(air_payload, "beijing"))
    store = DuckDBStore(tmp_path / "analytics.duckdb", processed)
    store.refresh_views()
    assert len(store.query_dataframe("SELECT * FROM environment_hourly")) == 2
    assert len(store.query_dataframe("SELECT * FROM city_daily_summary")) == 1

