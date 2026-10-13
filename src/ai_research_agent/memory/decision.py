from ai_research_agent.utils.logger import logger


class MemoryDecision:
    """Decide whether retrieved memory is relevant enough to reuse."""

    def __init__(
        self,
        similarity_threshold: float = 0.80,
    ):
        """Set the minimum similarity required to reuse memory."""
        self.similarity_threshold = similarity_threshold

    def should_research(
        self,
        memory_results,
    ) -> bool:
        """Return whether fresh research should be performed."""

        if not memory_results:

            logger.info("No memory found.")

            return True

        distances = memory_results.get(
            "distances",
            [],
        )

        if not distances:

            logger.info("No similarity scores found.")

            return True

        if not distances[0]:

            logger.info("Empty similarity results.")

            return True

        distance = distances[0][0]

        similarity = 1 - distance

        logger.info(f"Memory similarity: {similarity:.3f}")

        if similarity >= self.similarity_threshold:

            logger.success("Relevant memory found.")

            return False

        logger.info("Memory not sufficient.")

        return True
