"""Configuration loading helpers."""

import json
from pathlib import Path

from pydantic import TypeAdapter

from urban_environment.models.city import City


def load_cities(path: Path) -> list[City]:
    """Load and validate the city configuration JSON file."""

    payload = json.loads(path.read_text(encoding="utf-8"))
    return TypeAdapter(list[City]).validate_python(payload)

