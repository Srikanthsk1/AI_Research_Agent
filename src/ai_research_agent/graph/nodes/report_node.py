from ai_research_agent.graph.state import (
    ResearchState,
)

from ai_research_agent.report.service import (
    ReportService,
)

from ai_research_agent.utils.logger import (
    logger,
)


report_service = ReportService()


async def report_node(
    state: ResearchState,
) -> ResearchState:
    """Generate the final Markdown report from the reasoning output."""

    logger.info("Generating final report...")

    report = await report_service.generate_report(
        query=state["query"],
        reasoning_output=state["reasoning_output"],
        output_format=state.get("request_options", {}).get(
            "output_format", "report"
        ),
    )

    state["report"] = report

    logger.success("Report generated successfully.")

    return state
