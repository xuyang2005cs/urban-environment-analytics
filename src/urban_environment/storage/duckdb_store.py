"""DuckDB analytics catalog, watermarks and pipeline run tracking."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import duckdb
import pandas as pd


class DuckDBStore:
    def __init__(self, database_path: Path, processed_root: Path) -> None:
        self.database_path = database_path
        self.processed_root = processed_root
        database_path.parent.mkdir(parents=True, exist_ok=True)
        self.initialize()

    def connect(self) -> duckdb.DuckDBPyConnection:
        return duckdb.connect(str(self.database_path))

    def initialize(self) -> None:
        with self.connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS pipeline_watermarks (
                    city VARCHAR NOT NULL,
                    dataset VARCHAR NOT NULL,
                    latest_timestamp TIMESTAMPTZ NOT NULL,
                    updated_at TIMESTAMPTZ NOT NULL,
                    PRIMARY KEY (city, dataset)
                );
                CREATE TABLE IF NOT EXISTS collection_runs (
                    run_id VARCHAR PRIMARY KEY,
                    started_at TIMESTAMPTZ NOT NULL,
                    finished_at TIMESTAMPTZ,
                    status VARCHAR NOT NULL,
                    city VARCHAR NOT NULL,
                    dataset VARCHAR NOT NULL,
                    requested_start DATE,
                    requested_end DATE,
                    rows_fetched BIGINT DEFAULT 0,
                    rows_normalized BIGINT DEFAULT 0,
                    rows_inserted BIGINT DEFAULT 0,
                    rows_skipped BIGINT DEFAULT 0,
                    quality_status VARCHAR,
                    duration_ms DOUBLE,
                    error_type VARCHAR,
                    error_message VARCHAR
                );
                CREATE TABLE IF NOT EXISTS quality_runs (
                    run_id VARCHAR NOT NULL,
                    city VARCHAR NOT NULL,
                    dataset VARCHAR NOT NULL,
                    created_at TIMESTAMPTZ NOT NULL,
                    status VARCHAR NOT NULL,
                    rows BIGINT NOT NULL,
                    null_ratio DOUBLE NOT NULL,
                    duplicate_ratio DOUBLE NOT NULL,
                    timestamp_gaps BIGINT NOT NULL,
                    invalid_numeric BIGINT NOT NULL,
                    range_violations BIGINT NOT NULL
                );
                """
            )

    def refresh_views(self) -> None:
        weather = (self.processed_root / "weather" / "**" / "*.parquet").as_posix()
        air = (self.processed_root / "air_quality" / "**" / "*.parquet").as_posix()
        with self.connect() as connection:
            if list((self.processed_root / "weather").glob("**/*.parquet")):
                connection.execute(
                    f"CREATE OR REPLACE VIEW weather_clean AS "
                    f"SELECT * FROM read_parquet('{weather}', union_by_name=true, hive_partitioning=false)"
                )
            if list((self.processed_root / "air_quality").glob("**/*.parquet")):
                connection.execute(
                    f"CREATE OR REPLACE VIEW air_quality_clean AS "
                    f"SELECT * FROM read_parquet('{air}', union_by_name=true, hive_partitioning=false)"
                )
            views = {
                row[0]
                for row in connection.execute(
                    "SELECT view_name FROM duckdb_views() WHERE database_name=current_database()"
                ).fetchall()
            }
            if {"weather_clean", "air_quality_clean"}.issubset(views):
                connection.execute(
                    """
                    CREATE OR REPLACE VIEW environment_hourly AS
                    SELECT
                        w.city, w.country, w.timestamp, w.timezone,
                        w.temperature, w.relative_humidity, w.precipitation,
                        w.wind_speed, w.surface_pressure,
                        a.pm2_5, a.pm10, a.nitrogen_dioxide, a.ozone,
                        a.air_quality_index,
                        greatest(w.ingested_at, a.ingested_at) AS ingested_at
                    FROM weather_clean w
                    INNER JOIN air_quality_clean a USING (city, timestamp);

                    CREATE OR REPLACE VIEW city_daily_summary AS
                    SELECT
                        city,
                        CAST(timestamp AT TIME ZONE timezone AS DATE) AS local_date,
                        avg(temperature) AS temperature_mean,
                        min(temperature) AS temperature_min,
                        max(temperature) AS temperature_max,
                        avg(relative_humidity) AS humidity_mean,
                        avg(wind_speed) AS wind_speed_mean,
                        sum(precipitation) AS precipitation_sum,
                        avg(pm2_5) AS pm2_5_mean,
                        avg(pm10) AS pm10_mean,
                        avg(air_quality_index) AS aqi_mean
                    FROM environment_hourly
                    GROUP BY city, local_date;
                    """
                )

    def get_watermark(self, city: str, dataset: str) -> datetime | None:
        with self.connect() as connection:
            row = connection.execute(
                "SELECT latest_timestamp FROM pipeline_watermarks WHERE city=? AND dataset=?",
                [city, dataset],
            ).fetchone()
        return row[0] if row else None

    def set_watermark(self, city: str, dataset: str, timestamp: datetime) -> None:
        value = timestamp.astimezone(timezone.utc)
        with self.connect() as connection:
            connection.execute(
                """
                INSERT INTO pipeline_watermarks VALUES (?, ?, ?, ?)
                ON CONFLICT (city, dataset) DO UPDATE SET
                    latest_timestamp = greatest(pipeline_watermarks.latest_timestamp, excluded.latest_timestamp),
                    updated_at = excluded.updated_at
                """,
                [city, dataset, value, datetime.now(timezone.utc)],
            )

    def begin_run(self, values: dict[str, Any]) -> None:
        with self.connect() as connection:
            connection.execute(
                """INSERT INTO collection_runs
                (run_id, started_at, status, city, dataset, requested_start, requested_end)
                VALUES (?, ?, ?, ?, ?, ?, ?)""",
                [
                    values["run_id"], values["started_at"], "RUNNING", values["city"],
                    values["dataset"], values.get("requested_start"), values.get("requested_end"),
                ],
            )

    def finish_run(self, run_id: str, values: dict[str, Any]) -> None:
        with self.connect() as connection:
            connection.execute(
                """UPDATE collection_runs SET
                finished_at=?, status=?, rows_fetched=?, rows_normalized=?, rows_inserted=?,
                rows_skipped=?, quality_status=?, duration_ms=?, error_type=?, error_message=?
                WHERE run_id=?""",
                [
                    values["finished_at"], values["status"], values.get("rows_fetched", 0),
                    values.get("rows_normalized", 0), values.get("rows_inserted", 0),
                    values.get("rows_skipped", 0), values.get("quality_status"),
                    values.get("duration_ms"), values.get("error_type"), values.get("error_message"),
                    run_id,
                ],
            )

    def save_quality_run(self, run_id: str, city: str, dataset: str, report: Any) -> None:
        with self.connect() as connection:
            connection.execute(
                "INSERT INTO quality_runs VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                [
                    run_id, city, dataset, datetime.now(timezone.utc), report.result,
                    report.rows, report.null_ratio, report.duplicate_ratio,
                    report.timestamp_gaps, report.invalid_numeric, report.range_violations,
                ],
            )

    def query_dataframe(self, sql: str, parameters: list[Any] | None = None) -> pd.DataFrame:
        with self.connect() as connection:
            return connection.execute(sql, parameters or []).fetchdf()
