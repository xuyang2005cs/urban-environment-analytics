import pytest

from urban_environment.scheduler import PipelineLock, PipelineLockedError, build_scheduler


def test_pipeline_lock_creates_and_removes_file(tmp_path):
    path = tmp_path / "pipeline.lock"
    with PipelineLock(path):
        assert path.exists()
    assert not path.exists()


def test_pipeline_lock_rejects_second_owner(tmp_path):
    path = tmp_path / "pipeline.lock"
    with PipelineLock(path):
        with pytest.raises(PipelineLockedError):
            with PipelineLock(path):
                pass


def test_scheduler_has_hourly_incremental_job(tmp_path):
    scheduler = build_scheduler(tmp_path)
    job = scheduler.get_job("incremental-environment-sync")
    assert job is not None
    assert str(job.trigger) == "interval[1:00:00]"


def test_scheduler_prevents_overlapping_instances(tmp_path):
    scheduler = build_scheduler(tmp_path)
    job = scheduler.get_job("incremental-environment-sync")
    assert job.max_instances == 1
    assert job.coalesce is True

