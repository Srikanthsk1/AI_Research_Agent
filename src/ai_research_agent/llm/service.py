from ai_research_agent.llm.client import (
    LLMClient,
)

from ai_research_agent.report.prompt import (
    REPORT_SYSTEM_PROMPT,
)

from ai_research_agent.utils.logger import (
    logger,
)


class ReportService:
    """Legacy report-generation service retained for compatibility."""

    def __init__(self):
        """Create the LLM client used by this service."""
        self.client = LLMClient()

    async def generate_report(
        self,
        query: str,
        reasoning_output: str,
    ) -> str:
        """Generate a report from a query and reasoning output."""
        """Generate a report from a query and reasoning output."""
        logger.info("Generating research report...")

        user_prompt = f"""
User Query:

{query}

Reasoning Output:

{reasoning_output}


"""

        report = await self.client.generate(
            system_prompt=REPORT_SYSTEM_PROMPT,
            user_prompt=user_prompt,
        )

        logger.success("Research report generated.")

        return report
