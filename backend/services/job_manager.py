from datetime import datetime, timezone
from threading import Lock
from uuid import uuid4

from models.schemas import JobRecord, JobStatus, ResearchResult, SourceEvidence


class JobManager:
    def __init__(self) -> None:
        self._jobs: dict[str, JobRecord] = {}
        self._lock = Lock()

    def create_job(self, query: str) -> JobRecord:
        now = datetime.now(timezone.utc)
        job = JobRecord(
            id=str(uuid4()),
            status=JobStatus.PENDING,
            query=query,
            created_at=now,
            updated_at=now,
        )
        with self._lock:
            self._jobs[job.id] = job
        return job

    def get_job(self, job_id: str) -> JobRecord | None:
        with self._lock:
            return self._jobs.get(job_id)

    def set_status(self, job_id: str, status: JobStatus) -> None:
        with self._lock:
            job = self._jobs[job_id]
            job.status = status
            job.updated_at = datetime.now(timezone.utc)

    def set_sources(self, job_id: str, sources: list[SourceEvidence]) -> None:
        with self._lock:
            job = self._jobs[job_id]
            job.sources = sources
            job.updated_at = datetime.now(timezone.utc)

    def set_result(self, job_id: str, result: ResearchResult) -> None:
        with self._lock:
            job = self._jobs[job_id]
            job.result = result
            job.status = JobStatus.COMPLETED
            job.updated_at = datetime.now(timezone.utc)

    def set_error(self, job_id: str, error: str) -> None:
        with self._lock:
            job = self._jobs[job_id]
            job.error = error
            job.status = JobStatus.FAILED
            job.failures.append(error)
            job.updated_at = datetime.now(timezone.utc)

    def add_failure(self, job_id: str, failure: str) -> None:
        with self._lock:
            job = self._jobs[job_id]
            job.failures.append(failure)
            job.updated_at = datetime.now(timezone.utc)

    def set_stage_timing(self, job_id: str, stage: str, duration_seconds: float) -> None:
        with self._lock:
            job = self._jobs[job_id]
            job.stage_timings[stage] = round(duration_seconds, 4)
            job.updated_at = datetime.now(timezone.utc)


job_manager = JobManager()
