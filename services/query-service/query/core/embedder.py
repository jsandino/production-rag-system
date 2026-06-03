from typing import Protocol


class Embedder(Protocol):
    """
    Model-agnostic contract to produce an embedding from a query string.
    """

    def embed(self, text: str) -> list[float]: ...
