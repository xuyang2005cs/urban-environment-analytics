"""Hourly APScheduler service with a simple cross-process lock."""

from __future__ import annotations

import os
from contextlib import AbstractContextManager
from pathlib import Path

from apscheduler.schedulers.blocking import BlockingScheduler

from urban_environment.pipeline import DataPipeline


class PipelineLockedError(RuntimeError):
    """Raised when another process already owns the pipeline lock."""


class PipelineLock(AbstractContextManager["PipelineLock"]):
    def __init__(self, path: Path) -> None:
        self.path = path
        self._descriptor: int | None = None

    def __enter__(self) -> "PipelineLock":
        self.path.parent.mkdir(parents=True, exist_ok=True)
        try:
            self._descriptor = os.open(
                self.path, os.O_CREAT | os.O_EXCL | os.O_WRONLY
            )
            os.write(self._descriptor, str(os.getpid()).encode("ascii"))
        except FileExistsError as exc:
            raise PipelineLockedError(f"pipeline lock already exists: {self.path}") from exc
        return self

    def __exit__(self, *_: object) -> None:
        if self._descriptor is not None:
            os.close(self._descriptor)
            self._descriptor = None
        self.path.unlink(missing_ok=True)


def execute_scheduled_pipeline(root: Path) -> None:
    """Run one incremental sync if the lock can be acquired."""

    with PipelineLock(root / "data" / "locks" / "pipeline.lock"):
        DataPipeline(root=root).run()


def build_scheduler(root: Path) -> BlockingScheduler:
    scheduler = BlockingScheduler(timezone="UTC")
    scheduler.add_job(
        execute_scheduled_pipeline,
        "interval",
        hours=1,
        args=[root],
        id="incremental-environment-sync",
        max_instances=1,
        coalesce=True,
        replace_existing=True,
    )
    return scheduler


def run_scheduler(root: Path) -> None:
    """Start the foreground scheduler; never called implicitly by imports."""

    scheduler = build_scheduler(root)
    print("SCHEDULER=STARTED INTERVAL=1h TIMEZONE=UTC")
    scheduler.start()
