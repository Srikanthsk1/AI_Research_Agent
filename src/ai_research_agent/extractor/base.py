from abc import ABC, abstractmethod


class BaseExtractor(ABC):
    """Interface for asynchronous webpage text extractors."""

    @abstractmethod
    async def extract(
        self,
        url: str,
    ) -> str:
        """Fetch a URL and return its readable text content."""
        ...
