"""FastAPI routes exposing the local analytics layer as read-only JSON."""

from __future__ import annotations

from datetime import date
from zoneinfo import ZoneInfo

import pandas as pd
from fastapi import APIRouter, Depends, HTTPException, Query, Request

from urban_environment.analytics.environment import correlation_exploration, detect_anomalies
from urban_environment.models.city import City
from urban_environment.utils.config import load_cities
from urban_environment.web.queries import AnalyticsRepository
from urban_environment.web.schemas import (
    Anomaly,
    CityMeta,
    CitySnapshot,
    CitySummaryResponse,
    CollectionRun,
    ComparisonItem,
    ComparisonResponse,
    Correlation,
    HealthResponse,
    Observation,
    OverviewResponse,
    PipelinePulse,
    QualityCheck,
    QualityRun,
    QualitySummaryResponse,
    SeriesPoint,
    SeriesResponse,
    Watermark,
)


router = APIRouter(prefix="/api")

WEATHER_METRICS = ("temperature", "relative_humidity", "precipitation", "wind_speed", "surface_pressure", "weather_code")
AIR_METRICS = ("air_quality_index", "pm2_5", "pm10", "nitrogen_dioxide", "ozone")
COMPARISON_UNITS = {
    "temperature": "°C",
    "pm2_5": "μg/m³",
    "air_quality_index": "European AQI",
    "precipitation": "mm",
    "wind_speed": "km/h",
}


def repository(request: Request) -> AnalyticsRepository:
    return request.app.state.repository


def cities(request: Request) -> list[City]:
    return request.app.state.cities


def city_by_id(city_id: str, configured: list[City]) -> City:
    match = next((city for city in configured if city.id == city_id), None)
    if match is None:
        raise HTTPException(status_code=404, detail="Unknown city")
    return match


def city_meta(city: City) -> CityMeta:
    return CityMeta(**city.__dict__)


def number(value: object, *, integer: bool = False) -> float | int | None:
    if pd.isna(value):
        return None
    return int(value) if integer else round(float(value), 3)


def observation(row: pd.Series, city: City) -> Observation:
    observed = pd.Timestamp(row["timestamp"]).tz_convert("UTC").to_pydatetime()
    local = observed.astimezone(ZoneInfo(city.timezone))
    values = {name: number(row.get(name), integer=name == "weather_code") for name in (*WEATHER_METRICS, *AIR_METRICS)}
    return Observation(city=city.id, observed_at=observed, local_time=local, **values)


def points(frame: pd.DataFrame, metrics: tuple[str, ...]) -> list[SeriesPoint]:
    return [
        SeriesPoint(
            timestamp=pd.Timestamp(row.timestamp).tz_convert("UTC").to_pydatetime(),
            values={metric: number(getattr(row, metric)) for metric in metrics},
        )
        for row in frame.itertuples()
    ]


def checked_range(start: date | None, end: date | None) -> tuple[date | None, date | None]:
    if start and end and start > end:
        raise HTTPException(status_code=422, detail="start must not be after end")
    return start, end


def require_data(frame: pd.DataFrame) -> pd.DataFrame:
    if frame.empty:
        raise HTTPException(status_code=404, detail="No observations for this selection")
    return frame


@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok")


@router.get("/meta/cities", response_model=list[CityMeta])
def meta_cities(configured: list[City] = Depends(cities)) -> list[CityMeta]:
    return [city_meta(city) for city in configured]


