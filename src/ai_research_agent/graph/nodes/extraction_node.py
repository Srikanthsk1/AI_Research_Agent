import os

from ai_research_agent.graph.state import (
    ResearchState,
)

from ai_research_agent.research.extraction_service import (
    ExtractionService,
)


extraction = ExtractionService()


async def extraction_node(
    state: ResearchState,
) -> ResearchState:
    """Collect URLs and extract fresh evidence from search results."""

    urls, fresh_evidences = await extraction.extract(
        task_results=state["task_results"],
        max_urls=min(
            int(state.get("request_options", {}).get("max_sources", 10)),
            int(os.getenv("MAX_SEARCH_RESULTS", "10")),
        ),
        concurrency=int(os.getenv("MAX_PARALLEL_EXTRACTIONS", "5")),
    )

    state["urls"] = urls

    state["fresh_evidences"] = fresh_evidences

    state["evidences"] = fresh_evidences.copy()

    return state
