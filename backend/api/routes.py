from time import perf_counter

from fastapi import APIRouter, BackgroundTasks, HTTPException

from core.executor import execute_plan
from core.planner import create_plan
from core.synthesizer import synthesize
from models.schemas import CreateResearchResponse, JobResponse, JobStatus, ResearchRequest
from services.job_manager import job_manager
from utils.logging import log_stage

router = APIRouter()


def run_research_job(job_id: str) -> None:
    job = job_manager.get_job(job_id)
    if not job:
        return

    try:
        job_manager.set_status(job_id, JobStatus.RUNNING)

        log_stage(job_id, "planner", "started")
        planner_start = perf_counter()
        plan = create_plan(job.query)
        job_manager.set_stage_timing(job_id, "planner", perf_counter() - planner_start)
        log_stage(job_id, "planner", "completed")

        log_stage(job_id, "executor", "started")
        executor_start = perf_counter()
        sources = execute_plan(plan, job.query)
        job_manager.set_sources(job_id, sources)
        job_manager.set_stage_timing(job_id, "executor", perf_counter() - executor_start)
        log_stage(job_id, "executor", "completed")

        log_stage(job_id, "synthesizer", "started")
        synth_start = perf_counter()
        result = synthesize(job.query, sources)
        job_manager.set_stage_timing(job_id, "synthesizer", perf_counter() - synth_start)
        log_stage(job_id, "synthesizer", "completed")

        job_manager.set_result(job_id, result)
    except Exception as exc:
        message = f"Pipeline failed: {exc}"
        job_manager.set_error(job_id, message)


@router.post("/research", response_model=CreateResearchResponse)
def create_research_job(payload: ResearchRequest, background_tasks: BackgroundTasks) -> CreateResearchResponse:
    job = job_manager.create_job(payload.query)
    background_tasks.add_task(run_research_job, job.id)
    return CreateResearchResponse(job_id=job.id, status=job.status)


@router.get("/research/{job_id}", response_model=JobResponse)
def get_research_job(job_id: str) -> JobResponse:
    job = job_manager.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return JobResponse.from_job(job)
