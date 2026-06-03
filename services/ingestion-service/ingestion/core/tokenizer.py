from typing import Protocol


class Tokenizer(Protocol):
    """
    Model-agnostic contract for tokenizing text
    """

    def encode(self, text: str) -> list[int]: ...

    def decode(self, tokens: list[int]) -> str: ...
