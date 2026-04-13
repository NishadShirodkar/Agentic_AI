# Research Agent V2 - Design Document

## 1. Overview

Research Agent V2 is a job-based backend service for source-grounded research queries.

- Client submits a query via `POST /research`
- Service creates a job and runs a multi-stage pipeline asynchronously
- Client polls `GET /research/{job_id}` for status and final output

Why agentic:

- The problem is multi-step by nature (plan -> collect evidence -> synthesize)
- Splitting into stages improves control, debuggability, and failure isolation
- Output quality is better when synthesis is grounded on retrieved evidence rather than a single direct model call

---

## 2. Architecture

High-level flow:

1. Create job (`pending`)
2. Run pipeline in background (`running`)
3. Persist stage outputs (plan, sources, result/errors)
4. Return terminal state (`completed` or `failed`)

Components:

- Planner
  - Produces execution plan (`steps`, `tools`)
  - Plan directly affects executor behavior
- Executor
  - Runs search, scraping, filtering
  - Produces normalized source list
- Synthesizer
  - Produces structured JSON answer
  - Validates citations against retrieved sources
- Job Manager
  - Thread-safe in-memory job store
  - Tracks status, timestamps, result, sources, stage timings, failures

---

## 3. API Design

### POST /research

- Input: query string
- Behavior:
  - validate request
  - create job id
  - enqueue background pipeline execution
- Output:
  - `job_id`
  - initial status (`pending`)

### GET /research/{job_id}

- Returns full job state:
  - status
  - result (when available)
  - sources
  - error
  - timings/failures metadata

### Job states

- `pending` -> `running` -> `completed` or `failed`

---

## 4. Data Model

### Job schema (core fields)

- `id: string`
- `status: pending | running | completed | failed`
- `query: string`
- `result: object | null`
- `sources: list`
- `error: string | null`
- `created_at: timestamp`
- `updated_at: timestamp`

Operational metadata:

- `stage_timings: {stage: duration}`
- `failures: list[string]`

### Source structure

- `url`
- `snippet`
- `content`

### Result format

- `question`
- `short_answer`
- `key_findings`
- `sources`
- `confidence`
- `limitations`
- `next_steps`

---

## 5. Key Design Decisions

- Job-based system
  - Avoids request timeouts for long-running research tasks
  - Enables polling and explicit lifecycle management
- FastAPI
  - Strong request/response validation with Pydantic
  - Good ergonomics for API-first services
- BackgroundTasks over Celery
  - Minimal operational overhead
  - Appropriate for a take-home/single-instance scope
- In-memory store
  - Fast to implement and easy to reason about
  - Acceptable for demo scope; intentionally not durable

---

## 6. Reliability & Failure Handling

- Timeouts
  - External calls use bounded timeout windows
- Partial failures
  - One bad source does not fail the whole job
  - Executor continues processing remaining sources
- Error propagation
  - Stage exceptions are captured and surfaced in job state
  - Job transitions to `failed` with descriptive error

---

## 7. Citation Integrity

How enforced:

- Synthesizer output sources are validated against executor-collected source URLs
- Any citation not in retrieved sources is dropped/replaced

Why it matters:

- Prevents fabricated citations
- Keeps the final answer traceable to actual retrieved evidence

---

## 8. Observability

- Logging
  - Stage-level logs include `job_id` and stage transitions
- Stage timings
  - Per-stage duration recorded for performance visibility
- Failure tracking
  - Errors and stage failures stored in job metadata for debugging

---

## 9. Testing Strategy

- Unit tests
  - Core job manager behavior (creation/state)
- API integration tests
  - Endpoint contracts for POST and GET
- End-to-end test
  - Full lifecycle: create job -> poll -> terminal state validation

---

## 10. Tradeoffs & Limitations

- In-memory storage
  - No persistence across restarts
  - Not suitable for horizontal scaling
- External API dependency
  - Quality/latency/reliability tied to providers
  - Quota/rate limits can affect completion
- No distributed queue
  - BackgroundTasks works per-process only
  - Limited concurrency control and retry semantics

---

## 11. Future Improvements

- Persistent data layer
  - Move jobs/sources/results to Postgres (or equivalent)
- Queue/workers
  - Replace BackgroundTasks with Celery/RQ + Redis
- Caching
  - Cache search/scrape/model outputs for repeated queries
- Multi-provider model support
  - Provider abstraction for failover and cost/performance routing
