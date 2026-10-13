from sentence_transformers import SentenceTransformer

from ai_research_agent.utils.logger import logger


class EmbeddingService:
    """Generate normalized Sentence Transformers embeddings."""

    def __init__(self):
        """Load the local sentence embedding model."""
        logger.info("Loading embedding model...")

        self.model = SentenceTransformer("all-MiniLM-L6-v2")

        logger.success("Embedding model loaded.")

    def embed_text(
        self,
        text: str,
    ) -> list[float]:
        """Return a normalized embedding for one text string."""

        embedding = self.model.encode(
            text,
            normalize_embeddings=True,
        )

        return embedding.tolist()

    def embed_documents(
        self,
        documents: list[str],
    ) -> list[list[float]]:
        """Return normalized embeddings for a batch of documents."""

        embeddings = self.model.encode(
            documents,
            normalize_embeddings=True,
        )

        return embeddings.tolist()
