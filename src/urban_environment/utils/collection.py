"""Shared helpers for live collection entry points."""

from __future__ import annotations

import json
from datetime import date, timedelta
from pathlib import Path
from typing import Any


def recent_complete_window(days: int = 7) -> tuple[str, str]:
    """Return an inclusive window ending yesterday."""

    end = date.today() - timedelta(days=1)
    start = end - timedelta(days=days - 1)
    return start.isoformat(), end.isoformat()


def write_json(path: Path, payload: object) -> None:
    """Write readable UTF-8 JSON, creating parent directories."""

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def compact_hourly_sample(payload: dict[str, Any], rows: int = 3) -> dict[str, Any]:
    """Create a small, truthful sample by truncating every hourly array."""

    sample = {key: value for key, value in payload.items() if key != "hourly"}
    hourly = payload.get("hourly", {})
    sample["hourly"] = {
        key: value[:rows] if isinstance(value, list) else value for key, value in hourly.items()
    }
    sample["sample_note"] = (
        f"First {rows} hourly records retained from a live Open-Meteo response."
    )
    return sample

