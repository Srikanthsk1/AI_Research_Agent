from typing import Any

from typing_extensions import TypedDict

from ai_research_agent.planner.schemas import (
    ResearchPlan,
)

from ai_research_agent.research.evidence import (
    Evidence,
)


class ResearchState(TypedDict):
    """
    Shared state for the LangGraph workflow.

    Every node reads the fields it needs and
    writes only the fields it produces.
    """

    # --------------------------------------------------
    # User Input
    # --------------------------------------------------

    run_id: str

    query: str

    request_options: dict[str, Any]

    # --------------------------------------------------
    # Planner Output
    # --------------------------------------------------

    research_plan: ResearchPlan | None

    # --------------------------------------------------
    # Executor Output
    # --------------------------------------------------

    completed_tasks: list[int]

    task_results: dict[int, Any]

    metadata: dict[str, Any]

    # --------------------------------------------------
    # Extraction Output
    # --------------------------------------------------

    urls: list[str]

    fresh_evidences: list[Evidence]

    # --------------------------------------------------
    # Memory Output
    # --------------------------------------------------

    evidences: list[Evidence]

    # --------------------------------------------------
    # Reasoning Output
    # --------------------------------------------------

    reasoning_output: str

    # --------------------------------------------------
    # Report Output
    # --------------------------------------------------

    report: Any

    # --------------------------------------------------
    # PDF Output
    # --------------------------------------------------

    pdf_path: str
