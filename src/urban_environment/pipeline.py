"""Incremental Raw → Clean Parquet → DuckDB pipeline and CLI."""

from __future__ import annotations

import argparse
import json
import os
import time
import uuid
from dataclasses import asdict, dataclass
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Callable
from zoneinfo import ZoneInfo

from urban_environment.collectors.open_meteo import OpenMeteoClient
from urban_environment.models.city import City
from urban_environment.processing.normalization import (
    air_quality_to_dataframe,
    weather_to_dataframe,
)
from urban_environment.quality.checks import QualityReport, check_dataframe
from urban_environment.storage.duckdb_store import DuckDBStore
from urban_environment.storage.parquet import ParquetStore
from urban_environment.utils.collection import write_json
from urban_environment.utils.config import load_cities


ROOT = Path(__file__).resolve().parents[2]


@dataclass
class DatasetRun:
    city: str
    dataset: str
    requested_start: str | None
    requested_end: str | None
    rows_fetched: int = 0
    rows_normalized: int = 0
    rows_inserted: int = 0
    rows_skipped: int = 0
    quality_status: str = "NOT_RUN"
    status: str = "PENDING"
    watermark_before: str | None = None
    watermark_after: str | None = None
    error: str | None = None


@dataclass
class PipelineSummary:
    started_at: str
    finished_at: str
    runs: list[DatasetRun]

    @property
    def rows_fetched(self) -> int:
        return sum(run.rows_fetched for run in self.runs)

    @property
    def rows_inserted(self) -> int:
        return sum(run.rows_inserted for run in self.runs)

    @property
    def rows_skipped(self) -> int:
        return sum(run.rows_skipped for run in self.runs)

    @property
    def result(self) -> str:
        return "PASS" if all(run.status in {"SUCCESS", "NO_DATA"} for run in self.runs) else "WARN"

    def to_dict(self) -> dict[str, object]:
        return {
            "started_at": self.started_at,
            "finished_at": self.finished_at,
            "runs": [asdict(run) for run in self.runs],
            "rows_fetched": self.rows_fetched,
            "rows_inserted": self.rows_inserted,
            "rows_skipped": self.rows_skipped,
            "result": self.result,
        }


