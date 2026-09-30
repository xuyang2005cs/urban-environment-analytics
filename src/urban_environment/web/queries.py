"""Small DuckDB query layer used only by the presentation API."""

from __future__ import annotations

from datetime import date
from pathlib import Path

import duckdb
import pandas as pd


class AnalyticsUnavailableError(RuntimeError):
    """Raised when the local analytics database cannot answer a query."""


class AnalyticsRepository:
    def __init__(self, database_path: Path) -> None:
        self.database_path = database_path

    def query(self, sql: str, params: list[object] | None = None) -> pd.DataFrame:
        if not self.database_path.exists():
            raise AnalyticsUnavailableError("Analytics database has not been initialized")
        try:
            with duckdb.connect(str(self.database_path), read_only=True) as connection:
                return connection.execute(sql, params or []).fetchdf()
        except duckdb.Error as exc:
            raise AnalyticsUnavailableError("Analytics query failed") from exc

    def environment(
        self,
        *,
        cities: list[str] | None = None,
        start: date | None = None,
        end: date | None = None,
    ) -> pd.DataFrame:
        clauses: list[str] = []
        params: list[object] = []
        if cities:
            clauses.append("city IN (" + ",".join("?" for _ in cities) + ")")
            params.extend(cities)
        if start:
            clauses.append("CAST(timestamp AS DATE) >= ?")
            params.append(start)
        if end:
            clauses.append("CAST(timestamp AS DATE) <= ?")
            params.append(end)
        where = " WHERE " + " AND ".join(clauses) if clauses else ""
        return self.query(f"SELECT * FROM environment_hourly{where} ORDER BY timestamp", params)

    def collection_runs(self, limit: int = 30) -> pd.DataFrame:
        return self.query(
            """SELECT started_at, status, city, dataset, rows_fetched, rows_inserted,
            rows_skipped, quality_status, duration_ms, error_type
            FROM collection_runs ORDER BY started_at DESC LIMIT ?""",
            [limit],
        )

    def quality_runs(self, limit: int = 100) -> pd.DataFrame:
        return self.query("SELECT * FROM quality_runs ORDER BY created_at DESC LIMIT ?", [limit])

    def watermarks(self) -> pd.DataFrame:
        return self.query(
            "SELECT city, dataset, latest_timestamp, updated_at "
            "FROM pipeline_watermarks ORDER BY city, dataset"
        )
