from typing import List, Protocol


class Embedder(Protocol):
    """
    Model-agnostic contract to produce embeddings from text chunks.
    """

    def embed(self, texts: List[str]) -> List[List[float]]: ...
