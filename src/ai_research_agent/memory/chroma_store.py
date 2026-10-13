"""Backward-compatible imports for the former Chroma store module."""

from ai_research_agent.memory.qdrant_store import QdrantStore


ChromaStore = QdrantStore

__all__ = ["ChromaStore", "QdrantStore"]
