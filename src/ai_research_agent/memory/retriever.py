from ai_research_agent.memory.embeddings import EmbeddingService

from ai_research_agent.utils.logger import logger


class MemoryRetriever:
    """Coordinate query embedding and vector-store search."""

    def __init__(
        self,
        embedding_service,
        store,
    ):
        """Store the embedding provider and vector-store adapter."""
        self.embedding_service = embedding_service

        self.store = store

    def retrieve(
        self,
        query,
        top_k=5,
    ):
        """Return the nearest stored memories for a query."""
        logger.info("Searching memory...")

        embedding = self.embedding_service.embed_text(query)

        results = self.store.search(
            embedding,
            query=query,
            top_k=top_k,
        )

        logger.success("Memory retrieval completed.")

        return results
