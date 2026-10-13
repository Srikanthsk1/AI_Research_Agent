import uuid

from ai_research_agent.utils.chunker import TextChunker
from ai_research_agent.utils.hash_utils import generate_hash

from ai_research_agent.memory.models import MemoryRecord

from ai_research_agent.memory.embeddings import EmbeddingService
from ai_research_agent.memory.qdrant_store import QdrantStore
from ai_research_agent.memory.retriever import MemoryRetriever

from ai_research_agent.utils.logger import logger


class MemoryService:
    """Store, deduplicate, and retrieve research memory chunks."""

    def __init__(self):
        """Initialize chunking, embeddings, storage, and retrieval."""
        self.chunker = TextChunker()

        self.embedding_service = EmbeddingService()

        self.store = QdrantStore()

        self.retriever = MemoryRetriever(
            self.embedding_service,
            self.store,
        )

    def store_memory(
        self,
        query,
        source_url,
        content,
        source_type="web",
        credibility_score=50,
        metadata=None,
    ):
        """Chunk content and persist only hashes not already stored."""
        chunks = self.chunker.chunk(content)

        stored = 0
        skipped = 0

        for index, chunk in enumerate(
            chunks,
            start=1,
        ):

            memory_hash = generate_hash(chunk)

            if self.store.exists(memory_hash):

                skipped += 1

                continue

            memory = MemoryRecord(
                id=str(uuid.uuid4()),
                query=query,
                source_url=source_url,
                content=chunk,
                source_type=source_type,
                credibility_score=credibility_score,
                metadata={
                    **(metadata or {}),
                    "memory_hash": memory_hash,
                    "chunk_number": index,
                    "total_chunks": len(chunks),
                },
            )

            embedding = self.embedding_service.embed_text(chunk)

            self.store.add_memory(
                memory,
                embedding,
            )

            stored += 1

        logger.info(f"Stored: {stored} chunks")

        logger.info(f"Skipped: {skipped} duplicates")

    def retrieve(
        self,
        query,
        top_k=5,
    ):
        """Return nearest memory records for a query."""
        return self.retriever.retrieve(
            query,
            top_k,
        )

    def count(self):
        """Return the total number of stored memory chunks."""
        return self.store.count()
