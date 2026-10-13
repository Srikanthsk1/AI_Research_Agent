from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class MemoryRecord(BaseModel):
    """A chunk of research evidence persisted in vector memory."""

    id: str

    query: str

    source_url: str

    content: str

    source_type: str = "web"

    credibility_score: int = Field(
        default=50,
        ge=0,
        le=100,
    )

    created_at: datetime = Field(
        default_factory=datetime.utcnow,
    )

    metadata: Optional[dict] = Field(
        default_factory=dict,
    )
