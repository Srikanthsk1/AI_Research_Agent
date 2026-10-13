from ai_research_agent.graph.state import (
    ResearchState,
)

from ai_research_agent.memory.instance import (
    memory_service,
)

from ai_research_agent.utils.logger import (
    logger,
)


memory = memory_service


def memory_storage_node(
    state: ResearchState,
) -> ResearchState:
    """Persist newly extracted evidence for future research runs."""

    logger.info("Saving fresh evidences into memory...")

    stored = 0

    for evidence in state["fresh_evidences"]:

        try:

            memory.store_memory(
                query=state["query"],
                source_url=evidence.source_url,
                content=evidence.content,
            )

            stored += 1

        except Exception as e:

            logger.warning(f"Failed storing memory: {e}")

    logger.success(f"{stored} evidences stored.")

    return state
