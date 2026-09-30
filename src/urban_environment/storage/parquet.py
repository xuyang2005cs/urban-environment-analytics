"""Idempotent, partitioned Parquet clean layer."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd


@dataclass(frozen=True)
class WriteResult:
    fetched: int
    inserted: int
    skipped: int
    files: tuple[Path, ...]


class ParquetStore:
    """Store clean records partitioned by dataset, city, year and month."""

    def __init__(self, root: Path) -> None:
        self.root = root

    def dataset_files(self, dataset: str) -> list[Path]:
        return sorted((self.root / dataset).glob("city=*/year=*/month=*/data.parquet"))

    def read_dataset(self, dataset: str) -> pd.DataFrame:
        files = self.dataset_files(dataset)
        if not files:
            return pd.DataFrame()
        return pd.concat((pd.read_parquet(path) for path in files), ignore_index=True)

    def write_incremental(self, dataset: str, frame: pd.DataFrame) -> WriteResult:
        """Upsert by city/timestamp and atomically replace touched partitions."""

        if frame.empty:
            return WriteResult(0, 0, 0, ())
        required = {"city", "timestamp"}
        missing = required.difference(frame.columns)
        if missing:
            raise ValueError(f"clean frame missing keys: {', '.join(sorted(missing))}")

        incoming = frame.copy()
        incoming["timestamp"] = pd.to_datetime(incoming["timestamp"], utc=True)
        incoming["year"] = incoming["timestamp"].dt.year
        incoming["month"] = incoming["timestamp"].dt.month
        inserted = 0
        skipped = 0
        written: list[Path] = []

        for (city, year, month), partition in incoming.groupby(
            ["city", "year", "month"], sort=True, dropna=False
        ):
            path = (
                self.root
                / dataset
                / f"city={city}"
                / f"year={int(year):04d}"
                / f"month={int(month):02d}"
                / "data.parquet"
            )
            path.parent.mkdir(parents=True, exist_ok=True)
            clean_partition = partition.drop(columns=["year", "month"])
            existing = pd.read_parquet(path) if path.exists() else pd.DataFrame()
            existing_keys = (
                set(zip(existing["city"], pd.to_datetime(existing["timestamp"], utc=True)))
                if not existing.empty
                else set()
            )
            incoming_keys = list(
                zip(clean_partition["city"], pd.to_datetime(clean_partition["timestamp"], utc=True))
            )
            new_mask = [key not in existing_keys for key in incoming_keys]
            inserted += sum(new_mask)
            skipped += len(new_mask) - sum(new_mask)

            combined = pd.concat([existing, clean_partition], ignore_index=True)
            combined["timestamp"] = pd.to_datetime(combined["timestamp"], utc=True)
            combined = (
                combined.sort_values(["city", "timestamp", "ingested_at"])
                .drop_duplicates(["city", "timestamp"], keep="last")
                .reset_index(drop=True)
            )
            temporary = path.with_suffix(".parquet.tmp")
            combined.to_parquet(temporary, index=False, engine="pyarrow")
            temporary.replace(path)
            written.append(path)

        return WriteResult(len(frame), inserted, skipped, tuple(written))