@router.get("/overview", response_model=OverviewResponse)
def overview(
    city: str = "beijing",
    repo: AnalyticsRepository = Depends(repository),
    configured: list[City] = Depends(cities),
) -> OverviewResponse:
    selected_city = city_by_id(city, configured)
    frame = require_data(repo.environment())
    snapshots: list[CitySnapshot] = []
    for item in configured:
        local = frame[frame.city == item.id].sort_values("timestamp")
        if local.empty:
            continue
        snapshots.append(
            CitySnapshot(
                city=city_meta(item),
                observation=observation(local.iloc[-1], item),
                temperature_sparkline=[round(float(value), 2) for value in local.temperature.tail(24)],
            )
        )
    selected = next((item for item in snapshots if item.city.id == selected_city.id), None)
    if selected is None:
        raise HTTPException(status_code=404, detail="No observations for this city")
    recent = frame[frame.city == selected_city.id].sort_values("timestamp").tail(48)
    runs = repo.collection_runs(1)
    pulse = PipelinePulse(status="NO_RUN", last_run=None, rows_inserted=0, quality_status=None)
    if not runs.empty:
        latest = runs.iloc[0]
        pulse = PipelinePulse(
            status=str(latest.status),
            last_run=pd.Timestamp(latest.started_at).to_pydatetime(),
            rows_inserted=int(latest.rows_inserted),
            quality_status=None if pd.isna(latest.quality_status) else str(latest.quality_status),
        )
    return OverviewResponse(
        selected=selected,
        cities=snapshots,
        recent_weather=points(recent, WEATHER_METRICS[:-1]),
        recent_air_quality=points(recent, AIR_METRICS),
        pipeline=pulse,
    )


@router.get("/cities/{city_id}/summary", response_model=CitySummaryResponse)
def city_summary(
    city_id: str,
    start: date | None = None,
    end: date | None = None,
    repo: AnalyticsRepository = Depends(repository),
    configured: list[City] = Depends(cities),
) -> CitySummaryResponse:
    city = city_by_id(city_id, configured)
    start, end = checked_range(start, end)
    frame = require_data(repo.environment(cities=[city.id], start=start, end=end))
    numeric = [*WEATHER_METRICS[:-1], *AIR_METRICS]
    means = {metric: number(frame[metric].mean()) for metric in numeric}
    return CitySummaryResponse(
        city=city_meta(city),
        latest=observation(frame.iloc[-1], city),
        period_start=pd.Timestamp(frame.timestamp.min()).to_pydatetime(),
        period_end=pd.Timestamp(frame.timestamp.max()).to_pydatetime(),
        rows=len(frame),
        means=means,
        totals={"precipitation": number(frame.precipitation.sum())},
    )


def series_response(city: City, frame: pd.DataFrame, metrics: tuple[str, ...]) -> SeriesResponse:
    frame = require_data(frame)
    return SeriesResponse(
        city=city_meta(city),
        start=pd.Timestamp(frame.timestamp.min()).to_pydatetime(),
        end=pd.Timestamp(frame.timestamp.max()).to_pydatetime(),
        points=points(frame, metrics),
    )


@router.get("/cities/{city_id}/weather-series", response_model=SeriesResponse)
def weather_series(
    city_id: str,
    start: date | None = None,
    end: date | None = None,
    repo: AnalyticsRepository = Depends(repository),
    configured: list[City] = Depends(cities),
) -> SeriesResponse:
    city = city_by_id(city_id, configured)
    start, end = checked_range(start, end)
    return series_response(city, repo.environment(cities=[city.id], start=start, end=end), WEATHER_METRICS)


@router.get("/cities/{city_id}/air-quality-series", response_model=SeriesResponse)
def air_quality_series(
    city_id: str,
    start: date | None = None,
    end: date | None = None,
    repo: AnalyticsRepository = Depends(repository),
    configured: list[City] = Depends(cities),
) -> SeriesResponse:
    city = city_by_id(city_id, configured)
    start, end = checked_range(start, end)
    return series_response(city, repo.environment(cities=[city.id], start=start, end=end), AIR_METRICS)


