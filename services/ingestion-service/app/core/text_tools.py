from typing import Protocol

from app.core.tokenizer import Tokenizer
from app.core.chunker import Chunker
from app.core.embedder import Embedder


class TextTools(Protocol):
    """
    Cohesive set of text tool collaborators used during ingestion.

    Guarantees that tokenizer, chunker, and embedder are aligned.
    """

    @property
    def tokenizer(self) -> Tokenizer: ...

    @property
    def chunker(self) -> Chunker: ...

    @property
    def embedder(self) -> Embedder: ...
