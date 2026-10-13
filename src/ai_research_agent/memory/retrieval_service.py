from ai_research_agent.memory.instance import (
    memory_service,
)

from ai_research_agent.research.evidence import (
    Evidence,
)

from ai_research_agent.utils.logger import (
    logger,
)


class MemoryRetrievalService:
    """Convert relevant vector-search results into evidence records."""

    def __init__(self):
        """Use the shared memory service instance."""
        self.memory = memory_service

    def retrieve(
        self,
        query: str,
        top_k: int = 5,
    ) -> list[Evidence]:
        """Return unique memories from the fused dense and sparse rankings."""
        logger.info("Retrieving related memories...")

        evidences = []

        try:

            results = self.memory.retrieve(
                query=query,
                top_k=top_k,
            )

            documents = results.get("documents", [])

            metadatas = results.get("metadatas", [])

            if documents and len(documents) > 0 and len(documents[0]) > 0:

                logger.info(f"Found {len(documents[0])} related memories")

                selected = set()
                for document, metadata in zip(
                    documents[0],
                    metadatas[0],
                ):
                    content_key = " ".join(document.split()).casefold()
                    if content_key in selected:
                        continue
                    selected.add(content_key)

                    evidences.append(
                        Evidence(
                            source_url=metadata.get(
                                "source_url",
                                "memory",
                            ),
                            content=document,
                        )
                    )

            else:

                logger.info("No related memories found.")

        except Exception as e:

            logger.warning(f"Memory retrieval failed: {e}")

        return evidences
