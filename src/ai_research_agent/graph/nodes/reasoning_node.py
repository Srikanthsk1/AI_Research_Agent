from ai_research_agent.graph.state import (
    ResearchState,
)

from ai_research_agent.reasoning.service import (
    ReasoningService,
)


reasoning = ReasoningService()


async def reasoning_node(
    state: ResearchState,
) -> ResearchState:
    """Synthesize collected evidence and attach validated citations."""

    reasoning_output = await reasoning.analyze(
        query=state["query"],
        evidences=state["evidences"],
        include_citations=state.get("request_options", {}).get(
            "include_citations", True
        ),
    )

    state["reasoning_output"] = reasoning_output

    return state
