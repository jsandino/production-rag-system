from typing import Protocol


class Generator(Protocol):
    """
    Model-agnostic contract to generate an answer from a query and context.
    """

    def generate(self, query: str, context: str) -> str: ...
