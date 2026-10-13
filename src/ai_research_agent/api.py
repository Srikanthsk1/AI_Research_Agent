import asyncio
import hmac
import os
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal
from uuid import UUID, uuid4

from fastapi import BackgroundTasks, Depends, FastAPI, Header, HTTPException, Request
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from loguru import logger
from pydantic import BaseModel, Field, field_validator

from ai_research_agent.graph.state import ResearchState
from ai_research_agent.planner.schemas import ResearchRequest

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load the workflow once and serialize use of local persistent Qdrant."""
    host = os.getenv("API_HOST", "127.0.0.1").lower()
    if (
        host not in {"127.0.0.1", "localhost", "::1"}
        and not os.getenv("API_KEY", "").strip()
    ):
        raise RuntimeError("Set API_KEY before binding the API to a non-local host.")

    from ai_research_agent.graph.workflow import graph

    app.state.workflow = graph
    app.state.research_lock = asyncio.Lock()
    # Job state is intentionally process-local; completed reports remain on disk.
    app.state.research_jobs = {}
    yield


app = FastAPI(
    title="AI Research Agent API",
    description="Generate cited research reports from a research question.",
    version="0.1.0",
    lifespan=lifespan,
)

# Allow a separately hosted web UI to call the API when explicitly configured.
# An empty list keeps browser cross-origin access disabled by default.
_cors_origins = [
    origin.strip()
    for origin in os.getenv("CORS_ORIGINS", "").split(",")
    if origin.strip()
]
if _cors_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=_cors_origins,
        allow_credentials=False,
        allow_methods=["GET", "POST"],
        allow_headers=["Authorization", "Content-Type"],
    )


class ResearchAPIRequest(ResearchRequest):
    query: str = Field(min_length=3, max_length=2000, description="Research question")

    @field_validator("query")
    @classmethod
    def normalize_query(cls, value: str) -> str:
        value = value.strip()
        if len(value) < 3:
            raise ValueError("Query must contain at least 3 non-whitespace characters.")
        return value


class ResearchAPIResponse(BaseModel):
    run_id: UUID
    query: str
    output_format: Literal["markdown", "json", "report"]
    report: str | dict[str, Any]
    pdf_url: str | None = None
    evidence_count: int


class ResearchJobAccepted(BaseModel):
    run_id: UUID
    status: Literal["queued"]
    status_url: str


class ResearchJobStatus(BaseModel):
    run_id: UUID
    query: str
    status: Literal["queued", "running", "completed", "failed"]
    submitted_at: datetime
    completed_at: datetime | None = None
    result: ResearchAPIResponse | None = None
    error: str | None = None


def _initial_state(
    run_id: UUID,
    query: str,
    options: dict[str, Any],
) -> ResearchState:
    return {
        "run_id": run_id.hex,
        "query": query,
        "request_options": options,
        "research_plan": None,
        "completed_tasks": [],
        "task_results": {},
        "metadata": {},
        "urls": [],
        "fresh_evidences": [],
        "evidences": [],
        "reasoning_output": "",
        "report": "",
        "pdf_path": "",
    }


async def _run_research(
    run_id: UUID,
    query: str,
    options: dict[str, Any],
) -> ResearchAPIResponse:
    """Run one workflow under the local persistent-store lock."""
    final_state = await app.state.workflow.ainvoke(
        _initial_state(run_id, query, options)
    )
    return ResearchAPIResponse(
        run_id=run_id,
        query=query,
        output_format=options["output_format"],
        report=final_state["report"],
        pdf_url=f"/research/{run_id}/report.pdf" if final_state.get("pdf_path") else None,
        evidence_count=len(final_state.get("evidences", [])),
    )


async def _run_research_job(
    run_id: UUID,
    query: str,
    options: dict[str, Any],
    pdf_url: str,
) -> None:
    """Execute a queued job and retain its outcome for polling clients."""
    job = app.state.research_jobs[run_id.hex]
    try:
        async with app.state.research_lock:
            job["status"] = "running"
            result = await _run_research(run_id, query, options)
        if result.pdf_url is not None:
            result.pdf_url = pdf_url
        job["result"] = result
        job["status"] = "completed"
    except Exception:
        logger.exception("Research job {} failed", run_id)
        job["error"] = "The research workflow failed. Check the server logs for details."
        job["status"] = "failed"
    finally:
        job["completed_at"] = datetime.now(timezone.utc)


async def _check_api_key(authorization: str | None = Header(default=None)) -> None:
    """Enforce bearer authentication when API_KEY is configured."""
    expected_key = os.getenv("API_KEY", "").strip()
    if not expected_key:
        return

    supplied_key = ""
    if authorization and authorization.lower().startswith("bearer "):
        supplied_key = authorization[7:].strip()

    if not hmac.compare_digest(
        supplied_key.encode("utf-8"),
        expected_key.encode("utf-8"),
    ):
        raise HTTPException(status_code=401, detail="Invalid or missing API key.")


@app.get("/healthz")
async def health_check() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/")
async def service_info() -> dict[str, str]:
    """Give API clients a small discovery response and links to the schema."""
    return {
        "name": "AI Research Agent API",
        "status": "ok",
        "docs_url": "/docs",
        "openapi_url": "/openapi.json",
        "research_endpoint": "/research",
    }


@app.post(
    "/research",
    response_model=ResearchAPIResponse,
    dependencies=[Depends(_check_api_key)],
)
async def create_research(
    request: ResearchAPIRequest,
    http_request: Request,
) -> ResearchAPIResponse:
    """Run the research workflow and return its report and PDF URL."""
    run_id = uuid4()
    try:
        async with app.state.research_lock:
            result = await _run_research(
                run_id,
                request.query,
                request.model_dump(exclude={"query"}),
            )
    except Exception as exc:
        logger.exception("Research workflow failed")
        raise HTTPException(
            status_code=500,
            detail="The research workflow failed. Check the server logs for details.",
        ) from exc

    if result.pdf_url is not None:
        result.pdf_url = str(
            http_request.url_for("download_report", run_id=str(run_id))
        )
    return result


@app.post(
    "/research/jobs",
    response_model=ResearchJobAccepted,
    status_code=202,
    dependencies=[Depends(_check_api_key)],
)
async def submit_research_job(
    request: ResearchAPIRequest,
    background_tasks: BackgroundTasks,
    http_request: Request,
) -> ResearchJobAccepted:
    """Queue a research run and return immediately with a polling URL."""
    run_id = uuid4()
    options = request.model_dump(exclude={"query"})
    app.state.research_jobs[run_id.hex] = {
        "run_id": run_id,
        "query": request.query,
        "status": "queued",
        "submitted_at": datetime.now(timezone.utc),
        "completed_at": None,
        "result": None,
        "error": None,
    }
    pdf_url = str(
        http_request.url_for("download_report", run_id=str(run_id))
    )
    background_tasks.add_task(
        _run_research_job,
        run_id,
        request.query,
        options,
        pdf_url,
    )
    return ResearchJobAccepted(
        run_id=run_id,
        status="queued",
        status_url=str(http_request.url_for("get_research_job", run_id=str(run_id))),
    )


@app.get(
    "/research/jobs/{run_id}",
    response_model=ResearchJobStatus,
    dependencies=[Depends(_check_api_key)],
)
async def get_research_job(run_id: UUID) -> ResearchJobStatus:
    """Return a queued job's state and its report when completed."""
    job = app.state.research_jobs.get(run_id.hex)
    if job is None:
        raise HTTPException(status_code=404, detail="Research job not found.")
    return ResearchJobStatus(**job)


@app.get(
    "/research/{run_id}/report.pdf",
    dependencies=[Depends(_check_api_key)],
)
async def download_report(run_id: UUID) -> FileResponse:
    """Download a PDF generated by a previous research request."""
    pdf_path = Path("reports") / f"{run_id.hex}.pdf"
    if not pdf_path.is_file():
        raise HTTPException(status_code=404, detail="Report PDF not found.")

    return FileResponse(
        path=pdf_path,
        media_type="application/pdf",
        filename=f"research-report-{run_id.hex}.pdf",
    )


def run() -> None:
    """Start the API server on localhost by default."""
    import uvicorn

    uvicorn.run(
        "ai_research_agent.api:app",
        host=os.getenv("API_HOST", "127.0.0.1"),
        port=int(os.getenv("API_PORT", "8000")),
    )
