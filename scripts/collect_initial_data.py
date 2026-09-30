"""Collect the first small, seven-day dataset for all configured cities."""

from __future__ import annotations

import os
import time
from datetime import date
from pathlib import Path

from urban_environment.collectors.open_meteo import OpenMeteoClient
from urban_environment.processing.normalization import (
    air_quality_to_dataframe,
    merge_environment_data,
    weather_to_dataframe,
)
from urban_environment.quality.checks import check_dataframe
from urban_environment.utils.collection import (
    compact_hourly_sample,
    recent_complete_window,
    write_json,
)
from urban_environment.utils.config import load_cities


ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    cities = load_cities(ROOT / "config" / "cities.json")
    start_date, end_date = recent_complete_window()
    run_date = date.today().isoformat()
    results: list[dict[str, object]] = []

    with OpenMeteoClient(
        connect_timeout=float(os.getenv("OPEN_METEO_CONNECT_TIMEOUT", "5")),
        read_timeout=float(os.getenv("OPEN_METEO_READ_TIMEOUT", "20")),
        max_attempts=int(os.getenv("OPEN_METEO_MAX_ATTEMPTS", "3")),
    ) as client:
        for city in cities:
            started = time.perf_counter()
            result: dict[str, object] = {
                "city": city.name,
                "city_id": city.id,
                "start_date": start_date,
                "end_date": end_date,
                "weather_rows": 0,
                "air_quality_rows": 0,
                "merged_rows": 0,
                "status": "FAIL",
            }
            try:
                weather_payload = client.fetch_weather(
                    latitude=city.latitude,
                    longitude=city.longitude,
                    start_date=start_date,
                    end_date=end_date,
                    timezone=city.timezone,
                )
                raw_dir = ROOT / "data" / "raw" / run_date / city.id
                write_json(raw_dir / "weather.json", weather_payload)

                air_payload = client.fetch_air_quality(
                    latitude=city.latitude,
                    longitude=city.longitude,
                    start_date=start_date,
                    end_date=end_date,
                    timezone=city.timezone,
                )
                write_json(raw_dir / "air_quality.json", air_payload)

                weather = weather_to_dataframe(weather_payload, city.id)
                air = air_quality_to_dataframe(air_payload, city.id)
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
                result.update(
                    {
                        "weather_rows": len(weather),
                        "air_quality_rows": len(air),
                        "merged_rows": len(merged),
                        "weather_fields": weather.columns.tolist(),
                        "air_quality_fields": air.columns.tolist(),
                        "weather_quality": weather_quality.to_dict(),
                        "air_quality_check": air_quality.to_dict(),
                        "status": "PASS",
                    }
                )
                if city.id == "beijing":
                    write_json(
                        ROOT / "data" / "samples" / "weather_sample.json",
                        compact_hourly_sample(weather_payload),
                    )
                    write_json(
                        ROOT / "data" / "samples" / "air_quality_sample.json",
                        compact_hourly_sample(air_payload),
                    )
            except Exception as exc:  # Continue collecting other cities.
                result["error"] = f"{type(exc).__name__}: {exc}"
            result["elapsed_ms"] = round((time.perf_counter() - started) * 1000, 1)
            results.append(result)

    summary = {
        "run_date": run_date,
        "window": {"start_date": start_date, "end_date": end_date},
        "cities": results,
        "successful_cities": sum(item["status"] == "PASS" for item in results),
        "failed_cities": sum(item["status"] != "PASS" for item in results),
    }
    summary["result"] = "PASS" if summary["successful_cities"] == len(cities) else "WARN"
    write_json(ROOT / "output" / "evidence" / "collection_summary.json", summary)

    print("INITIAL_COLLECTION")
    print(f"WINDOW={start_date}..{end_date}")
    print("CITY | WEATHER_ROWS | AIR_QUALITY_ROWS | MERGED_ROWS | STATUS | ELAPSED_MS")
    for item in results:
        print(
            f"{item['city']} | {item['weather_rows']} | {item['air_quality_rows']} | "
            f"{item['merged_rows']} | {item['status']} | {item['elapsed_ms']}"
        )
    print(f"RESULT={summary['result']}")
    return 0 if summary["result"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
