class TextChunker:
    """Split text into overlapping word chunks for vector storage."""

    def __init__(self, chunk_size: int = 500, overlap: int = 100) -> None:
        """Configure chunk length and overlap, both measured in words."""
        if chunk_size <= 0:
            raise ValueError("chunk_size must be positive")
        if overlap < 0 or overlap >= chunk_size:
            raise ValueError("overlap must be non-negative and smaller than chunk_size")
        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk(self, text: str) -> list[str]:
        """Return word chunks while preserving the configured overlap."""
        words = text.split()
        if not words:
            return []
        chunks = []
        start = 0
        while start < len(words):
            end = start + self.chunk_size
            chunks.append(" ".join(words[start:end]))
            start += self.chunk_size - self.overlap
        return chunks
