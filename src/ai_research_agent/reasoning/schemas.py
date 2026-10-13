from pydantic import BaseModel


class ReasoningResult(BaseModel):
    """Structured form of a research analysis."""

    summary: str

    key_findings: list[str]

    conclusions: str

    limitations: str
