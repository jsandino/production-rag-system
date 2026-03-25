from typing import List, Protocol


class EmbeddingService(Protocol):
    def embed(self, texts: List[str]) -> List[List[float]]: ...
