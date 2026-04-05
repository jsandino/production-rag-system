from typing import Protocol, List

from app.models.chunk_result import ChunkResult


class ChunkRepository(Protocol):
    def search(self, embedding: list[float], top_k: int) -> List[ChunkResult]:
        """Return the top_k most similar chunks for the given query embedding."""
