"""Pydantic response contracts for the analytics API."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class CityMeta(BaseModel):
    id: str
    name: str
    country: str
    latitude: float
    longitude: float
    timezone: str


class Observation(BaseModel):
    city: str
    observed_at: datetime
    local_time: datetime
    temperature: float | None
    relative_humidity: float | None
    precipitation: float | None
    wind_speed: float | None
    surface_pressure: float | None
    weather_code: int | None
    pm2_5: float | None
    pm10: float | None
    nitrogen_dioxide: float | None
    ozone: float | None
    air_quality_index: float | None


class SeriesPoint(BaseModel):
    timestamp: datetime
    values: dict[str, float | None]


class CitySnapshot(BaseModel):
    city: CityMeta
    observation: Observation
    temperature_sparkline: list[float]


class PipelinePulse(BaseModel):
    status: str
    last_run: datetime | None
    rows_inserted: int
    quality_status: str | None


class OverviewResponse(BaseModel):
    selected: CitySnapshot
    cities: list[CitySnapshot]
    recent_weather: list[SeriesPoint]
    recent_air_quality: list[SeriesPoint]
    pipeline: PipelinePulse


class CitySummaryResponse(BaseModel):
    city: CityMeta
    latest: Observation
    period_start: datetime
    period_end: datetime
    rows: int
    means: dict[str, float | None]
    totals: dict[str, float | None]


class SeriesResponse(BaseModel):
    city: CityMeta
    start: datetime
    end: datetime
    points: list[SeriesPoint]


class ComparisonItem(BaseModel):
    city: CityMeta
    value: float
    latest: float | None = None


class ComparisonResponse(BaseModel):
    metric: str
    unit: str
    start: datetime
    end: datetime
    items: list[ComparisonItem]


class QualityCheck(BaseModel):
    name: str
    status: str
    value: float
    unit: str


class QualitySummaryResponse(BaseModel):
    status: str
    passed: int
    total: int
    records_checked: int
    checks: list[QualityCheck]


class QualityRun(BaseModel):
    run_id: str
    city: str
    dataset: str
    created_at: datetime
    status: str
    rows: int
    null_ratio: float
    duplicate_ratio: float
    timestamp_gaps: int
    invalid_numeric: int
    range_violations: int


class CollectionRun(BaseModel):
    started_at: datetime
    status: str
    city: str
    dataset: str
    rows_fetched: int
    rows_inserted: int
    rows_skipped: int
    quality_status: str | None
    duration_ms: float | None
    error_type: str | None


class Watermark(BaseModel):
    city: str
    dataset: str
    latest_timestamp: datetime
    updated_at: datetime


class Anomaly(BaseModel):
    city: str
    timestamp: datetime
    metric: str
    value: float
    score: float


class Correlation(BaseModel):
    metric_x: str
    metric_y: str
    correlation: float | None
    status: str


class HealthResponse(BaseModel):
    status: str = Field(examples=["ok"])
