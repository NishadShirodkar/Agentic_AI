import sys
import time
from pathlib import Path

from fastapi.testclient import TestClient

# Ensure imports work whether tests are run from repo root or backend/.
BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app import app  # noqa: E402
from services.job_manager import JobManager, job_manager  # noqa: E402


client = TestClient(app)


def test_job_creation_unit() -> None:
    manager = JobManager()

    job = manager.create_job("test research query")

    assert job.id
    assert job.status == "pending"
    assert job.query == "test research query"
    assert manager.get_job(job.id) is not None


def test_post_research_creates_job() -> None:
    response = client.post("/research", json={"query": "Compare vector databases for RAG"})

    assert response.status_code == 200

    payload = response.json()
    assert "job_id" in payload
    assert payload["status"] == "pending"

    created_job = job_manager.get_job(payload["job_id"])
    assert created_job is not None
    assert created_job.query == "Compare vector databases for RAG"


def test_get_research_job_returns_state() -> None:
    create_response = client.post("/research", json={"query": "Compare Milvus and Qdrant"})
    job_id = create_response.json()["job_id"]

    response = client.get(f"/research/{job_id}")
    assert response.status_code == 200

    payload = response.json()
    assert payload["id"] == job_id
    assert payload["query"] == "Compare Milvus and Qdrant"
    assert payload["status"] in {"pending", "running", "completed", "failed"}
    assert "sources" in payload
    assert "stage_timings" in payload


def test_end_to_end_post_wait_get() -> None:
    create_response = client.post("/research", json={"query": "Compare top 3 open-source vector databases"})
    job_id = create_response.json()["job_id"]

    terminal_payload = None
    deadline = time.time() + 25

    while time.time() < deadline:
        response = client.get(f"/research/{job_id}")
        assert response.status_code == 200
        payload = response.json()

        if payload["status"] in {"completed", "failed"}:
            terminal_payload = payload
            break

        time.sleep(0.4)

    assert terminal_payload is not None, "Job did not reach a terminal state in time"

    if terminal_payload["status"] == "completed":
        result = terminal_payload["result"]
        assert result is not None
        assert set(result.keys()) == {
            "question",
            "short_answer",
            "key_findings",
            "sources",
            "confidence",
            "limitations",
            "next_steps",
        }

        for source in result["sources"]:
            assert "url" in source
            assert "snippet" in source
    else:
        assert terminal_payload["error"] is not None
