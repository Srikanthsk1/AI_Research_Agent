from ai_research_agent.planner.schemas import (
    ResearchRequest,
)

from ai_research_agent.planner.service import (
    PlannerService,
)

from ai_research_agent.graph.state import (
    ResearchState,
)


planner = PlannerService()


async def planner_node(
    state: ResearchState,
) -> ResearchState:
    """Create a validated research plan from the user's query."""

    request = ResearchRequest(
        query=state["query"],
        **state.get("request_options", {}),
    )

    plan = await planner.create_plan(request)

    state["research_plan"] = plan

    return state
