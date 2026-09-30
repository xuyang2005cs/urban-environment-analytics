"""Run a small real-network probe against all three Open-Meteo APIs."""

from __future__ import annotations

import os
import time
from pathlib import Path

from urban_environment.collectors.open_meteo import OpenMeteoClient
from urban_environment.processing.normalization import (
    air_quality_to_dataframe,
    merge_environment_data,
    weather_to_dataframe,
)
from urban_environment.quality.checks import check_dataframe
from urban_environment.utils.collection import recent_complete_window, write_json


ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    start_date, end_date = recent_complete_window()
    started = time.perf_counter()
    summary: dict[str, object] = {
        "city": "Beijing",
        "window": {"start_date": start_date, "end_date": end_date},
        "geo": "FAIL",
        "weather": "FAIL",
        "air_quality": "FAIL",
        "result": "FAIL",
    }
    try:
        with OpenMeteoClient(
            connect_timeout=float(os.getenv("OPEN_METEO_CONNECT_TIMEOUT", "5")),
            read_timeout=float(os.getenv("OPEN_METEO_READ_TIMEOUT", "20")),
            max_attempts=int(os.getenv("OPEN_METEO_MAX_ATTEMPTS", "3")),
        ) as client:
            location = client.geocode("Beijing", country_code="CN")
            summary["geo"] = "PASS"
            summary["timezone"] = location["timezone"]
            weather_payload = client.fetch_weather(
                latitude=location["latitude"],
                longitude=location["longitude"],
                start_date=start_date,
                end_date=end_date,
                timezone=location["timezone"],
            )
            summary["weather"] = "PASS"
            air_payload = client.fetch_air_quality(
                latitude=location["latitude"],
                longitude=location["longitude"],
                start_date=start_date,
                end_date=end_date,
                timezone=location["timezone"],
            )
            summary["air_quality"] = "PASS"

        weather = weather_to_dataframe(weather_payload, "beijing")
        air = air_quality_to_dataframe(air_payload, "beijing")
        merged = merge_environment_data(weather, air)
        weather_quality = check_dataframe(
            weather,
            required_columns=set(weather.columns),
            numeric_columns=set(weather.columns) - {"city", "timestamp"},
        )
        air_quality = check_dataframe(
            air,
            required_columns=set(air.columns),
            numeric_columns=set(air.columns) - {"city", "timestamp"},
        )
        summary.update(
            {
                "weather_rows": len(weather),
                "air_quality_rows": len(air),
                "merged_rows": len(merged),
                "weather_columns": weather.columns.tolist(),
                "air_quality_columns": air.columns.tolist(),
                "weather_quality": weather_quality.to_dict(),
                "air_quality_check": air_quality.to_dict(),
                "elapsed_ms": round((time.perf_counter() - started) * 1000, 1),
                "result": "PASS",
            }
        )
    except Exception as exc:  # CLI boundary: preserve a useful summary on failure.
        summary["error"] = f"{type(exc).__name__}: {exc}"
        summary["elapsed_ms"] = round((time.perf_counter() - started) * 1000, 1)

    write_json(ROOT / "output" / "evidence" / "probe_summary.json", summary)
    print("OPEN_METEO_PROBE")
    for key in (
        "city",
        "geo",
        "weather",
        "air_quality",
        "weather_rows",
        "air_quality_rows",
        "merged_rows",
        "timezone",
        "elapsed_ms",
        "result",
        "error",
    ):
        if key in summary:
            print(f"{key.upper()}={summary[key]}")
    return 0 if summary["result"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())

