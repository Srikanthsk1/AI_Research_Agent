from ai_research_agent.graph.state import (
    ResearchState,
)

from ai_research_agent.memory.retrieval_service import (
    MemoryRetrievalService,
)


memory = MemoryRetrievalService()


def memory_node(
    state: ResearchState,
) -> ResearchState:
    """Append relevant historical evidence without duplicating fresh URLs."""

    previous_evidences = memory.retrieve(
        query=state["query"],
    )

    fresh_urls = {evidence.source_url for evidence in state["fresh_evidences"]}
    state["evidences"].extend(
        evidence
        for evidence in previous_evidences
        if evidence.source_url not in fresh_urls
    )

    return state
