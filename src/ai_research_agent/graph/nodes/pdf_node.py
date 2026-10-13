import asyncio
import os

from ai_research_agent.graph.state import (
    ResearchState,
)

from ai_research_agent.report.pdf_service import (
    PDFService,
)

from ai_research_agent.utils.logger import (
    logger,
)


pdf_service = PDFService()


async def pdf_node(
    state: ResearchState,
) -> ResearchState:
    """Render the generated Markdown report to the configured PDF path."""

    if state.get("request_options", {}).get("output_format") == "json":
        state["pdf_path"] = ""
        return state

    logger.info("Generating PDF report...")

    os.makedirs(
        "reports",
        exist_ok=True,
    )

    pdf_path = os.path.join("reports", f"{state['run_id']}.pdf")

    await asyncio.to_thread(
        pdf_service.generate_pdf,
        markdown_text=state["report"],
        output_path=pdf_path,
    )

    state["pdf_path"] = pdf_path

    logger.success(f"PDF saved to {pdf_path}")

    return state