class DataPipeline:
    """Coordinate incremental API collection, clean storage and metadata."""

    def __init__(
        self,
        *,
        root: Path = ROOT,
        client_factory: Callable[[], OpenMeteoClient] | None = None,
        cities: list[City] | None = None,
        bootstrap_days: int = 7,
    ) -> None:
        self.root = root
        self.cities = cities or load_cities(root / "config" / "cities.json")
        self.parquet = ParquetStore(root / "data" / "processed")
        self.database = DuckDBStore(
            root / "data" / "analytics" / "environment.duckdb",
            root / "data" / "processed",
        )
        self.bootstrap_days = bootstrap_days
        self.client_factory = client_factory or self._default_client

    @staticmethod
    def _default_client() -> OpenMeteoClient:
        return OpenMeteoClient(
            connect_timeout=float(os.getenv("OPEN_METEO_CONNECT_TIMEOUT", "5")),
            read_timeout=float(os.getenv("OPEN_METEO_READ_TIMEOUT", "20")),
            max_attempts=int(os.getenv("OPEN_METEO_MAX_ATTEMPTS", "3")),
        )

    def run(
        self,
        *,
        city_ids: list[str] | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
    ) -> PipelineSummary:
        selected = [city for city in self.cities if not city_ids or city.id in city_ids]
        unknown = set(city_ids or ()).difference(city.id for city in selected)
        if unknown:
            raise ValueError(f"unknown cities: {', '.join(sorted(unknown))}")
        if (start_date is None) != (end_date is None):
            raise ValueError("start_date and end_date must be provided together")

        started = datetime.now(timezone.utc)
        runs: list[DatasetRun] = []
        with self.client_factory() as client:
            for city in selected:
                for dataset in ("weather", "air_quality"):
                    requested = self._request_window(
                        city, dataset, explicit_start=start_date, explicit_end=end_date
                    )
                    runs.append(self._run_dataset(client, city, dataset, requested))
        self.database.refresh_views()
        finished = datetime.now(timezone.utc)
        summary = PipelineSummary(started.isoformat(), finished.isoformat(), runs)
        write_json(self.root / "data" / "reports" / "latest_pipeline.json", summary.to_dict())
        return summary

    def _request_window(
        self,
        city: City,
        dataset: str,
        *,
        explicit_start: str | None,
        explicit_end: str | None,
    ) -> tuple[str, str] | None:
        if explicit_start and explicit_end:
            if explicit_start > explicit_end:
                raise ValueError("start_date must not be after end_date")
            return explicit_start, explicit_end

        local_today = datetime.now(ZoneInfo(city.timezone)).date()
        available_end = local_today - timedelta(days=1)
        watermark = self.database.get_watermark(city.id, dataset)
        if watermark is None:
            start = available_end - timedelta(days=self.bootstrap_days - 1)
        else:
            next_local = watermark.astimezone(ZoneInfo(city.timezone)) + timedelta(hours=1)
            start = next_local.date()
        if start > available_end:
            return None
        return start.isoformat(), available_end.isoformat()

    def _run_dataset(
        self,
        client: OpenMeteoClient,
        city: City,
        dataset: str,
        requested: tuple[str, str] | None,
    ) -> DatasetRun:
        run_id = str(uuid.uuid4())
        started = datetime.now(timezone.utc)
        before = self.database.get_watermark(city.id, dataset)
        result = DatasetRun(
            city=city.id,
            dataset=dataset,
            requested_start=requested[0] if requested else None,
            requested_end=requested[1] if requested else None,
            watermark_before=before.isoformat() if before else None,
        )
        self.database.begin_run(
            {
                "run_id": run_id,
                "started_at": started,
                "city": city.id,
                "dataset": dataset,
                "requested_start": result.requested_start,
                "requested_end": result.requested_end,
            }
        )

        if requested is None:
            result.status = "NO_DATA"
            result.quality_status = "NOT_RUN"
            self._finish_metadata(run_id, started, result)
            return result

        try:
            fetch = client.fetch_weather if dataset == "weather" else client.fetch_air_quality
            payload = fetch(
                latitude=city.latitude,
                longitude=city.longitude,
                start_date=requested[0],
                end_date=requested[1],
                timezone=city.timezone,
            )
            raw_path = (
                self.root / "data" / "raw" / date.today().isoformat() / city.id / f"{dataset}.json"
            )
            write_json(raw_path, payload)
            result.rows_fetched = len(payload["hourly"]["time"])

            normalize = weather_to_dataframe if dataset == "weather" else air_quality_to_dataframe
            frame = normalize(
                payload,
                city.id,
                country=city.country,
                timezone_name=city.timezone,
                ingested_at=started,
            )
            result.rows_normalized = len(frame)
            report = self._quality_report(dataset, frame)
            result.quality_status = report.result
            write_result = self.parquet.write_incremental(dataset, frame)
            result.rows_inserted = write_result.inserted
            result.rows_skipped = write_result.skipped
            latest = frame["timestamp"].max().to_pydatetime()
            self.database.set_watermark(city.id, dataset, latest)
            after = self.database.get_watermark(city.id, dataset)
            result.watermark_after = after.isoformat() if after else None
            result.status = "SUCCESS"
            self.database.save_quality_run(run_id, city.id, dataset, report)
            write_json(
                self.root / "data" / "reports" / f"quality-{run_id}.json",
                report.to_dict(),
            )
        except Exception as exc:  # Per-dataset isolation is intentional.
            result.status = "FAILED"
            result.error = f"{type(exc).__name__}: {exc}"
        self._finish_metadata(run_id, started, result)
        return result

    def _finish_metadata(self, run_id: str, started: datetime, result: DatasetRun) -> None:
        finished = datetime.now(timezone.utc)
        error_type, _, error_message = (result.error or "").partition(": ")
        self.database.finish_run(
            run_id,
            {
                "finished_at": finished,
                "status": result.status,
                "rows_fetched": result.rows_fetched,
                "rows_normalized": result.rows_normalized,
                "rows_inserted": result.rows_inserted,
                "rows_skipped": result.rows_skipped,
                "quality_status": result.quality_status,
                "duration_ms": round((finished - started).total_seconds() * 1000, 1),
                "error_type": error_type or None,
                "error_message": error_message or None,
            },
        )

    @staticmethod
    def _quality_report(dataset: str, frame) -> QualityReport:
        if dataset == "weather":
            required = {
                "city", "country", "timestamp", "timezone", "temperature",
                "relative_humidity", "precipitation", "wind_speed", "surface_pressure",
                "source", "ingested_at",
            }
            numeric = {
                "temperature", "relative_humidity", "precipitation", "wind_speed",
                "surface_pressure",
            }
            ranges = {
                "relative_humidity": (0, 100),
                "precipitation": (0, None),
                "wind_speed": (0, None),
                "surface_pressure": (500, 1200),
            }
        else:
            required = {
                "city", "country", "timestamp", "timezone", "pm2_5", "pm10",
                "nitrogen_dioxide", "ozone", "air_quality_index", "source", "ingested_at",
            }
            numeric = {"pm2_5", "pm10", "nitrogen_dioxide", "ozone", "air_quality_index"}
            ranges = {column: (0, None) for column in numeric}
        return check_dataframe(
            frame,
            required_columns=required,
            numeric_columns=numeric,
            ranges=ranges,
        )


def print_summary(summary: PipelineSummary) -> None:
    print("ENVIRONMENT_PIPELINE")
    for run in summary.runs:
        print(
            f"CITY={run.city} DATASET={run.dataset} STATUS={run.status} "
            f"ROWS_FETCHED={run.rows_fetched} ROWS_NORMALIZED={run.rows_normalized} "
            f"ROWS_INSERTED={run.rows_inserted} ROWS_SKIPPED_DUPLICATE={run.rows_skipped} "
            f"QUALITY_STATUS={run.quality_status}"
        )
    print(f"ROWS_FETCHED={summary.rows_fetched}")
    print(f"ROWS_INSERTED={summary.rows_inserted}")
    print(f"ROWS_SKIPPED={summary.rows_skipped}")
    print(f"RESULT={summary.result}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Urban environment incremental pipeline")
    subparsers = parser.add_subparsers(dest="command", required=True)
    collect = subparsers.add_parser("collect", help="Run an incremental collection")
    selection = collect.add_mutually_exclusive_group()
    selection.add_argument("--city", action="append", dest="cities")
    selection.add_argument("--all-cities", action="store_true")
    collect.add_argument("--start")
    collect.add_argument("--end")
    subparsers.add_parser("scheduler", help="Start the hourly scheduler")
    args = parser.parse_args(argv)

    if args.command == "scheduler":
        from urban_environment.scheduler import run_scheduler

        run_scheduler(ROOT)
        return 0

    summary = DataPipeline().run(
        city_ids=args.cities if not args.all_cities else None,
        start_date=args.start,
        end_date=args.end,
    )
    print_summary(summary)
    return 0 if summary.result == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
