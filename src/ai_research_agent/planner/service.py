from ai_research_agent.planner.schemas import (
    ResearchRequest,
    ResearchPlan,
    ResearchTask,
)

from ai_research_agent.planner.prompt import (
    PLANNER_SYSTEM_PROMPT,
)

from ai_research_agent.planner.client import generate

from ai_research_agent.planner.validator import (
    validate_research_plan,
)


class PlannerService:
    """Generate and validate structured research plans."""

    @staticmethod
    async def create_plan(
        request: ResearchRequest,
    ) -> ResearchPlan:
        """Ask the configured model for a plan and validate its schema."""

        messages = [
            {
                "role": "system",
                "content": PLANNER_SYSTEM_PROMPT,
            },
            {
                "role": "user",
                "content": request.model_dump_json(indent=2),
            },
        ]

        raw_response = await generate(messages)

        validated_plan = validate_research_plan(raw_response)

        return validated_plan
