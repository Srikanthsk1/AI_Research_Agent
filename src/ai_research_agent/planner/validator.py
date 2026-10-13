import re
from typing import Union

from json_repair import repair_json
from pydantic import ValidationError

from ai_research_agent.planner.schemas import ResearchPlan


class PlannerValidationError(Exception):
    """Raised when a generated plan cannot be validated."""

    pass


def clean_llm_output(text: str) -> str:
    """Remove Markdown fences and surrounding whitespace from output."""

    text = text.strip()

    # Remove ```json
    text = re.sub(r"^```(?:json)?", "", text, flags=re.IGNORECASE)

    # Remove ending ```
    text = re.sub(r"```$", "", text)

    return text.strip()


def validate_research_plan(planner_output: Union[str, dict]) -> ResearchPlan:
    """Repair and validate model output as a research plan."""

    try:

        # Already parsed
        if isinstance(planner_output, dict):
            return ResearchPlan.model_validate(planner_output)

        # Clean markdown formatting
        planner_output = clean_llm_output(planner_output)

        # Repair malformed JSON
        repaired = repair_json(planner_output)

        # Validate against Pydantic model
        plan = ResearchPlan.model_validate_json(repaired)

        return plan

    except ValidationError as e:
        raise PlannerValidationError(f"Pydantic validation failed:\n{e}")

    except Exception as e:
        raise PlannerValidationError(f"Planner output validation failed:\n{e}")
