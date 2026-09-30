from pathlib import Path

from fastapi.testclient import TestClient

from urban_environment.models.city import City
from urban_environment.pipeline import DataPipeline
from urban_environment.web.app import create_app
from tests.test_pipeline import FakeClient


def api_client(tmp_path, beijing, weather_payload, air_payload):
    tokyo = City(
        id="tokyo",
        name="东京",
        query_name="Tokyo",
        country="日本",
        country_code="JP",
        latitude=35.6895,
        longitude=139.69171,
        timezone="Asia/Tokyo",
    )
    cities = [beijing, tokyo]
    pipeline = DataPipeline(
        root=tmp_path,
        cities=cities,
        client_factory=lambda: FakeClient(weather_payload, air_payload),
    )
    pipeline.run(start_date="2026-09-23", end_date="2026-09-23")
    config = tmp_path / "cities.json"
    config.write_text(
        """[
          {"id":"beijing","name":"北京","query_name":"Beijing","country":"中国","country_code":"CN","latitude":39.9075,"longitude":116.39723,"timezone":"Asia/Shanghai"},
          {"id":"tokyo","name":"东京","query_name":"Tokyo","country":"日本","country_code":"JP","latitude":35.6895,"longitude":139.69171,"timezone":"Asia/Tokyo"}
        ]""",
        encoding="utf-8",
    )
    app = create_app(
        database_path=tmp_path / "data/analytics/environment.duckdb",
        cities_path=config,
        frontend_dir=tmp_path / "frontend",
    )
    return TestClient(app)


def test_health_endpoint(tmp_path, beijing, weather_payload, air_payload):
    assert api_client(tmp_path, beijing, weather_payload, air_payload).get("/api/health").json() == {"status": "ok"}


def test_cities_metadata(tmp_path, beijing, weather_payload, air_payload):
    response = api_client(tmp_path, beijing, weather_payload, air_payload).get("/api/meta/cities")
    assert response.status_code == 200
    assert [city["id"] for city in response.json()] == ["beijing", "tokyo"]


def test_overview_uses_real_latest_observation(tmp_path, beijing, weather_payload, air_payload):
    response = api_client(tmp_path, beijing, weather_payload, air_payload).get("/api/overview?city=beijing")
    assert response.status_code == 200
    body = response.json()
    assert body["selected"]["observation"]["temperature"] == 21.0
    assert body["selected"]["observation"]["weather_code"] == 2
    assert len(body["cities"]) == 2


def test_overview_rejects_unknown_city(tmp_path, beijing, weather_payload, air_payload):
    response = api_client(tmp_path, beijing, weather_payload, air_payload).get("/api/overview?city=missing")
    assert response.status_code == 404


def test_city_summary(tmp_path, beijing, weather_payload, air_payload):
    response = api_client(tmp_path, beijing, weather_payload, air_payload).get("/api/cities/beijing/summary")
    assert response.status_code == 200
    assert response.json()["rows"] == 2
    assert response.json()["totals"]["precipitation"] == 0.1


def test_city_series_rejects_inverted_range(tmp_path, beijing, weather_payload, air_payload):
    response = api_client(tmp_path, beijing, weather_payload, air_payload).get(
        "/api/cities/beijing/weather-series?start=2026-09-24&end=2026-09-23"
    )
    assert response.status_code == 422


def test_weather_series(tmp_path, beijing, weather_payload, air_payload):
    response = api_client(tmp_path, beijing, weather_payload, air_payload).get("/api/cities/tokyo/weather-series")
    assert response.status_code == 200
    assert response.json()["points"][0]["values"]["weather_code"] == 1.0


def test_air_quality_series(tmp_path, beijing, weather_payload, air_payload):
    response = api_client(tmp_path, beijing, weather_payload, air_payload).get("/api/cities/beijing/air-quality-series")
    assert response.status_code == 200
    assert response.json()["points"][1]["values"]["pm2_5"] == 11.0


def test_comparison_returns_selected_metric(tmp_path, beijing, weather_payload, air_payload):
    response = api_client(tmp_path, beijing, weather_payload, air_payload).get("/api/comparison?metric=temperature")
    assert response.status_code == 200
    assert response.json()["metric"] == "temperature"
    assert len(response.json()["items"]) == 2


def test_comparison_rejects_unsupported_metric(tmp_path, beijing, weather_payload, air_payload):
    response = api_client(tmp_path, beijing, weather_payload, air_payload).get("/api/comparison?metric=unknown")
    assert response.status_code == 422


def test_quality_endpoints(tmp_path, beijing, weather_payload, air_payload):
    client = api_client(tmp_path, beijing, weather_payload, air_payload)
    summary = client.get("/api/quality/summary")
    runs = client.get("/api/quality/runs")
    assert summary.status_code == 200
    assert summary.json()["status"] == "PASS"
    assert len(runs.json()) == 4


def test_pipeline_endpoints(tmp_path, beijing, weather_payload, air_payload):
    client = api_client(tmp_path, beijing, weather_payload, air_payload)
    assert len(client.get("/api/pipeline/runs").json()) == 4
    assert len(client.get("/api/pipeline/watermarks").json()) == 4


def test_analysis_endpoints(tmp_path, beijing, weather_payload, air_payload):
    client = api_client(tmp_path, beijing, weather_payload, air_payload)
    assert client.get("/api/anomalies?city=beijing").status_code == 200
    correlations = client.get("/api/correlation?city=beijing")
    assert correlations.status_code == 200
    assert len(correlations.json()) == 4


def test_missing_database_returns_service_unavailable(tmp_path):
    config = Path(__file__).resolve().parents[1] / "config/cities.json"
    app = create_app(database_path=tmp_path / "missing.duckdb", cities_path=config, frontend_dir=tmp_path)
    response = TestClient(app).get("/api/overview")
    assert response.status_code == 503