@router.get("/comparison", response_model=ComparisonResponse)
def comparison(
    metric: str = Query("temperature"),
    city: list[str] | None = Query(None),
    start: date | None = None,
    end: date | None = None,
    repo: AnalyticsRepository = Depends(repository),
    configured: list[City] = Depends(cities),
) -> ComparisonResponse:
    if metric not in COMPARISON_UNITS:
        raise HTTPException(status_code=422, detail="Unsupported comparison metric")
    selected = city or [item.id for item in configured]
    selected_cities = [city_by_id(item, configured) for item in selected]
    start, end = checked_range(start, end)
    frame = require_data(repo.environment(cities=selected, start=start, end=end))
    items = []
    for item in selected_cities:
        local = frame[frame.city == item.id]
        if local.empty:
            continue
        items.append(
            ComparisonItem(
                city=city_meta(item),
                value=round(float(local[metric].mean()), 3),
                latest=number(local.iloc[-1][metric]),
            )
        )
    items.sort(key=lambda item: item.value)
    return ComparisonResponse(
        metric=metric,
        unit=COMPARISON_UNITS[metric],
        start=pd.Timestamp(frame.timestamp.min()).to_pydatetime(),
        end=pd.Timestamp(frame.timestamp.max()).to_pydatetime(),
        items=items,
    )


@router.get("/quality/summary", response_model=QualitySummaryResponse)
def quality_summary(repo: AnalyticsRepository = Depends(repository)) -> QualitySummaryResponse:
    frame = require_data(repo.quality_runs(500))
    latest = frame.sort_values("created_at").groupby(["city", "dataset"], as_index=False).tail(1)
    checks = [
        QualityCheck(name="Schema", status="PASS", value=float(len(latest)), unit="reports"),
        QualityCheck(name="Completeness", status="PASS" if latest.null_ratio.max() == 0 else "WARN", value=float(latest.null_ratio.mean()), unit="ratio"),
        QualityCheck(name="Duplicates", status="PASS" if latest.duplicate_ratio.max() == 0 else "WARN", value=float(latest.duplicate_ratio.mean()), unit="ratio"),
        QualityCheck(name="Continuity", status="PASS" if latest.timestamp_gaps.sum() == 0 else "WARN", value=float(latest.timestamp_gaps.sum()), unit="gaps"),
        QualityCheck(name="Numeric", status="PASS" if latest.invalid_numeric.sum() == 0 else "WARN", value=float(latest.invalid_numeric.sum()), unit="records"),
        QualityCheck(name="Range", status="PASS" if latest.range_violations.sum() == 0 else "WARN", value=float(latest.range_violations.sum()), unit="records"),
    ]
    passed = sum(check.status == "PASS" for check in checks)
    status = "FAIL" if "FAIL" in set(latest.status) else "PASS" if passed == len(checks) else "WARN"
    return QualitySummaryResponse(status=status, passed=passed, total=len(checks), records_checked=int(latest.rows.sum()), checks=checks)


@router.get("/quality/runs", response_model=list[QualityRun])
def quality_runs(limit: int = Query(30, ge=1, le=200), repo: AnalyticsRepository = Depends(repository)) -> list[QualityRun]:
    return [QualityRun(**row) for row in repo.quality_runs(limit).to_dict("records")]


@router.get("/pipeline/runs", response_model=list[CollectionRun])
def pipeline_runs(limit: int = Query(30, ge=1, le=200), repo: AnalyticsRepository = Depends(repository)) -> list[CollectionRun]:
    return [CollectionRun(**row) for row in repo.collection_runs(limit).to_dict("records")]


@router.get("/pipeline/watermarks", response_model=list[Watermark])
def pipeline_watermarks(repo: AnalyticsRepository = Depends(repository)) -> list[Watermark]:
    return [Watermark(**row) for row in repo.watermarks().to_dict("records")]


@router.get("/anomalies", response_model=list[Anomaly])
def anomalies(city: str | None = None, repo: AnalyticsRepository = Depends(repository), configured: list[City] = Depends(cities)) -> list[Anomaly]:
    selected = [city_by_id(city, configured).id] if city else None
    frame = require_data(repo.environment(cities=selected))
    result = detect_anomalies(frame)
    return [Anomaly(**row) for row in result.to_dict("records")]


@router.get("/correlation", response_model=list[Correlation])
def correlation(city: str | None = None, repo: AnalyticsRepository = Depends(repository), configured: list[City] = Depends(cities)) -> list[Correlation]:
    selected = [city_by_id(city, configured).id] if city else None
    frame = require_data(repo.environment(cities=selected))
    result = correlation_exploration(frame)
    return [Correlation(**row) for row in result.to_dict("records")]
