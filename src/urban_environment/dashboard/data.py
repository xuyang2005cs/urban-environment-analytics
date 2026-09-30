"""Cached-friendly DuckDB queries used by the Streamlit dashboard."""

from __future__ import annotations

from pathlib import Path

import duckdb
import pandas as pd


class DashboardRepository:
    def __init__(self, database_path: Path) -> None:
        self.database_path = database_path

    def _query(self, sql: str, params: list[object] | None = None) -> pd.DataFrame:
        if not self.database_path.exists():
            return pd.DataFrame()
        try:
            with duckdb.connect(str(self.database_path), read_only=True) as connection:
                return connection.execute(sql, params or []).fetchdf()
        except duckdb.Error:
            return pd.DataFrame()

    def environment(self, cities: list[str] | None = None) -> pd.DataFrame:
        sql = "SELECT * FROM environment_hourly"
        params: list[object] = []
        if cities:
            sql += " WHERE city IN (" + ",".join("?" for _ in cities) + ")"
            params.extend(cities)
        sql += " ORDER BY timestamp"
        return self._query(sql, params)

    def daily_summary(self) -> pd.DataFrame:
        return self._query("SELECT * FROM city_daily_summary ORDER BY local_date, city")

    def recent_runs(self, limit: int = 10) -> pd.DataFrame:
        return self._query(
            """SELECT started_at, status, city, dataset, rows_fetched, rows_inserted,
            rows_skipped, quality_status, duration_ms, error_type
            FROM collection_runs ORDER BY started_at DESC LIMIT ?""",
            [limit],
        )

    def watermarks(self) -> pd.DataFrame:
        return self._query(
            "SELECT city, dataset, latest_timestamp, updated_at FROM pipeline_watermarks ORDER BY city, dataset"
        )

    def quality_runs(self, limit: int = 30) -> pd.DataFrame:
        return self._query(
            "SELECT * FROM quality_runs ORDER BY created_at DESC LIMIT ?", [limit]
        )
