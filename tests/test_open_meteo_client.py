"""Offline HTTPX MockTransport tests for the shared API client."""

from __future__ import annotations

import json

import httpx
import pytest

from urban_environment.collectors.open_meteo import (
    OpenMeteoClient,
    OpenMeteoHTTPError,
    OpenMeteoResponseError,
    OpenMeteoTransportError,
)


def client_for(handler, *, max_attempts: int = 3, sleep=lambda _: None):
    return OpenMeteoClient(
        client=httpx.Client(transport=httpx.MockTransport(handler)),
        max_attempts=max_attempts,
        backoff_seconds=0,
        sleep=sleep,
    )


def test_geocoding_success():
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.params["countryCode"] == "CN"
        return httpx.Response(
            200,
            json={
                "results": [
                    {
                        "name": "Beijing",
                        "country": "China",
                        "country_code": "CN",
                        "latitude": 39.9,
                        "longitude": 116.4,
                        "timezone": "Asia/Shanghai",
                    }
                ]
            },
        )

    result = client_for(handler).geocode("Beijing", country_code="CN")
    assert result["timezone"] == "Asia/Shanghai"


def test_weather_success(weather_payload):
    def handler(request: httpx.Request) -> httpx.Response:
        assert "surface_pressure" in request.url.params["hourly"]
        return httpx.Response(200, json=weather_payload)

    result = client_for(handler).fetch_weather(
        latitude=39.9,
        longitude=116.4,
        start_date="2026-09-23",
        end_date="2026-09-23",
        timezone="Asia/Shanghai",
    )
    assert len(result["hourly"]["time"]) == 2


def test_air_quality_success(air_payload):
    def handler(request: httpx.Request) -> httpx.Response:
        assert "european_aqi" in request.url.params["hourly"]
        return httpx.Response(200, json=air_payload)

    result = client_for(handler).fetch_air_quality(
        latitude=39.9,
        longitude=116.4,
        start_date="2026-09-23",
        end_date="2026-09-23",
        timezone="Asia/Shanghai",
    )
    assert result["hourly"]["pm2_5"] == [10.0, 11.0]


def test_timeout_is_retried_and_wrapped():
    attempts = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal attempts
        attempts += 1
        raise httpx.ReadTimeout("slow", request=request)

    with pytest.raises(OpenMeteoTransportError, match="3 attempts"):
        client_for(handler).geocode("Beijing", country_code="CN")
    assert attempts == 3


def test_5xx_is_retried_then_succeeds():
    attempts = 0

    def handler(_: httpx.Request) -> httpx.Response:
        nonlocal attempts
        attempts += 1
        if attempts < 3:
            return httpx.Response(503, text="busy")
        return httpx.Response(
            200,
            json={
                "results": [
                    {
                        "name": "Tokyo",
                        "country": "Japan",
                        "country_code": "JP",
                        "latitude": 35.6,
                        "longitude": 139.6,
                        "timezone": "Asia/Tokyo",
                    }
                ]
            },
        )

    result = client_for(handler).geocode("Tokyo", country_code="JP")
    assert result["country_code"] == "JP"
    assert attempts == 3


def test_4xx_is_not_retried():
    attempts = 0

    def handler(_: httpx.Request) -> httpx.Response:
        nonlocal attempts
        attempts += 1
        return httpx.Response(400, json={"error": True, "reason": "bad parameter"})

    with pytest.raises(OpenMeteoHTTPError, match="400"):
        client_for(handler).geocode("Beijing", country_code="CN")
    assert attempts == 1


def test_invalid_json():
    def handler(_: httpx.Request) -> httpx.Response:
        return httpx.Response(200, content=b"not-json")

    with pytest.raises(OpenMeteoResponseError, match="invalid JSON"):
        client_for(handler).geocode("Beijing", country_code="CN")


def test_missing_expected_hourly_field(weather_payload):
    payload = json.loads(json.dumps(weather_payload))
    del payload["hourly"]["surface_pressure"]

    def handler(_: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json=payload)

    with pytest.raises(OpenMeteoResponseError, match="surface_pressure"):
        client_for(handler).fetch_weather(
            latitude=39.9,
            longitude=116.4,
            start_date="2026-09-23",
            end_date="2026-09-23",
            timezone="Asia/Shanghai",
        )


def test_retry_uses_exponential_backoff():
    delays: list[float] = []

    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("offline", request=request)

    with pytest.raises(OpenMeteoTransportError):
        OpenMeteoClient(
            client=httpx.Client(transport=httpx.MockTransport(handler)),
            max_attempts=3,
            backoff_seconds=0.5,
            sleep=delays.append,
        ).geocode("Osaka", country_code="JP")
    assert delays == [0.5, 1.0]


def test_empty_geocoding_results_are_rejected():
    def handler(_: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"results": []})

    with pytest.raises(OpenMeteoResponseError, match="No geocoding result"):
        client_for(handler).geocode("Nowhere", country_code="CN")

