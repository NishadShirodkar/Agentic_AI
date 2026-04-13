from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class JobStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class ResearchRequest(BaseModel):
    query: str = Field(..., min_length=3, max_length=1000)


class SourceEvidence(BaseModel):
    url: str
    snippet: str
    content: str = ""


class ExecutionPlan(BaseModel):
    steps: list[str] = Field(default_factory=list)
    tools: list[str] = Field(default_factory=list)


class ResearchResult(BaseModel):
    question: str
    short_answer: str
    key_findings: list[str]
    sources: list[SourceEvidence]
    confidence: str
    limitations: list[str]
    next_steps: list[str]


class JobRecord(BaseModel):
    id: str
    status: JobStatus
    query: str
    result: ResearchResult | None = None
    sources: list[SourceEvidence] = Field(default_factory=list)
    error: str | None = None
    created_at: datetime
    updated_at: datetime
    stage_timings: dict[str, float] = Field(default_factory=dict)
    failures: list[str] = Field(default_factory=list)


class CreateResearchResponse(BaseModel):
    job_id: str
    status: JobStatus


class JobResponse(BaseModel):
    id: str
    status: JobStatus
    query: str
    result: ResearchResult | None = None
    sources: list[SourceEvidence] = Field(default_factory=list)
    error: str | None = None
    created_at: datetime
    updated_at: datetime
    stage_timings: dict[str, float] = Field(default_factory=dict)
    failures: list[str] = Field(default_factory=list)

    @classmethod
    def from_job(cls, job: JobRecord) -> "JobResponse":
        data: dict[str, Any] = job.model_dump()
        return cls(**data)
