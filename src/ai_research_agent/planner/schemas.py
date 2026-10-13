from typing import List, Literal
from pydantic import BaseModel, Field, field_validator


class ResearchRequest(BaseModel):
    """Validated user request used to generate a research plan."""

    query: str = Field(..., description="The user's research request.")

    research_depth: Literal["basic", "intermediate", "deep"] = Field(
        default="deep", description="Level of research required."
    )

    output_format: Literal["markdown", "json", "report"] = Field(
        default="report", description="Desired output format."
    )

    max_sources: int = Field(
        default=10, ge=1, le=100, description="Maximum number of sources to collect."
    )

    include_citations: bool = Field(
        default=True, description="Whether citations should be included."
    )


class TavilySearchArguments(BaseModel):
    """Validated arguments for the only tool exposed to generated plans."""

    query: str = Field(min_length=1, max_length=500)
    max_results: int = Field(default=5, ge=1, le=20)


class ResearchTask(BaseModel):
    """One search or research action produced by the planner."""

    task_id: int

    title: str

    description: str

    task_type: Literal[
        "search",
        "crawl",
        "extract",
        "summarize",
        "compare",
        "verify",
        "reason",
        "report",
        "memory",
    ]

    tool_name: Literal["tavily_search"] = Field(
        description="The allowlisted MCP tool to execute."
    )

    tool_arguments: TavilySearchArguments = Field(
        description="Validated arguments passed to Tavily search."
    )

    priority: int = Field(default=1, ge=1, le=5)

    @field_validator("priority", mode="before")
    @classmethod
    def clamp_priority(cls, value: object) -> object:
        """Keep model-generated priorities within the supported 1–5 range."""
        if isinstance(value, int) and not isinstance(value, bool):
            return min(5, max(1, value))
        return value

    depends_on: List[int] = Field(default_factory=list)

    expected_output: str


class ResearchPlan(BaseModel):
    """Validated collection of tasks for a research request."""

    objective: str

    research_scope: str

    estimated_steps: int

    tasks: List[ResearchTask]

    final_output_format: Literal["markdown", "json", "report"] = "report"
