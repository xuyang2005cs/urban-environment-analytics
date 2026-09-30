"""Centralized, retry-aware client for Open-Meteo public APIs."""

from __future__ import annotations

import time
from collections.abc import Callable, Mapping
from typing import Any

import httpx


GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
WEATHER_URL = "https://archive-api.open-meteo.com/v1/archive"
AIR_QUALITY_URL = "https://air-quality-api.open-meteo.com/v1/air-quality"

WEATHER_VARIABLES = (
    "temperature_2m",
    "relative_humidity_2m",
    "precipitation",
    "wind_speed_10m",
    "surface_pressure",
    "weather_code",
)
AIR_QUALITY_VARIABLES = (
    "pm2_5",
    "pm10",
    "nitrogen_dioxide",
    "ozone",
    "european_aqi",
)


class OpenMeteoError(RuntimeError):
    """Base error for Open-Meteo collection failures."""


class OpenMeteoTransportError(OpenMeteoError):
    """Raised after retryable transport failures are exhausted."""


class OpenMeteoHTTPError(OpenMeteoError):
    """Raised for a non-successful API response."""


class OpenMeteoResponseError(OpenMeteoError):
    """Raised when a successful response has invalid JSON or structure."""


class OpenMeteoClient:
    """Small synchronous client shared by probes and collection scripts."""

    def __init__(
        self,
        *,
        client: httpx.Client | None = None,
        connect_timeout: float = 5.0,
        read_timeout: float = 20.0,
        max_attempts: int = 3,
        backoff_seconds: float = 0.5,
        sleep: Callable[[float], None] = time.sleep,
    ) -> None:
        if max_attempts < 1:
            raise ValueError("max_attempts must be at least 1")
        self._owns_client = client is None
        self._client = client or httpx.Client(
            timeout=httpx.Timeout(read_timeout, connect=connect_timeout),
            headers={"User-Agent": "urban-environment-analytics/0.1"},
        )
        self._max_attempts = max_attempts
        self._backoff_seconds = backoff_seconds
        self._sleep = sleep

    def __enter__(self) -> OpenMeteoClient:
        return self

    def __exit__(self, *_: object) -> None:
        self.close()

    def close(self) -> None:
        """Close the internally created HTTP client."""

        if self._owns_client:
            self._client.close()

    def geocode(
        self, name: str, *, country_code: str, language: str = "en"
    ) -> dict[str, Any]:
        """Return the best country-filtered geocoding match."""

        payload = self._get_json(
            GEOCODING_URL,
            {"name": name, "countryCode": country_code, "count": 10, "language": language},
        )
        results = payload.get("results")
        if not isinstance(results, list) or not results:
            raise OpenMeteoResponseError(f"No geocoding result for {name!r}")
        required = {"name", "country", "country_code", "latitude", "longitude", "timezone"}
        for result in results:
            if isinstance(result, dict) and required.issubset(result):
                return result
        raise OpenMeteoResponseError("Geocoding results are missing required fields")

    def fetch_weather(
        self,
        *,
        latitude: float,
        longitude: float,
        start_date: str,
        end_date: str,
        timezone: str,
    ) -> dict[str, Any]:
        """Fetch hourly historical weather for an inclusive date interval."""

        return self._fetch_hourly(
            WEATHER_URL,
            latitude=latitude,
            longitude=longitude,
            start_date=start_date,
            end_date=end_date,
            timezone=timezone,
            variables=WEATHER_VARIABLES,
        )

    def fetch_air_quality(
        self,
        *,
        latitude: float,
        longitude: float,
        start_date: str,
        end_date: str,
        timezone: str,
    ) -> dict[str, Any]:
        """Fetch hourly air quality for an inclusive date interval."""

        return self._fetch_hourly(
            AIR_QUALITY_URL,
            latitude=latitude,
            longitude=longitude,
            start_date=start_date,
            end_date=end_date,
            timezone=timezone,
            variables=AIR_QUALITY_VARIABLES,
        )

    def _fetch_hourly(
        self,
        url: str,
        *,
        latitude: float,
        longitude: float,
        start_date: str,
        end_date: str,
        timezone: str,
        variables: tuple[str, ...],
    ) -> dict[str, Any]:
        payload = self._get_json(
            url,
            {
                "latitude": latitude,
                "longitude": longitude,
                "start_date": start_date,
                "end_date": end_date,
                "timezone": timezone,
                "hourly": ",".join(variables),
            },
        )
        hourly = payload.get("hourly")
        if not isinstance(hourly, dict):
            raise OpenMeteoResponseError("Response is missing the hourly object")
        expected = {"time", *variables}
        missing = expected.difference(hourly)
        if missing:
            raise OpenMeteoResponseError(
                f"Hourly response is missing fields: {', '.join(sorted(missing))}"
            )
        if not isinstance(hourly["time"], list) or not hourly["time"]:
            raise OpenMeteoResponseError("Hourly response has no timestamps")
        row_count = len(hourly["time"])
        mismatched = [
            name
            for name in variables
            if not isinstance(hourly[name], list) or len(hourly[name]) != row_count
        ]
        if mismatched:
            raise OpenMeteoResponseError(
                f"Hourly arrays do not align: {', '.join(mismatched)}"
            )
        return payload

    def _get_json(self, url: str, params: Mapping[str, object]) -> dict[str, Any]:
        last_error: Exception | None = None
        for attempt in range(1, self._max_attempts + 1):
            try:
                response = self._client.get(url, params=params)
                if response.status_code >= 500:
                    raise httpx.HTTPStatusError(
                        f"Open-Meteo server returned {response.status_code}",
                        request=response.request,
                        response=response,
                    )
                if response.status_code >= 400:
                    reason = response.text[:200]
                    raise OpenMeteoHTTPError(
                        f"Open-Meteo returned {response.status_code}: {reason}"
                    )
                try:
                    payload = response.json()
                except ValueError as exc:
                    raise OpenMeteoResponseError("Open-Meteo returned invalid JSON") from exc
                if not isinstance(payload, dict):
                    raise OpenMeteoResponseError("Open-Meteo JSON root must be an object")
                return payload
            except OpenMeteoHTTPError:
                raise
            except OpenMeteoResponseError:
                raise
            except (httpx.TimeoutException, httpx.NetworkError, httpx.HTTPStatusError) as exc:
                last_error = exc
                if attempt < self._max_attempts:
                    self._sleep(self._backoff_seconds * (2 ** (attempt - 1)))
        raise OpenMeteoTransportError(
            f"Open-Meteo request failed after {self._max_attempts} attempts"
        ) from last_error

