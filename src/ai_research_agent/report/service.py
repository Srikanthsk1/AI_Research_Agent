import json
import re

from ai_research_agent.llm.client import LLMClient
from pydantic import BaseModel

from ai_research_agent.report.prompt import REPORT_SYSTEM_PROMPT


class StructuredReport(BaseModel):
    title: str
    executive_summary: str
    key_findings: list[str]
    analysis: str
    conclusions: str
    limitations: str
    references: list[str]


class ReportService:
    """Generate the final report from research analysis."""

    def __init__(self):
        """Create the LLM client used for report generation."""
        self.llm = LLMClient()

    async def generate_report(
        self,
        query: str,
        reasoning_output: str,
        output_format: str = "report",
    ) -> str | dict:
        """Generate a full report, concise Markdown, or structured JSON."""
        if output_format == "json":
            system_prompt = """
You are a research analyst. Return only one valid JSON object with these keys:
title (string), executive_summary (string), key_findings (array of strings),
analysis (string), conclusions (string), limitations (string), and references
(array of strings). Use only the supplied reasoning. Preserve citation markers
and reference URLs exactly; never add sources or claims. If citations were not
provided, return an empty references array and do not invent citation markers.
"""
        elif output_format == "markdown":
            system_prompt = """
You are a research analyst. Write a concise Markdown answer with a title,
executive summary, key findings, conclusions, and limitations. Use only the
supplied reasoning. Preserve citation markers and URLs exactly when present;
never add sources or claims. Do not add a references section if none was supplied.
"""
        else:
            system_prompt = REPORT_SYSTEM_PROMPT

        user_prompt = f"""
Research Question:

{query}


Reasoning Output:

{reasoning_output}
"""

        report = await self.llm.generate(system_prompt=system_prompt, user_prompt=user_prompt)

        if output_format == "json":
            cleaned = re.sub(r"^\s*```(?:json)?\s*|\s*```\s*$", "", report, flags=re.IGNORECASE)
            parsed = json.loads(cleaned)
            if not isinstance(parsed, dict):
                raise ValueError("The model did not return a JSON object for the report.")
            return StructuredReport.model_validate(parsed).model_dump()

        return report
