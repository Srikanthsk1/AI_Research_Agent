import os

from fastembed import SparseTextEmbedding
from qdrant_client import QdrantClient, models

from ai_research_agent.utils.logger import logger


class QdrantStore:
    """Persist and search evidence vectors in a local Qdrant collection."""

    COLLECTION_NAME = "research_memory_hybrid"
    VECTOR_SIZE = 384  # all-MiniLM-L6-v2
    DENSE_VECTOR_NAME = "dense"
    SPARSE_VECTOR_NAME = "sparse"
    SPARSE_MODEL_NAME = "Qdrant/bm25"

    def __init__(self) -> None:
        """Open the persistent client and create the memory collection."""
        self.collection_name = os.getenv(
            "QDRANT_COLLECTION",
            self.COLLECTION_NAME,
        )
        storage_path = os.getenv("QDRANT_PATH", "./qdrant_db")
        sparse_model_name = os.getenv(
            "QDRANT_SPARSE_MODEL",
            self.SPARSE_MODEL_NAME,
        )

        logger.info("Initializing Qdrant...")
        self.client = QdrantClient(path=storage_path)
        self.sparse_model = SparseTextEmbedding(model_name=sparse_model_name)
        self._ensure_collection()
        logger.success("Qdrant initialized.")

    def _ensure_collection(self) -> None:
        if not self.client.collection_exists(self.collection_name):
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config={
                    self.DENSE_VECTOR_NAME: models.VectorParams(
                        size=self.VECTOR_SIZE,
                        distance=models.Distance.COSINE,
                    )
                },
                sparse_vectors_config={
                    self.SPARSE_VECTOR_NAME: models.SparseVectorParams(
                        modifier=models.Modifier.IDF,
                    )
                },
            )
            return

        collection = self.client.get_collection(self.collection_name)
        vectors = collection.config.params.vectors
        sparse_vectors = collection.config.params.sparse_vectors or {}
        if (
            not isinstance(vectors, dict)
            or self.DENSE_VECTOR_NAME not in vectors
            or self.SPARSE_VECTOR_NAME not in sparse_vectors
        ):
            raise RuntimeError(
                f"Qdrant collection '{self.collection_name}' is not configured "
                "for hybrid retrieval. Set QDRANT_COLLECTION to a new collection "
                "name such as 'research_memory_hybrid'."
            )

    def _sparse_vector(self, text: str, *, is_query: bool) -> models.SparseVector:
        if is_query:
            embedding = next(self.sparse_model.query_embed(text))
        else:
            embedding = next(self.sparse_model.embed(text))

        return models.SparseVector(
            indices=embedding.indices.tolist(),
            values=embedding.values.tolist(),
        )

    def add_memory(self, memory, embedding: list[float]) -> None:
        """Insert or replace a memory record with dense and sparse vectors."""
        payload = {
            "content": memory.content,
            "query": memory.query,
            "source_url": memory.source_url,
            "source_type": memory.source_type,
            "credibility_score": memory.credibility_score,
            "created_at": str(memory.created_at),
            **(memory.metadata or {}),
        }

        self.client.upsert(
            collection_name=self.collection_name,
            points=[
                models.PointStruct(
                    id=memory.id,
                    vector={
                        self.DENSE_VECTOR_NAME: embedding,
                        self.SPARSE_VECTOR_NAME: self._sparse_vector(
                            memory.content,
                            is_query=False,
                        ),
                    },
                    payload=payload,
                )
            ],
        )

    def exists(self, memory_hash: str) -> bool:
        """Return whether a record with this content hash exists."""
        points, _ = self.client.scroll(
            collection_name=self.collection_name,
            scroll_filter=models.Filter(
                must=[
                    models.FieldCondition(
                        key="memory_hash",
                        match=models.MatchValue(value=memory_hash),
                    )
                ]
            ),
            limit=1,
            with_payload=False,
            with_vectors=False,
        )
        return bool(points)

    def search(
        self,
        embedding: list[float],
        query: str,
        top_k: int = 5,
    ) -> dict:
        """Fuse dense and sparse matches with reciprocal rank fusion."""
        candidate_limit = max(top_k * 4, 20)
        prefetch = [
            models.Prefetch(
                query=embedding,
                using=self.DENSE_VECTOR_NAME,
                limit=candidate_limit,
            )
        ]

        sparse_query = self._sparse_vector(
            query,
            is_query=True,
        )

        if sparse_query.indices:
            prefetch.append(
                models.Prefetch(
                    query=sparse_query,
                    using=self.SPARSE_VECTOR_NAME,
                    limit=candidate_limit,
                )
            )

        response = self.client.query_points(
            collection_name=self.collection_name,
            prefetch=prefetch,
            query=models.RrfQuery(rrf=models.Rrf()),
            limit=top_k,
            with_payload=True,
        )
        points = response.points

        # Preserve the result shape consumed by retrieval_service.
        return {
            "documents": [
                [(point.payload or {}).get("content", "") for point in points]
            ],
            "metadatas": [
                [
                    {
                        key: value
                        for key, value in (point.payload or {}).items()
                        if key != "content"
                    }
                    for point in points
                ]
            ],
            "scores": [[point.score for point in points]],
        }

    def count(self) -> int:
        """Return the number of records in the collection."""
        result = self.client.count(
            collection_name=self.collection_name,
            exact=True,
        )
        return result.count

    def clear(self) -> None:
        """Delete and recreate the memory collection."""
        self.client.delete_collection(self.collection_name)
        self._ensure_collection()
